import os
import time
import cv2
import numpy as np
import pandas as pd
from scipy.spatial import cKDTree

print("=" * 65)
print(" EXTRACCIÓN Y LIMPIEZA DE DATOS AEROMAGNÉTICOS - CARTA SAN FELIPE")
print("=" * 65)

t_start = time.time()

# -----------------------------------------------------------------------------
# 1. RUTA DE LA IMAGEN Y CONFIGURACIÓN
# -----------------------------------------------------------------------------
script_dir = os.path.dirname(os.path.abspath(__file__))

# Soporta ambos nombres de archivo habituales
img_candidates = [
    os.path.join(script_dir, 'CartaMagneticaSanFelipe_pages-to-jpg-0001.jpg'),
    os.path.join(script_dir, 'CartaMagneticaSanFelipe.jpg')
]

img_path = None
for cand in img_candidates:
    if os.path.exists(cand):
        img_path = cand
        break

if img_path is None:
    raise FileNotFoundError(f"No se encontró la imagen de San Felipe en: {script_dir}")

print(f"\n[1/5] Cargando imagen: {os.path.basename(img_path)}...")
img = cv2.imread(img_path)
if img is None:
    raise ValueError(f"No se pudo decodificar la imagen: {img_path}")

rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
h, w, _ = rgb.shape
print(f"      Dimensiones de la imagen: {w} x {h} píxeles ({w * h:,} píxeles)")

# -----------------------------------------------------------------------------
# 2. DEFINICIÓN DE LÍMITES GEOGRÁFICOS Y DE RECUADRO (NEATLINE)
# -----------------------------------------------------------------------------
# Límites del marco interno del mapa (omite ejes exteriores, coordenadas y márgenes)
ymin, ymax = 185, 5440
xmin, xmax = 120, 9080

# Coordenadas geográficas oficiales de la Carta San Felipe (SGM 1:250,000)
# Latitud:  31° 00' N (sur) a 32° 00' N (norte)
# Longitud: 116° 00' W (oeste) a 114° 00' W (este)
lat_top, lat_bottom = 32.0, 31.0
lon_left, lon_right = -116.0, -114.0

# -----------------------------------------------------------------------------
# 3. ESCALA OFICIAL SGM (SAN FELIPE)
# Intervalos de 50 nT: de < -600 nT a > 100 nT
# -----------------------------------------------------------------------------
color_scale_sf = {
    -600: [3, 179, 229],   # #03B3E5 (< -600 nT)
    -550: [88, 196, 234],  # #58C4EA (-600 a -550)
    -500: [129, 206, 234], # #81CEEA (-550 a -500)
    -450: [165, 215, 224], # #A5D7E0 (-500 a -450)
    -400: [203, 230, 221], # #CBE6DD (-450 a -400)
    -350: [224, 238, 223], # #E0EEDF (-400 a -350)
    -300: [226, 242, 231], # #E2F2E7 (-350 a -300)
    -250: [240, 247, 231], # #F0F7E7 (-300 a -250)
    -200: [255, 252, 223], # #FFFCDF (-250 a -200)
    -150: [255, 250, 210], # #FFFAD2 (-200 a -150)
    -100: [255, 237, 187], # #FFEDBB (-150 a -100)
    -50:  [255, 228, 183], # #FFE4B7 (-100 a -50)
    0:    [253, 208, 175], # #FDD0AF (-50 a 0)
    50:   [248, 172, 123], # #F8AC7B (0 a 50)
    100:  [248, 154, 92],  # #F89A5C (50 a 100)
    150:  [245, 131, 69]   # #F58345 (> 100 nT)
}

nt_values = np.array(list(color_scale_sf.keys()))
ref_colors = np.array(list(color_scale_sf.values()))
tree = cKDTree(ref_colors)

# -----------------------------------------------------------------------------
# 4. MÁSCARAS DE FILTRADO (TEXTOS, CURVAS NEGRAS, BLANCOS Y MAR/GOLFO)
# -----------------------------------------------------------------------------
print("\n[2/5] Generando filtros de ruido (textos, curvas, márgenes y mar)...")

# A) Detección de texto, curvas de nivel y elementos oscuros (< 95 en escala de grises)
gray = cv2.cvtColor(rgb, cv2.COLOR_RGB2GRAY)
dark_mask = gray < 95

# Dilatación morfológica: elimina el borde difuso (anti-aliasing) de letras y curvas
kernel_dark = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
dark_mask_dilated = cv2.dilate(dark_mask.astype(np.uint8), kernel_dark, iterations=1) > 0

# B) Detección de blancos y artefactos de compresión JPEG
hsv = cv2.cvtColor(rgb, cv2.COLOR_RGB2HSV)
ptp = np.ptp(rgb, axis=2)  # max(RGB) - min(RGB)
is_white = ((rgb[:, :, 0] > 238) & (rgb[:, :, 1] > 238) & (rgb[:, :, 2] > 238)) | \
           ((hsv[:, :, 1] < 12) & (hsv[:, :, 2] > 225) & (ptp < 14))

# C) Detección del Golfo de California (mar sin datos aeromagnéticos, azul uniforme)
is_sea = (rgb[:, :, 2] > 235) & (rgb[:, :, 2].astype(int) - rgb[:, :, 0].astype(int) > 20)

# -----------------------------------------------------------------------------
# 5. MUESTREO Y EMPAREJAMIENTO VECTORIZADO
# -----------------------------------------------------------------------------
# STEP: Espaciado de muestreo en píxeles.
# step = 5 genera ~1,100,000 puntos limpios en menos de 4 segundos.
STEP = 5

