import os
import tifffile
import numpy as np

def cargar_matriz_magnetometria(ruta_tif=None):
    """
    Carga la matriz aeromagnética curada de alta resolución generada para CICESE.
    
    Retorna:
        data (np.ndarray): Matriz 2D Float32 con valores en Nanoteslas (nT).
                           Los valores fuera del levantamiento (EE.UU. y Mar) contienen np.nan.
        metadatos (dict): Información de cobertura geográfica, resolución y estadísticas.
    """
    if ruta_tif is None:
        work_dir = r"C:\Users\ruben\OneDrive\Desktop\Procesamiento de imagenes"
        ruta_tif = os.path.join(work_dir, "mapa_aeromagnetico_elgp_curado.tif")

    if not os.path.exists(ruta_tif):
        raise FileNotFoundError(f"No se encontró el archivo: {ruta_tif}")

    data = tifffile.imread(ruta_tif).astype(np.float32)
    # Reemplazar NoData (-99999) por NaN para operaciones matemáticas en NumPy
    data[data <= -90000.0] = np.nan

    h, w = data.shape
    # Coordenadas geográficas oficiales (31°N a 33°N, 116°W a 114°W)
    lons = np.linspace(-116.0, -114.0, w)
    lats = np.linspace(33.0, 31.0, h)

    metadatos = {
        "filas": h,
        "columnas": w,
        "total_celdas": h * w,
        "celdas_validas": int(np.count_nonzero(~np.isnan(data))),
        "min_nT": float(np.nanmin(data)),
        "max_nT": float(np.nanmax(data)),
        "media_nT": float(np.nanmean(data)),
        "std_nT": float(np.nanstd(data)),
        "longitudes": lons,
        "latitudes": lats
    }
    return data, metadatos

if __name__ == "__main__":
    print("=" * 65)
    print(" CARGADOR DE MATRICES GEOFÍSICAS PARA MODELADO ELGP (CICESE)")
    print("=" * 65)
    matriz, meta = cargar_matriz_magnetometria()
    print(f"\nMatriz cargada exitosamente:")
    print(f" - Dimensiones: {meta['filas']} filas x {meta['columnas']} columnas")
    print(f" - Celdas válidas en México (tierra firme): {meta['celdas_validas']:,} ({meta['celdas_validas']/meta['total_celdas']*100:.1f}%)")
    print(f" - Rango geofísico: {meta['min_nT']:.1f} nT a {meta['max_nT']:.1f} nT")
    print(f" - Media: {meta['media_nT']:.1f} nT | Desviación estándar: {meta['std_nT']:.1f} nT")
    print("\nEstructura lista para alimentar el algoritmo de Programación Genética.")
