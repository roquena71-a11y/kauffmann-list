"""Cliente HTTP mínimo (stdlib) con caché en disco, reintentos y límite de velocidad.

- User-Agent genérico (no se envía ningún dato personal).
- Caché: pipeline/cache/<namespace>/<sha256>.body (+ .meta.json). Ignorada por git.
- Modo offline: solo caché; si falta, lanza OfflineCacheMiss.
"""
import hashlib
import json
import os
import time
import urllib.error
import urllib.parse
import urllib.request

from .util import PIPELINE_DIR

USER_AGENT = "KauffmannList-pipeline/1.0"
CACHE_DIR = os.path.join(PIPELINE_DIR, "cache")


class OfflineCacheMiss(Exception):
    pass


class HttpError(Exception):
    pass


class HttpClient:
    def __init__(self, namespace, offline=False, min_interval=1.0, retries=4, timeout=120,
                 cache_dir=None, sleep=time.sleep, opener=None):
        self.namespace = namespace
        self.offline = offline
        self.min_interval = float(min_interval)
        self.retries = int(retries)
        self.timeout = timeout
        self.cache_dir = os.path.join(cache_dir or CACHE_DIR, namespace)
        self._last = 0.0
        self._sleep = sleep
        self._opener = opener or urllib.request.urlopen
        self.stats = {"requests": 0, "cache_hits": 0, "retries": 0}

    def _key(self, method, url, body):
        h = hashlib.sha256()
        h.update(method.encode())
        h.update(b"\0")
        h.update(url.encode())
        h.update(b"\0")
        h.update(body or b"")
        return h.hexdigest()

    def _throttle(self):
        wait = self._last + self.min_interval - time.monotonic()
        if wait > 0:
            self._sleep(wait)
        self._last = time.monotonic()

    def request(self, url, params=None, data=None, headers=None, method=None):
        if params:
            url = url + ("&" if "?" in url else "?") + urllib.parse.urlencode(params)
        body = None
        if data is not None:
            body = data if isinstance(data, bytes) else urllib.parse.urlencode(data).encode()
        method = method or ("POST" if body is not None else "GET")
        key = self._key(method, url, body)
        path = os.path.join(self.cache_dir, key[:2], key + ".body")
        if os.path.exists(path):
            self.stats["cache_hits"] += 1
            with open(path, "rb") as f:
                return f.read()
        if self.offline:
            raise OfflineCacheMiss("%s %s (sin caché, modo --offline)" % (method, url[:160]))
        hdrs = {"User-Agent": USER_AGENT, "Accept-Encoding": "identity"}
        hdrs.update(headers or {})
        last_err = None
        for attempt in range(self.retries + 1):
            self._throttle()
            req = urllib.request.Request(url, data=body, headers=hdrs, method=method)
            try:
                self.stats["requests"] += 1
                with self._opener(req, timeout=self.timeout) as resp:
                    content = resp.read()
                os.makedirs(os.path.dirname(path), exist_ok=True)
                tmp = path + ".tmp"
                with open(tmp, "wb") as f:
                    f.write(content)
                os.replace(tmp, path)
                with open(path[:-5] + ".meta.json", "w", encoding="utf-8") as f:
                    json.dump({"url": url, "method": method, "fetched": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}, f)
                return content
            except urllib.error.HTTPError as e:
                last_err = e
                if e.code not in (429, 500, 502, 503, 504):
                    raise HttpError("HTTP %s en %s" % (e.code, url[:160]))
                retry_after = e.headers.get("Retry-After") if e.headers else None
                delay = float(retry_after) if retry_after and retry_after.isdigit() else 2 ** (attempt + 1)
            except (urllib.error.URLError, TimeoutError, ConnectionError, OSError) as e:
                last_err = e
                delay = 2 ** (attempt + 1)
            if attempt < self.retries:
                self.stats["retries"] += 1
                self._sleep(min(delay, 60))
        raise HttpError("Fallo tras %d intentos: %s (%s)" % (self.retries + 1, url[:160], last_err))

    def get_json(self, url, params=None, headers=None):
        return json.loads(self.request(url, params=params, headers=headers).decode("utf-8"))

    def post_json(self, url, data, headers=None):
        return json.loads(self.request(url, data=data, headers=headers).decode("utf-8"))
