"""v37 (auditoría M5): imagen para compartir (og:image/twitter:image) 1200×630, a partir de una captura propia ya publicada
(proyecto/media/uebersicht.png: vista general del mapa 3D). Recorta solo el mapa (sin la barra lateral con cifras viejas
ni los controles), añade título y el crédito del mapa base. Sin cifras dentro de la imagen (no envejecen).
Uso: python3 tests/make-og-image.py  → media/og-kauffmann.jpg"""
import os
from PIL import Image, ImageDraw, ImageFont
ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
SERIF = os.path.join(ROOT, "fonts/j8_w6_fAw7jrcalD7oKYNX0QfAnPW7Dl4Q.woff2")      # Frank Ruhl Libre (latin), OFL
SANS = os.path.join(ROOT, "fonts/NGS6v5_NC0k9P9H2TbE.woff2")                     # Heebo (latin), OFL
src = Image.open(os.path.join(ROOT, "proyecto/media/uebersicht.png")).convert("RGB")   # 1440×900
W, H = 1200, 630
box = (400, 196, 1395, 196 + round(995 * H / W))                                    # solo el lienzo del mapa
img = src.crop(box).resize((W, H), Image.LANCZOS)
# degradado oscuro a la izquierda para el título (contraste del texto ≥ 7:1 sobre #07111f)
ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
d = ImageDraw.Draw(ov)
for x in range(W):
    a = max(0, min(235, int(235 * (1 - (x - 380) / 340)))) if x > 380 else 235
    d.line([(x, 0), (x, H)], fill=(7, 17, 31, a))
d.rectangle([0, H - 44, W, H], fill=(7, 17, 31, 215))
img = Image.alpha_composite(img.convert("RGBA"), ov)
d = ImageDraw.Draw(img)
# placa dorada (degradado diagonal, como .plate del sitio)
for y in range(64):
    for x in range(64):
        t = (x + y) / 126
        stops = ((0, (240, 212, 138)), (0.55, (198, 161, 91)), (1, (122, 91, 40)))
        (t0, c0), (t1, c1) = (stops[0], stops[1]) if t <= 0.55 else (stops[1], stops[2])
        k = (t - t0) / (t1 - t0)
        d.point((64 + x, 92 + y), fill=tuple(int(a + (b - a) * k) for a, b in zip(c0, c1)))
d.rectangle([64, 92, 127, 155], outline=(60, 45, 20), width=1)
f1 = ImageFont.truetype(SERIF, 76)
f2 = ImageFont.truetype(SANS, 30)
f3 = ImageFont.truetype(SANS, 26)
fc = ImageFont.truetype(SANS, 17)
d.text((64, 180), "Lista Kauffmann", font=f1, fill=(246, 243, 236))
d.text((66, 278), "Mapa libre de los Stolpersteine", font=f2, fill=(240, 212, 138))
d.text((66, 318), "Kauffmann-Liste · Kauffmann List", font=f3, fill=(230, 224, 212))
d.text((66, 398), "Cada placa, cada nombre, cada historia.", font=f3, fill=(246, 243, 236))
d.text((66, 434), "Nunca olvidar.", font=f3, fill=(246, 243, 236))
d.text((20, H - 33), "Captura de la Lista Kauffmann · Mapa base © OpenFreeMap © OpenMapTiles · Datos © colaboradores de OpenStreetMap (ODbL), Wikidata (CC0)",
       font=fc, fill=(230, 224, 212))
os.makedirs(os.path.join(ROOT, "media"), exist_ok=True)
out = os.path.join(ROOT, "media/og-kauffmann.jpg")
img.convert("RGB").save(out, "JPEG", quality=82, optimize=True, progressive=True)
print(out, os.path.getsize(out), "bytes")
