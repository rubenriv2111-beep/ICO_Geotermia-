import os
import time
import cv2
import numpy as np
import pandas as pd
from scipy.spatial import cKDTree

print("=" * 65)
print(" EXTRACCIÓN Y LIMPIEZA DE DATOS AEROMAGNÉTICOS - CARTA MEXICALI")
print("=" * 65)

t_start = time.time()

# -----------------------------------------------------------------------------
# 1. RUTA DE LA IMAGEN Y CONFIGURACIÓN
# -----------------------------------------------------------------------------
script_dir = os.path.dirname(os.path.abspath(__file__))
img_path = os.path.join(script_dir, 'CartaMagneticaMexicali.jpg')

if not os.path.exists(img_path):
    raise FileNotFoundError(f"No se encontró el archivo: {img_path}")

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
ymin, ymax = 168, 5440
xmin, xmax = 226, 9125

# Coordenadas geográficas oficiales de la Carta Mexicali (SGM 1:250,000)
# Latitud:  32° 00' N (sur) a 33° 00' N (norte)
# Longitud: 116° 00' W (oeste) a 114° 00' W (este)
lat_top, lat_bottom = 33.0, 32.0
lon_left, lon_right = -116.0, -114.0

# -----------------------------------------------------------------------------
# 3. PALETA OFICIAL SGM (MEXICALI)
# -----------------------------------------------------------------------------
color_scale = {
    -340: [3, 179, 229],   # #03B3E5
    -320: [88, 196, 234],  # #58C4EA
    -300: [129, 206, 234], # #81CEEA
    -280: [165, 215, 224], # #A5D7E0
    -260: [203, 230, 221], # #CBE6DD
    -240: [224, 238, 223], # #E0EEDF
    -220: [226, 242, 231], # #E2F2E7
    -200: [240, 247, 231], # #F0F7E7
    -180: [255, 252, 223], # #FFFCDF
    -160: [255, 250, 210], # #FFFAD2
    -140: [255, 237, 187], # #FFEDBB
    -120: [255, 228, 183], # #FFE4B7
    -100: [253, 208, 175], # #FDD0AF
    -80:  [248, 172, 123], # #F8AC7B
    -60:  [248, 154, 92],  # #F89A5C
    -40:  [245, 131, 69]   # #F58345
}

nt_values = np.array(list(color_scale.keys()))
ref_colors = np.array(list(color_scale.values()))
tree = cKDTree(ref_colors)

# -----------------------------------------------------------------------------
# 4. MÁSCARAS DE FILTRADO (TEXTOS, CURVAS NEGRAS Y BLANCO/EE.UU.)
# -----------------------------------------------------------------------------
print("\n[2/5] Generando filtros de ruido (textos, curvas, ejes y territorio blanco)...")

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

# -----------------------------------------------------------------------------
# 5. MUESTREO Y EMPAREJAMIENTO VECTORIZADO
# -----------------------------------------------------------------------------
# STEP: Espaciado de píxeles para muestreo.
# step = 5 genera ~769,000 puntos (alta densidad, ideal para interpolación en QGIS)
# step = 10 genera ~190,000 puntos (más ligero para pruebas rápidas)
STEP = 5

print(f"\n[3/5] Extrayendo puntos con paso STEP = {STEP}...")

sub_rgb = rgb[::STEP, ::STEP]
sub_dark = dark_mask_dilated[::STEP, ::STEP]
sub_white = is_white[::STEP, ::STEP]
sh, sw, _ = sub_rgb.shape

# Convertir límites a coordenadas reducidas
sub_ymin, sub_ymax = ymin // STEP, ymax // STEP
sub_xmin, sub_xmax = xmin // STEP, xmax // STEP

# Candidatos: dentro del recuadro, no oscuros (sin textos/líneas), no blancos
cand_mask = np.zeros((sh, sw), dtype=bool)
cand_mask[sub_ymin:sub_ymax, sub_xmin:sub_xmax] = True
cand_mask &= ~sub_dark
cand_mask &= ~sub_white

# Búsqueda de color con KDTree
cand_pixels = sub_rgb[cand_mask]
dists, indices = tree.query(cand_pixels)

# Umbral estricto de coincidencia de color (distancia euclidiana < 26)
good_matches = dists < 26

valid_sub_mask = np.zeros((sh, sw), dtype=bool)
cand_coords = np.argwhere(cand_mask)
good_coords = cand_coords[good_matches]
valid_sub_mask[good_coords[:, 0], good_coords[:, 1]] = True

# Filtro de vecindad de blancos:
# En el territorio de EE.UU., las cruces azules de la retícula están rodeadas de >80% blanco.
# En México, los datos válidos están rodeados de <20% blanco.
white_density = cv2.boxFilter(sub_white.astype(np.float32), -1, (25, 25))
valid_sub_mask &= (white_density < 0.35)

# C) Aislamiento morfológico del polígono de México
kernel_mex = cv2.getStructuringElement(cv2.MORPH_RECT, (15, 15))
closed_mex = cv2.morphologyEx(valid_sub_mask.astype(np.uint8), cv2.MORPH_CLOSE, kernel_mex)

num_labels, labels, stats, centroids = cv2.connectedComponentsWithStats(closed_mex, connectivity=8)
mex_region = np.zeros((sh, sw), dtype=bool)
for lbl in range(1, num_labels):
    if stats[lbl, cv2.CC_STAT_AREA] > 500:
        mex_region |= (labels == lbl)

# Puntos finales válidos (dentro de México y con color coincidente)
final_mask = valid_sub_mask & mex_region
final_coords = np.argwhere(final_mask)
final_pixels = sub_rgb[final_coords[:, 0], final_coords[:, 1]]
_, final_indices = tree.query(final_pixels)
final_nt = nt_values[final_indices]

# Coordenadas en la imagen original
final_y_full = final_coords[:, 0] * STEP
final_x_full = final_coords[:, 1] * STEP

# Georreferenciación matemática exacta:
# Longitud WGS84/NAD27: xmin=-116.0, xmax=-114.0
# Latitud WGS84/NAD27:  ymin=33.0 (norte), ymax=32.0 (sur)
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

csv_out = os.path.join(script_dir, 'puntos_magnetica_limpios.csv')
df.to_csv(csv_out, index=False)
print(f"      Archivo CSV guardado: {csv_out}")

# -----------------------------------------------------------------------------
# 7. GENERAR IMAGEN DE VISTA PREVIA
# -----------------------------------------------------------------------------
print("\n[5/5] Generando imagen de verificación de los puntos extraídos...")

preview = np.ones((sh, sw, 3), dtype=np.uint8) * 255  # Fondo blanco limpio
preview[final_coords[:, 0], final_coords[:, 1]] = ref_colors[final_indices]

preview_bgr = cv2.cvtColor(preview, cv2.COLOR_RGB2BGR)
preview_out = os.path.join(script_dir, 'puntos_extraidos_preview.jpg')
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