print(f"\n[3/5] Extrayendo puntos con paso STEP = {STEP}...")

sub_rgb = rgb[::STEP, ::STEP]
sub_dark = dark_mask_dilated[::STEP, ::STEP]
sub_white = is_white[::STEP, ::STEP]
sub_sea = is_sea[::STEP, ::STEP]
sh, sw, _ = sub_rgb.shape

# Convertir límites del recuadro a coordenadas muestreadas
sub_ymin, sub_ymax = ymin // STEP, ymax // STEP
sub_xmin, sub_xmax = xmin // STEP, xmax // STEP

# Candidatos iniciales: dentro del marco, sin elementos oscuros, sin blancos, sin mar
cand_mask = np.zeros((sh, sw), dtype=bool)
cand_mask[sub_ymin:sub_ymax, sub_xmin:sub_xmax] = True
cand_mask &= ~sub_dark
cand_mask &= ~sub_white
cand_mask &= ~sub_sea

# Filtro de densidad espacial:
# Elimina bordes exteriores y texto dentro del Golfo de California
white_density = cv2.boxFilter(sub_white.astype(np.float32), -1, (25, 25))
sea_density = cv2.boxFilter(sub_sea.astype(np.float32), -1, (31, 31))
cand_mask &= (white_density < 0.35)
cand_mask &= (sea_density < 0.25)

# Búsqueda de color más cercano con KDTree
cand_pixels = sub_rgb[cand_mask]
dists, indices = tree.query(cand_pixels)

# Umbral de tolerancia de color (distancia euclidiana < 26)
good_matches = dists < 26

valid_sub_mask = np.zeros((sh, sw), dtype=bool)
cand_coords = np.argwhere(cand_mask)
good_coords = cand_coords[good_matches]
valid_sub_mask[good_coords[:, 0], good_coords[:, 1]] = True

# Cierre morfológico para conectar el territorio continental y descartar ruido aislado
kernel_land = cv2.getStructuringElement(cv2.MORPH_RECT, (15, 15))
closed_land = cv2.morphologyEx(valid_sub_mask.astype(np.uint8), cv2.MORPH_CLOSE, kernel_land)

num_labels, labels, stats, centroids = cv2.connectedComponentsWithStats(closed_land, connectivity=8)
land_region = np.zeros((sh, sw), dtype=bool)
for lbl in range(1, num_labels):
    if stats[lbl, cv2.CC_STAT_AREA] > 500:
        land_region |= (labels == lbl)

# Puntos finales válidos
final_mask = valid_sub_mask & land_region
final_coords = np.argwhere(final_mask)
final_pixels = sub_rgb[final_coords[:, 0], final_coords[:, 1]]
_, final_indices = tree.query(final_pixels)
final_nt = nt_values[final_indices]

# Coordenadas en la imagen original
final_y_full = final_coords[:, 0] * STEP
final_x_full = final_coords[:, 1] * STEP

# Georreferenciación matemática exacta:
# Longitud WGS84/NAD27: xmin=-116.0, xmax=-114.0
# Latitud WGS84/NAD27:  ymin=32.0 (norte), ymax=31.0 (sur)
lat = lat_top - (final_y_full - ymin) / (ymax - ymin) * (lat_top - lat_bottom)
lon = lon_left + (final_x_full - xmin) / (xmax - xmin) * (lon_right - lon_left)

# -----------------------------------------------------------------------------
# 6. EXPORTAR A CSV PARA QGIS
# -----------------------------------------------------------------------------
print(f"\n[4/5] Guardando {len(final_nt):,} puntos en CSV georreferenciado...")

df = pd.DataFrame({
    'Longitud': np.round(lon, 6),
    'Latitud': np.round(lat, 6),
    'X_pixel': final_x_full,
    'Y_pixel': final_y_full,
    'Nanoteslas': final_nt
})

csv_out = os.path.join(script_dir, 'puntos_magnetica_sanfelipe_limpios.csv')
df.to_csv(csv_out, index=False)
print(f"      Archivo CSV guardado: {csv_out}")

# -----------------------------------------------------------------------------
# 7. GENERAR IMAGEN DE VISTA PREVIA
# -----------------------------------------------------------------------------
print("\n[5/5] Generando imagen de verificación de los puntos extraídos...")

preview = np.ones((sh, sw, 3), dtype=np.uint8) * 255  # Fondo blanco limpio
preview[final_coords[:, 0], final_coords[:, 1]] = ref_colors[final_indices]

preview_bgr = cv2.cvtColor(preview, cv2.COLOR_RGB2BGR)
preview_out = os.path.join(script_dir, 'puntos_sanfelipe_preview.jpg')
cv2.imwrite(preview_out, preview_bgr)
print(f"      Vista previa guardada: {preview_out}")

t_total = time.time() - t_start
print("\n" + "=" * 65)
print(f" ¡PROCESO COMPLETADO EXITOSAMENTE EN {t_total:.2f} SEGUNDOS!")
print(f" Puntos limpios listos para QGIS: {len(df):,}")
print(" Rango de Latitud:   {:.4f}° a {:.4f}° N".format(lat.min(), lat.max()))
print(" Rango de Longitud:  {:.4f}° a {:.4f}° W".format(lon.min(), lon.max()))
print(" Rango Nanoteslas:   {} nT a {} nT".format(final_nt.min(), final_nt.max()))
print("=" * 65)
