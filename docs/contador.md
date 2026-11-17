# Contador de visitas propio — ACTIVADO (v13, 17-11-2026)

Código 100 % nuestro, sin servicios de analítica de terceros.

- Página: `counter.js` envía, al entrar en la página, solo la sección (`/`, `/2d/` o `/proyecto/`)
  a `https://kl-contador.roquena71.workers.dev/hit`. Sin cookies, sin almacenamiento en el navegador,
  sin credenciales. No se cuenta el paso de una sección a otra dentro de la página. Si el navegador
  pide «no rastrear» (DNT o GPC), o es un navegador automático, no se envía nada.
- Servidor: `contador/src/index.js` (Cloudflare Worker `kl-contador` en la cuenta de Carlos), base
  de datos D1 `kl-contador` con jurisdicción UE. Tabla `visits(day, section, hits)`: solo día (hora
  de Berlín), sección y número. No lee ni guarda IP, navegador, país ni procedencia. Registros
  (observability/logs) apagados. Solo acepta peticiones con `Origin: https://roquena71-a11y.github.io`;
  también ignora DNT/GPC, robots conocidos y precargas. Tope: 20.000 por sección y día.
- Cuenta visitas, no personas únicas.
- Números (públicos, sin datos personales): https://kl-contador.roquena71.workers.dev/ y
  https://kl-contador.roquena71.workers.dev/stats.json

## Límites del plan gratuito (documentación oficial, consultada el 17-11-2026)
- Workers Free: 100.000 peticiones/día, 10 ms CPU — https://developers.cloudflare.com/workers/platform/limits/
- D1 Free: 100.000 filas escritas/día, 5 millones leídas/día, 5 GB — https://developers.cloudflare.com/d1/platform/pricing/
- Si se supera, ese día deja de contar; la página sigue igual.

## Pruebas
`cd contador && npm install && npm test` (SQLite en memoria, sin red) y `tests/counter-sw-test.cjs`.

## Apagarlo
En `counter.js` poner `enabled: false` y publicar; la nota de privacidad vuelve sola a «sin contador».
