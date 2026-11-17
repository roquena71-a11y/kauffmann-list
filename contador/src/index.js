/* Lista Kauffmann — contador de visitas propio (Cloudflare Worker + D1).
   Código 100 % nuestro. Guarda SOLO: día (hora de Berlín), sección y un número.
   No lee ni guarda IP, navegador, país, procedencia ni nada que identifique a una persona.
   No pone cookies. Si el navegador pide «no rastrear» (DNT o GPC), no cuenta.

   POST /hit        cuerpo: '/', '/2d/' o '/proyecto/'  → suma 1 (responde 204 vacío)
   GET  /           texto sencillo con los totales (si STATS_PUBLIC = "true")
   GET  /stats.json los mismos totales en JSON (para quien quiera verificarlos)          */

export const SECTIONS = ['/', '/2d/', '/proyecto/'];
const BOT_RE = /bot|crawl|spider|slurp|preview|headless|lighthouse|curl|wget|python|httpclient|monitor/i;

const BASE_HEADERS = {
  'Cache-Control': 'no-store',
  'X-Content-Type-Options': 'nosniff',
  'Referrer-Policy': 'no-referrer',
  'Content-Security-Policy': "default-src 'none'; frame-ancestors 'none'",
  'Cross-Origin-Resource-Policy': 'cross-origin',
};

function reply(status, body, extra) {
  return new Response(body == null ? null : body, { status, headers: { ...BASE_HEADERS, ...(extra || {}) } });
}

// Día en hora de Berlín, p. ej. '2026-11-17'.
export function berlinDay(date) {
  return new Intl.DateTimeFormat('en-CA', { timeZone: 'Europe/Berlin', year: 'numeric', month: '2-digit', day: '2-digit' }).format(date);
}

// Decide si una petición se cuenta. Pura: no guarda nada. Devuelve la sección o ''.
export function sectionToCount(request, body, env) {
  const h = request.headers;
  if (request.method !== 'POST') return '';
  if (h.get('Origin') !== env.ALLOWED_ORIGIN) return '';               // solo desde la propia página
  if (h.get('DNT') === '1' || h.get('Sec-GPC') === '1') return '';      // «no rastrear»
  if (BOT_RE.test(h.get('User-Agent') || '')) return '';                // robots conocidos (no se guarda)
  if (h.get('Purpose') === 'prefetch' || h.get('Sec-Purpose')) return ''; // precargas
  const s = String(body || '').trim();
  return SECTIONS.includes(s) ? s : '';
}

async function countHit(env, section, now) {
  const cap = Math.max(1, parseInt(env.MAX_PER_DAY, 10) || 20000);
  // Una sola escritura atómica; deja de sumar al llegar al tope diario (protege la cuota gratuita).
  await env.DB.prepare(
    'INSERT INTO visits (day, section, hits) VALUES (?1, ?2, 1) ' +
    'ON CONFLICT (day, section) DO UPDATE SET hits = hits + 1 WHERE hits < ?3'
  ).bind(berlinDay(now), section, cap).run();
}

export async function readStats(env, now) {
  const today = berlinDay(now);
  const { results } = await env.DB.prepare(
    'SELECT day, SUM(hits) AS visits FROM visits GROUP BY day ORDER BY day DESC LIMIT 400'
  ).all();
  const days = (results || []).map(r => ({ day: r.day, visits: Number(r.visits) }));
  const sum = n => days.filter(d => d.day > shiftDay(today, -n)).reduce((a, d) => a + d.visits, 0);
  const totalRow = await env.DB.prepare('SELECT COALESCE(SUM(hits), 0) AS t, MIN(day) AS since FROM visits').first();
  return {
    since: totalRow && totalRow.since || null,
    total: Number(totalRow && totalRow.t || 0),
    today: (days.find(d => d.day === today) || { visits: 0 }).visits,
    last7: sum(7),
    last30: sum(30),
    days,
    note: 'Visitas (cargas de la página desde fuera), no personas únicas. Sin cookies ni IP.',
  };
}

function shiftDay(day, n) {
  const d = new Date(day + 'T12:00:00Z');
  d.setUTCDate(d.getUTCDate() + n);
  return d.toISOString().slice(0, 10);
}

const fmt = n => new Intl.NumberFormat('es-ES').format(n);

export default {
  async fetch(request, env) {
    const url = new URL(request.url);
    const now = new Date();

    if (url.pathname === '/hit') {
      if (request.method === 'OPTIONS') return reply(204);
      if (request.method !== 'POST') return reply(405, null, { Allow: 'POST' });
      const len = parseInt(request.headers.get('Content-Length') || '0', 10);
      if (len > 32) return reply(204);
      const body = (await request.text()).slice(0, 32);
      const section = sectionToCount(request, body, env);
      if (section) {
        try { await countHit(env, section, now); } catch (e) { /* sin registros: si falla, no se cuenta */ }
      }
      return reply(204); // siempre la misma respuesta: no revela si contó o no
    }

    if (request.method === 'GET' && (url.pathname === '/' || url.pathname === '/stats.json')) {
      if (env.STATS_PUBLIC !== 'true') return reply(404, 'No encontrado', { 'Content-Type': 'text/plain; charset=utf-8' });
      const s = await readStats(env, now);
      const cache = { 'Cache-Control': 'public, max-age=300' };
      if (url.pathname === '/stats.json') {
        return reply(200, JSON.stringify(s, null, 1), { ...cache, 'Content-Type': 'application/json; charset=utf-8', 'Access-Control-Allow-Origin': '*' });
      }
      const text = [
        'Lista Kauffmann — visitas',
        '',
        'Hoy: ' + fmt(s.today),
        'Últimos 7 días: ' + fmt(s.last7),
        'Últimos 30 días: ' + fmt(s.last30),
        'Total desde ' + (s.since || '—') + ': ' + fmt(s.total),
        '',
        'Cuenta visitas (cargas de la página desde fuera), no personas únicas.',
        'Sin cookies, sin IP, sin procedencia. Si el navegador pide «no rastrear», no se cuenta.',
      ].join('\n');
      return reply(200, text, { ...cache, 'Content-Type': 'text/plain; charset=utf-8' });
    }

    return reply(404, null);
  },
};
