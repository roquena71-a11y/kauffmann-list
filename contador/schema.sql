-- Lista Kauffmann — contador propio. Solo totales por día y sección.
-- No hay columnas para IP, navegador, país, procedencia, hora exacta ni identificadores.
CREATE TABLE IF NOT EXISTS visits (
  day     TEXT    NOT NULL,             -- 'AAAA-MM-DD' (hora de Berlín)
  section TEXT    NOT NULL,             -- '/', '/2d/' o '/proyecto/'
  hits    INTEGER NOT NULL DEFAULT 0,   -- número de visitas ese día en esa sección
  PRIMARY KEY (day, section)
) WITHOUT ROWID;
