// Pruebas del Worker con una base SQLite en memoria que imita D1 (node:sqlite). No usa red ni cuentas.
import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { DatabaseSync } from 'node:sqlite';
import worker, { berlinDay, sectionToCount } from '../src/index.js';

const ORIGIN = 'https://roquena71-a11y.github.io';
function fakeD1() {
  const db = new DatabaseSync(':memory:');
  db.exec(readFileSync(new URL('../schema.sql', import.meta.url), 'utf8'));
  const prep = (sql) => ({ _sql: sql, _args: [], bind(...a) { this._args = a; return this; },
    async run() { db.prepare(sql.replace(/\?(\d)/g, '?')).run(...this._args); return { success: true }; },
    async all() { return { results: db.prepare(sql).all(...this._args) }; },
    async first() { return db.prepare(sql).get(...this._args); } });
  return { prepare: prep, raw: db };
}
const env = (o) => ({ ALLOWED_ORIGIN: ORIGIN, MAX_PER_DAY: '20000', STATS_PUBLIC: 'true', DB: fakeD1(), ...o });
const hit = (e, body, headers) => worker.fetch(new Request('https://kl-contador.x.workers.dev/hit', {
  method: 'POST', body, headers: { Origin: ORIGIN, 'User-Agent': 'Mozilla/5.0 Firefox/140', 'Content-Type': 'text/plain', ...headers } }), e);
const rows = (e) => e.DB.raw.prepare('SELECT * FROM visits ORDER BY section').all().map(r => ({ ...r }));

test('cuenta una visita y guarda solo día, sección y número', async () => {
  const e = env();
  const r = await hit(e, '/');
  assert.equal(r.status, 204);
  assert.equal(r.headers.get('set-cookie'), null);
  const all = rows(e);
  assert.equal(all.length, 1);
  assert.deepEqual(Object.keys(all[0]).sort(), ['day', 'hits', 'section']);
  assert.equal(all[0].hits, 1);
  assert.equal(all[0].day, berlinDay(new Date()));
});

test('suma por sección', async () => {
  const e = env();
  for (const s of ['/', '/', '/2d/', '/proyecto/']) await hit(e, s);
  assert.deepEqual(rows(e).map(r => [r.section, r.hits]), [['/', 2], ['/2d/', 1], ['/proyecto/', 1]]);
});

test('no cuenta: otro origen, sin origen, DNT, GPC, robots, precarga, sección inventada, GET', async () => {
  const e = env();
  await hit(e, '/', { Origin: 'https://evil.example' });
  await hit(e, '/', { Origin: '' });
  await hit(e, '/', { DNT: '1' });
  await hit(e, '/', { 'Sec-GPC': '1' });
  await hit(e, '/', { 'User-Agent': 'Googlebot/2.1' });
  await hit(e, '/', { 'Sec-Purpose': 'prefetch' });
  await hit(e, '/?q=Löpert');
  await hit(e, 'x'.repeat(500));
  const g = await worker.fetch(new Request('https://k/hit'), e);
  assert.equal(g.status, 405);
  assert.equal(rows(e).length, 0);
});

test('la respuesta es igual cuente o no (no revela nada)', async () => {
  const e = env();
  const a = await hit(e, '/'), b = await hit(e, '/', { DNT: '1' });
  assert.equal(a.status, b.status);
  assert.deepEqual([...a.headers].sort(), [...b.headers].sort());
});

test('tope diario protege la cuota gratuita', async () => {
  const e = env({ MAX_PER_DAY: '3' });
  for (let i = 0; i < 6; i++) await hit(e, '/');
  assert.equal(rows(e)[0].hits, 3);
});

test('estadísticas: texto y JSON, sin datos personales', async () => {
  const e = env();
  e.DB.raw.exec("INSERT INTO visits VALUES ('2026-01-01','/',5),('2026-01-01','/2d/',2)");
  await hit(e, '/'); await hit(e, '/2d/');
  const t = await (await worker.fetch(new Request('https://k/'), e)).text();
  assert.match(t, /Hoy: 2/);
  assert.match(t, /Total desde 2026-01-01: 9/);
  const j = await (await worker.fetch(new Request('https://k/stats.json'), e)).json();
  assert.equal(j.total, 9); assert.equal(j.today, 2); assert.equal(j.since, '2026-01-01');
  assert.deepEqual(Object.keys(j.days[0]).sort(), ['day', 'visits']);
});

test('estadísticas privadas si STATS_PUBLIC no es "true"', async () => {
  const r = await worker.fetch(new Request('https://k/stats.json'), env({ STATS_PUBLIC: 'false' }));
  assert.equal(r.status, 404);
});

test('día en hora de Berlín (cambio de día y horario de verano)', () => {
  assert.equal(berlinDay(new Date('2026-11-17T22:59:00Z')), '2026-11-17');
  assert.equal(berlinDay(new Date('2026-11-17T23:00:00Z')), '2026-11-18');
  assert.equal(berlinDay(new Date('2026-07-01T21:59:00Z')), '2026-07-01');
  assert.equal(berlinDay(new Date('2026-07-01T22:00:00Z')), '2026-07-02');
});

test('el código no lee la IP ni el país, ni escribe registros', () => {
  const src = readFileSync(new URL('../src/index.js', import.meta.url), 'utf8');
  assert.doesNotMatch(src, /CF-Connecting-IP|X-Forwarded-For|X-Real-IP|request\.cf|console\.|Set-Cookie/i);
  const schema = readFileSync(new URL('../schema.sql', import.meta.url), 'utf8').replace(/--.*$/gm, '');
  assert.doesNotMatch(schema, /ip|agent|country|referr|ua\b/i);
  const cfg = readFileSync(new URL('../wrangler.jsonc', import.meta.url), 'utf8');
  assert.match(cfg, /"observability": \{ "enabled": false/);
});

test('sectionToCount es estricta', () => {
  const req = (h) => new Request('https://k/hit', { method: 'POST', headers: { Origin: ORIGIN, ...h } });
  assert.equal(sectionToCount(req({}), '/2d/', { ALLOWED_ORIGIN: ORIGIN }), '/2d/');
  assert.equal(sectionToCount(req({}), '/admin', { ALLOWED_ORIGIN: ORIGIN }), '');
});
