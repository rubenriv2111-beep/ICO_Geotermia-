import os
import time
import subprocess
import numpy as np
import pandas as pd
import tifffile
from scipy.spatial import cKDTree

print("=" * 65)
print(" INTERPOLACIÓN RÁPIDA DE DATOS AEROMAGNÉTICOS (MEXICALI + SAN FELIPE)")
print("=" * 65)

t_start = time.time()
script_dir = os.path.dirname(os.path.abspath(__file__))

csv_path = os.path.join(script_dir, 'puntos_magnetica_mexicali_sanfelipe_combinados.csv')
if not os.path.exists(csv_path):
    raise FileNotFoundError(f"No se encontró el archivo: {csv_path}")

print(f"\n[1/4] Leyendo datos: {os.path.basename(csv_path)}...")
df = pd.read_csv(csv_path)
coords = np.column_stack([df['Longitud'].values, df['Latitud'].values])
vals = df['Nanoteslas'].values
print(f"      Puntos cargados: {len(df):,} en {time.time() - t_start:.2f}s")

# -----------------------------------------------------------------------------
# MALLA DE SALIDA
# Rango: Lat 31.0 a 33.0 N, Lon -116.0 a -114.0 W
# Resolución: 0.001 grados (~100 metros) -> 2000 x 2000 píxeles
# -----------------------------------------------------------------------------
print("\n[2/4] Construyendo cuadrícula geográfica y árbol espacial KDTree...")
res = 0.001
lons = np.arange(-116.0, -114.0, res)
lats = np.arange(33.0, 31.0, -res)
ncols = len(lons)
nrows = len(lats)
print(f"      Dimensiones de la cuadrícula: {ncols} columnas x {nrows} filas ({ncols * nrows:,} celdas)")

tree = cKDTree(coords)

gx, gy = np.meshgrid(lons, lats)
grid_pts = np.column_stack([gx.ravel(), gy.ravel()])

# -----------------------------------------------------------------------------
# INTERPOLACIÓN IDW VECTORIZADA (K-Nearest Neighbors con radio de corte)
# -----------------------------------------------------------------------------
print("\n[3/4] Ejecutando interpolación IDW en paralelo (8 vecinos más cercanos)...")
t_idw = time.time()

# Radio máximo de búsqueda: 0.02 grados (~2 km)
# Si no hay puntos en 2 km (como en el mar o EE.UU.), queda como NoData / Transparente
max_dist = 0.02
dists, idxs = tree.query(grid_pts, k=8, distance_upper_bound=max_dist, workers=-1)

# Ponderación IDW (Potencia 2)
weights = 1.0 / np.maximum(dists, 1e-5)**2
valid_mask = dists[:, 0] < max_dist

idxs_safe = np.where(idxs < len(vals), idxs, 0)
val_neighbors = vals[idxs_safe]
w_sum = np.sum(weights, axis=1)
interpolated = np.sum(weights * val_neighbors, axis=1) / np.maximum(w_sum, 1e-10)

nodata_val = -9999.0
grid_result = np.full((nrows, ncols), nodata_val, dtype=np.float32)
grid_result.ravel()[valid_mask] = interpolated[valid_mask]

print(f"      Interpolación completada en {time.time() - t_idw:.2f}s")
print(f"      Celdas interpoladas con datos: {np.count_nonzero(valid_mask):,}")

# -----------------------------------------------------------------------------
# GUARDAR GEOTIFF PARA QGIS
# -----------------------------------------------------------------------------
print("\n[4/4] Exportando GeoTIFF georreferenciado (EPSG:4326)...")
temp_tif = os.path.join(script_dir, 'temp_interp.tif')
final_tif = os.path.join(script_dir, 'mapa_aeromagnetico_completo.tif')

tifffile.imwrite(temp_tif, grid_result)

# Asignar proyección y extensión con gdal_translate de QGIS si está disponible
gdal_translate = r"C:\Program Files\QGIS 3.44.15\bin\gdal_translate.exe"
if os.path.exists(gdal_translate):
    cmd = [
        gdal_translate,
        "-a_srs", "EPSG:4326",
        "-a_ullr", "-116.0", "33.0", "-114.0", "31.0",
        "-a_nodata", str(nodata_val),
        temp_tif,
        final_tif
    ]
    subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
    if os.path.exists(temp_tif):
        os.remove(temp_tif)
else:
    # Si no estuviera gdal_translate, renombra y guarda .tfw y .prj
    if os.path.exists(final_tif):
        os.remove(final_tif)
    os.rename(temp_tif, final_tif)
    with open(final_tif.replace('.tif', '.tfw'), 'w') as f:
        f.write(f"{res}\n0.0\n0.0\n{-res}\n{-116.0 + res/2}\n{33.0 - res/2}\n")
    with open(final_tif.replace('.tif', '.prj'), 'w') as f:
        f.write('GEOGCS["WGS 84",DATUM["WGS_1984",SPHEROID["WGS 84",6378137,298.257223563]],PRIMEM["Greenwich",0],UNIT["degree",0.0174532925199433]]')

t_total = time.time() - t_start
print("\n" + "=" * 65)
print(f" ¡RÁSTER GEOTIFF GENERADO EN SOLO {t_total:.2f} SEGUNDOS!")
print(f" Archivo listo para abrir en QGIS: {final_tif}")
print(" Resolución: ~100 metros por píxel (0.001°)")
print(" NoData (Transparente): Golfo de California y territorio de EE.UU.")
print("=" * 65)
