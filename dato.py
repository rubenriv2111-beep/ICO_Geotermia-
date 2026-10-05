import rasterio
import pandas as pd
from pyproj import Transformer

ruta_vrt = r"C:\Users\ruben\OneDrive\Desktop\ProyectoICO\LC09_L2SP_038038_20260925_20260926_02_T1\Matriz_Multivariada.vrt"

print("\n==========================================")
print("      MATRIZ MULTIVARIADA - GEOTERMIA")
print("==========================================")

print("\nLeyendo datos...")

with rasterio.open(ruta_vrt) as src:
    datos = src.read()
    transform = src.transform
    crs = src.crs
    filas = src.height
    columnas = src.width
    numero_bandas = src.count

print(f"Filas: {filas:,}")
print(f"Columnas: {columnas:,}")
print(f"Bandas: {numero_bandas}")
print(f"Sistema de coordenadas: {crs}")

# ============================================================
# CREAR TABLA
# ============================================================

print("\nPreparando tabla...")

rows, cols = datos[0].shape

# Generar coordenadas de forma eficiente
indices_fila, indices_columna = __import__("numpy").indices((rows, cols))

X, Y = rasterio.transform.xy(
    transform,
    indices_fila,
    indices_columna,
    offset="center"
)

df = pd.DataFrame({
    "X_Longitud_UTM": X,
    "Y_Latitud_UTM": Y
})

nombres_bandas = [
    "Banda_1_Pendientes",
    "Banda_2_LST",
    "Banda_3_Prox_Fallas",
    "Banda_4_NDVI",
    "Banda_5_Elevaciones",
    "Banda_6_Magnetometria"
]

for i in range(numero_bandas):
    if i < len(nombres_bandas):
        df[nombres_bandas[i]] = datos[i].flatten()
    else:
        df[f"Banda_{i + 1}"] = datos[i].flatten()

# Eliminar valores NoData / NaN
df = df.dropna()

print(f"\nRegistros válidos disponibles: {len(df):,}")

# ============================================================
# ELEGIR SISTEMA DE COORDENADAS
# ============================================================

print("\n==========================================")
print("       SISTEMA DE COORDENADAS")
print("==========================================")

print("\n¿Cómo quieres visualizar las coordenadas?")
print("1. Coordenadas UTM")
print("2. Grados geográficos (Longitud / Latitud)")

opcion_coord = input("\nSelecciona una opción (1 o 2): ").strip()

# ============================================================
# ELEGIR CANTIDAD DE DATOS
# ============================================================

print("\n==========================================")
print("          CANTIDAD DE DATOS")
print("==========================================")

print("\n¿Cuántos datos quieres visualizar?")
print("Ejemplos: 10, 100, 200")
print("También puedes escribir 'todos'.")

opcion_cantidad = input("\nCantidad de datos: ").strip().lower()

# ============================================================
# SELECCIÓN ALEATORIA
# ============================================================

if opcion_cantidad == "todos":

    muestra = df.copy()

else:

    try:
        cantidad = int(opcion_cantidad)

        if cantidad <= 0:
            print("\nError: la cantidad debe ser mayor que cero.")
            exit()

        if cantidad > len(df):
            print(f"\nSolo existen {len(df):,} registros disponibles.")
            cantidad = len(df)

        muestra = df.sample(
            n=cantidad,
            random_state=None
        )

    except ValueError:
        print("\nError: escribe un número válido o 'todos'.")
        exit()

# ============================================================
# CONVERTIR UTM A GRADOS
# ============================================================

if opcion_coord == "1":

    columnas_coord = [
        "X_Longitud_UTM",
        "Y_Latitud_UTM"
    ]

elif opcion_coord == "2":

    print("\nConvirtiendo coordenadas UTM a grados geográficos...")

    transformer = Transformer.from_crs(
        "EPSG:32611",
        "EPSG:4326",
        always_xy=True
    )

    longitud, latitud = transformer.transform(
        muestra["X_Longitud_UTM"].values,
        muestra["Y_Latitud_UTM"].values
    )

    muestra = muestra.copy()

    muestra["Longitud"] = longitud
    muestra["Latitud"] = latitud

    columnas_coord = [
        "Longitud",
        "Latitud"
    ]

else:

    print("\nError: opción de coordenadas no válida.")
    exit()

# ============================================================
# MOSTRAR RESULTADOS
# ============================================================

columnas_bandas = [
    "Banda_1_Pendientes",
    "Banda_2_LST",
    "Banda_3_Prox_Fallas",
    "Banda_4_NDVI",
    "Banda_5_Elevaciones",
    "Banda_6_Magnetometria"
]

columnas_mostrar = columnas_coord + columnas_bandas

print("\n\n==========================================")
print("        MUESTRA ALEATORIA DE DATOS")
print("==========================================")

print(
    muestra[columnas_mostrar].to_string(index=False)
)

# ============================================================
# RESUMEN
# ============================================================

print("\n==========================================")
print("              RESUMEN")
print("==========================================")

print(f"Registros mostrados: {len(muestra):,}")
print(f"Registros disponibles: {len(df):,}")

if opcion_coord == "1":
    print("Coordenadas: UTM Zona 11N")
else:
    print("Coordenadas: WGS84 - Grados geográficos")

print("Selección: Aleatoria")
print("==========================================\n")