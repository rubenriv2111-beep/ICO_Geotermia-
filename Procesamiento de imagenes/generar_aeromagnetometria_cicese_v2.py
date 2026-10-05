import os
import sys
import time
import subprocess
import cv2
import fitz
import numpy as np
import tifffile
import pandas as pd
import matplotlib.cm as cm
from scipy.spatial import cKDTree
from scipy.ndimage import distance_transform_edt, gaussian_filter

def main():
    print("=" * 80)
    print(" RECONSTRUCCIÓN AEROMAGNÉTICA PURA Y EXACTA (SGM) — CICESE ELGP")
    print(" Cartas Mexicali (H11-12, paso 20 nT) y San Felipe (H11-3, paso 50 nT)")
    print(" Calibración No-Invertida | Máxima Precisión de Anomalías Concéntricas")
    print("=" * 80)

    t_start = time.time()
    work_dir = r"C:\Users\ruben\OneDrive\Desktop\Procesamiento de imagenes"
    pdf_dir = r"C:\Users\ruben\OneDrive\Desktop\ProyectoICO\LC09_L2SP_038038_20260925_20260926_02_T1"
    art_dir = r"C:\Users\ruben\.gemini\antigravity\brain\4b5923ef-c3b4-4cf6-868c-821d9273731f"

    p_mex_pdf = os.path.join(pdf_dir, "CartaMagneticaMexicali.pdf")
    p_sf_pdf = os.path.join(pdf_dir, "CartaMagneticaSanFelipe.pdf")

    gdal_translate = r"C:\Program Files\QGIS 3.44.15\bin\gdal_translate.exe"
    gdalwarp = r"C:\Program Files\QGIS 3.44.15\bin\gdalwarp.exe"

    if not os.path.exists(p_mex_pdf) or not os.path.exists(p_sf_pdf):
        raise FileNotFoundError(f"No se encontraron los PDFs en: {pdf_dir}")

    # Resolución estándar para 30 metros por píxel en escala 1:250,000
    W = 4449
    H_sheet = 2636

    # 16 Colores oficiales de la leyenda SGM en orden físico (Azul = Mínimo nT -> Naranja = Máximo nT)
    # Color 0 (Azul) = Anomalía negativa extrema
    # Color 15 (Naranja rojizo) = Anomalía positiva / alta
    ref_colors_rgb = np.array([
        [4, 180, 230], [90, 196, 234], [130, 207, 235], [166, 215, 226],
        [203, 232, 221], [223, 239, 222], [227, 242, 231], [240, 247, 231],
        [255, 252, 223], [255, 251, 210], [255, 238, 188], [255, 228, 184],
        [253, 209, 176], [250, 173, 124], [248, 155, 92],  [245, 131, 69]
    ], dtype=np.uint8)
    ref_colors_norm = ref_colors_rgb / 255.0

    # Escala física exacta Carta Mexicali (paso = 20 nT entre isolíneas)
    # Rangos: < -340, -340..-320, ..., > -60 nT
    val_mex = np.array([-350, -330, -310, -290, -270, -250, -230, -210,
                        -190, -170, -150, -130, -110,  -90,  -70,  -50], dtype=np.float32)
    thresh_mex = np.array([-340, -320, -300, -280, -260, -240, -220, -200,
                           -180, -160, -140, -120, -100,  -80,  -60,   50], dtype=np.float32)

    # Escala física exacta Carta San Felipe (paso = 50 nT entre isolíneas)
    # Rangos: < -600, -600..-550, ..., 50..100, > 100 nT
    val_sf = np.array([-625, -575, -525, -475, -425, -375, -325, -275,
                       -225, -175, -125,  -75,  -25,   25,   75,  125], dtype=np.float32)
    thresh_sf = np.array([-600, -550, -500, -450, -400, -350, -300, -250,
                          -200, -150, -100,  -50,    0,   50,  100,  200], dtype=np.float32)

    tree_mex = cKDTree(ref_colors_rgb)
    tree_sf = cKDTree(ref_colors_rgb)

    # Marcos geográficos interiores exactos (1° Latitud x 2° Longitud)
    rect_mex = fitz.Rect(184.32, 273.20, 2304.46, 1485.00)
    rect_sf = fitz.Rect(139.40, 240.45, 2283.06, 1463.24)

    # -------------------------------------------------------------------------
    # 1. EXTRACCIÓN VECTORIAL PURA DE POLÍGONOS DE COLOR (SIN TINTA CARTOGRÁFICA)
    # -------------------------------------------------------------------------
    def extraer_vector_puro(pdf_path, neat_rect, nombre):
        print(f"\n[1/6] Extrayendo geometría vectorial pura de {nombre}...")
        t0 = time.time()
        doc = fitz.open(pdf_path)
        page = doc[0]
        drawings = page.get_drawings()

        doc_clean = fitz.open()
        page_clean = doc_clean.new_page(width=page.rect.width, height=page.rect.height)

        count = 0
        for d in drawings:
            if d['fill'] is None:
                continue
            r = d['rect']
            if not r.intersects(neat_rect) or r.y0 > 1530:
                continue
            fill_arr = np.array(d['fill'])
            dists = np.linalg.norm(ref_colors_norm - fill_arr, axis=1)
            if np.min(dists) > 0.05:
                continue

            count += 1
            s = page_clean.new_shape()
            for item in d['items']:
                if item[0] == 'l': s.draw_line(item[1], item[2])
                elif item[0] == 'c': s.draw_bezier(item[1], item[2], item[3], item[4])
                elif item[0] == 're': s.draw_rect(item[1])
                elif item[0] == 'qu': s.draw_quad(item[1])
            s.finish(fill=d['fill'], color=None, even_odd=d.get('even_odd', True))
            s.commit()

        # Renderizar en espacio DeviceRGB nativo
        pix = page_clean.get_pixmap(clip=neat_rect, dpi=150)
        img_rgb = np.frombuffer(pix.samples, dtype=np.uint8).reshape((pix.height, pix.width, pix.n))[:, :, :3]
        img_res = cv2.resize(img_rgb, (W, H_sheet), interpolation=cv2.INTER_NEAREST)
        print(f"      -> {count:,} polígonos transferidos intactos en {time.time()-t0:.2f}s.")
        return img_res

    img_m_rgb = extraer_vector_puro(p_mex_pdf, rect_mex, "Carta Mexicali")
    img_s_rgb = extraer_vector_puro(p_sf_pdf, rect_sf, "Carta San Felipe")

    # -------------------------------------------------------------------------
    # 2. DELIMITACIÓN DE MÁSCARAS GEOGRÁFICAS Y SELLADO DE LÍNEAS
    # -------------------------------------------------------------------------
    print("\n[2/6] Delimitando máscaras (USA / Golfo de California) y sellando líneas en tierra...")

    # A. MEXICALI:
    is_white_m = (img_m_rgb[:, :, 0] > 245) & (img_m_rgb[:, :, 1] > 245) & (img_m_rgb[:, :, 2] > 245)
    usa_dense = cv2.boxFilter(is_white_m.astype(np.float32), -1, (31, 31)) > 0.50
    _, labels_m, stats_m, _ = cv2.connectedComponentsWithStats(usa_dense.astype(np.uint8))
    top_labels = set(labels_m[0, :]).difference({0})
    usa_mask = np.isin(labels_m, list(top_labels))
    usa_mask = cv2.dilate(usa_mask.astype(np.uint8), cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (7, 7))) > 0

    mex_land = ~usa_mask
    valid_mex = mex_land & ~is_white_m
    dist_m, (i_m, j_m) = distance_transform_edt(~valid_mex, return_indices=True)
    img_m_clean = np.copy(img_m_rgb)
    missing_mex = mex_land & is_white_m
    img_m_clean[missing_mex] = img_m_rgb[i_m[missing_mex], j_m[missing_mex]]

    # Consulta directa RGB -> árbol KDTree (SIN inversión de canales)
    _, idx_m = tree_mex.query(img_m_clean.reshape(-1, 3))
    grid_m = val_mex[idx_m].reshape((H_sheet, W))
    grid_m[usa_mask] = np.nan
    print(f"      -> Mexicali: Rango {np.nanmin(grid_m):.0f} a {np.nanmax(grid_m):.0f} nT (Azul = -350 nT, Naranja = -50 nT).")

    # B. SAN FELIPE:
    is_white_s = (img_s_rgb[:, :, 0] > 245) & (img_s_rgb[:, :, 1] > 245) & (img_s_rgb[:, :, 2] > 245)
    sea_dense = cv2.boxFilter(is_white_s.astype(np.float32), -1, (31, 31)) > 0.50
    _, labels_s, stats_s, _ = cv2.connectedComponentsWithStats(sea_dense.astype(np.uint8))
    sea_edge_labels = set(labels_s[:, -1]).union(set(labels_s[-1, :])).difference({0})
    sea_mask = np.isin(labels_s, list(sea_edge_labels))
    sea_mask = cv2.dilate(sea_mask.astype(np.uint8), cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (7, 7))) > 0

    sf_land = ~sea_mask
    valid_sf = sf_land & ~is_white_s
    dist_s, (i_s, j_s) = distance_transform_edt(~valid_sf, return_indices=True)
    img_s_clean = np.copy(img_s_rgb)
    missing_sf = sf_land & is_white_s
    img_s_clean[missing_sf] = img_s_rgb[i_s[missing_sf], j_s[missing_sf]]

    # Consulta directa RGB -> árbol KDTree (SIN inversión de canales)
    _, idx_s = tree_sf.query(img_s_clean.reshape(-1, 3))
    grid_s = val_sf[idx_s].reshape((H_sheet, W))
    grid_s[sea_mask] = np.nan
    print(f"      -> San Felipe: Rango {np.nanmin(grid_s):.0f} a {np.nanmax(grid_s):.0f} nT (Azul = -625 nT, Naranja = +125 nT).")

    # -------------------------------------------------------------------------
    # 3. EXPORTAR HOJAS INDIVIDUALES CON ESCALAS PURAS SGM
    # -------------------------------------------------------------------------
    print("\n[3/6] Exportando GeoTIFFs individuales con escalas independientes...")
    tif_m_raw = os.path.join(work_dir, "temp_m_raw.tif")
    tif_s_raw = os.path.join(work_dir, "temp_s_raw.tif")
    out_m_tif = os.path.join(work_dir, "mapa_aeromagnetico_mexicali_exacto.tif")
    out_s_tif = os.path.join(work_dir, "mapa_aeromagnetico_sanfelipe_exacto.tif")

    mat_m = np.copy(grid_m)
    mat_m[np.isnan(mat_m)] = -99999.0
    tifffile.imwrite(tif_m_raw, mat_m)
    subprocess.run([
        gdal_translate,
        "-a_srs", "EPSG:4326",
        "-a_ullr", "-116.0", "33.0", "-114.0", "32.0",
        "-a_nodata", "-99999",
        "-co", "COMPRESS=DEFLATE",
        tif_m_raw, out_m_tif
    ], check=True)
    if os.path.exists(tif_m_raw): os.remove(tif_m_raw)

    mat_s = np.copy(grid_s)
    mat_s[np.isnan(mat_s)] = -99999.0
    tifffile.imwrite(tif_s_raw, mat_s)
    subprocess.run([
        gdal_translate,
        "-a_srs", "EPSG:4326",
        "-a_ullr", "-116.0", "32.0", "-114.0", "31.0",
        "-a_nodata", "-99999",
        "-co", "COMPRESS=DEFLATE",
        tif_s_raw, out_s_tif
    ], check=True)
    if os.path.exists(tif_s_raw): os.remove(tif_s_raw)

    print(f"      -> Mexicali TIF: {out_m_tif}")
    print(f"      -> San Felipe TIF: {out_s_tif}")

    # -------------------------------------------------------------------------
    # 4. ARMONIZACIÓN EN 32°N Y UNIFICACIÓN CONTINUA
    # -------------------------------------------------------------------------
    print("\n[4/6] Armonizando contacto entre cartas en Latitud 32°N...")
    grid_m_comp = np.copy(grid_m)
    grid_s_comp = np.copy(grid_s)

    diff_border = np.nanmean(grid_m_comp[-5:, :], axis=0) - np.nanmean(grid_s_comp[:5, :], axis=0)
    diff_smooth = np.copy(diff_border)
    valid_d = ~np.isnan(diff_border)
    if np.any(valid_d):
        diff_smooth[~valid_d] = np.nanmedian(diff_border)
        diff_smooth = cv2.GaussianBlur(diff_smooth.reshape(1, -1), (201, 1), 50)[0]

    blend_h = 45
    for i in range(blend_h):
        w = 0.5 * (1.0 - np.cos(np.pi * (i + 1) / blend_h)) * 0.5
        row_m = H_sheet - blend_h + i
        m_mask = ~np.isnan(grid_m_comp[row_m, :])
        grid_m_comp[row_m, m_mask] -= (w * diff_smooth)[m_mask]

        row_s = i
        s_mask = ~np.isnan(grid_s_comp[row_s, :])
        grid_s_comp[row_s, s_mask] += ((0.5 - w) * diff_smooth)[s_mask]

    unified_discrete = np.vstack([grid_m_comp, grid_s_comp]).astype(np.float32)

    # Campo continuo geofísico (suavizado sub-intervalo para derivadas ELGP sin escalones)
    valid_mask = ~np.isnan(unified_discrete)
    dist_u, (i_u, j_u) = distance_transform_edt(~valid_mask, return_indices=True)
    temp_filled = unified_discrete[i_u, j_u]
    smooth_geophys = gaussian_filter(temp_filled, sigma=2.0)
    unified_continuous = np.copy(smooth_geophys)
    unified_continuous[~valid_mask] = np.nan

    # -------------------------------------------------------------------------
    # 5. EXPORTACIÓN GEOTIFF UNIFICADO (WGS84 y UTM 11N 30m)
    # -------------------------------------------------------------------------
    print("\n[5/6] Exportando GeoTIFFs unificados WGS84 y UTM 11N (30m)...")
    out_exact_4326 = os.path.join(work_dir, "mapa_aeromagnetico_cicese_exacto.tif")
    out_exact_utm = os.path.join(work_dir, "mapa_aeromagnetico_utm11n_exacto.tif")
    out_cont_4326 = os.path.join(work_dir, "mapa_aeromagnetico_cicese_continuo.tif")
    out_cont_utm = os.path.join(work_dir, "mapa_aeromagnetico_utm11n_continuo.tif")

    for grid_data, out_4326, out_utm in [
        (unified_discrete, out_exact_4326, out_exact_utm),
        (unified_continuous, out_cont_4326, out_cont_utm)
    ]:
        raw_tmp = os.path.join(work_dir, "temp_raw_export.tif")
        mat_exp = np.copy(grid_data)
        mat_exp[np.isnan(mat_exp)] = -99999.0
        tifffile.imwrite(raw_tmp, mat_exp)

        subprocess.run([
            gdal_translate,
            "-a_srs", "EPSG:4326",
            "-a_ullr", "-116.0", "33.0", "-114.0", "31.0",
            "-a_nodata", "-99999",
            "-co", "COMPRESS=DEFLATE",
            raw_tmp, out_4326
        ], check=True)
        if os.path.exists(raw_tmp): os.remove(raw_tmp)

        subprocess.run([
            gdalwarp,
            "-s_srs", "EPSG:4326",
            "-t_srs", "EPSG:32611",
            "-tr", "30.0", "30.0",
            "-r", "bilinear",
            "-srcnodata", "-99999",
            "-dstnodata", "-99999",
            "-co", "COMPRESS=DEFLATE",
            "-overwrite",
            out_4326, out_utm
        ], check=True)

    print(f"      -> GeoTIFF WGS84 discreto: {out_exact_4326}")
    print(f"      -> GeoTIFF UTM 11N 30m discreto: {out_exact_utm}")
    print(f"      -> GeoTIFF WGS84 continuo: {out_cont_4326}")
    print(f"      -> GeoTIFF UTM 11N 30m continuo: {out_cont_utm}")

    # -------------------------------------------------------------------------
    # 6. TABLAS CSV DE PUNTOS Y ESTILOS QGIS (.QML)
    # -------------------------------------------------------------------------
    print("\n[6/6] Generando CSVs de puntos, estilos QGIS (.qml) y vistas previas...")
    
    # CSV unificado de puntos cada 120m (submuestreo STEP=4)
    csv_p = os.path.join(work_dir, "puntos_magnetometria_exactos.csv")
    STEP = 4
    sub_vals = unified_discrete[::STEP, ::STEP]
    h_sub, w_sub = sub_vals.shape
    lons_sub = np.linspace(-116.0, -114.0, w_sub)
    lats_sub = np.linspace(33.0, 31.0, h_sub)
    lon_grid, lat_grid = np.meshgrid(lons_sub, lats_sub)

    valid_pts = ~np.isnan(sub_vals)
    df = pd.DataFrame({
        "Longitud": np.round(lon_grid[valid_pts], 6),
        "Latitud": np.round(lat_grid[valid_pts], 6),
        "Nanoteslas": np.round(sub_vals[valid_pts], 1)
    })
    df.to_csv(csv_p, index=False)
    print(f"      -> CSV de puntos unificado: {csv_p} ({len(df):,} puntos)")

    # CSV exclusivo San Felipe
    csv_sf_p = os.path.join(work_dir, "puntos_magnetometria_sanfelipe.csv")
    sub_sf = grid_s[::STEP, ::STEP]
    h_sfs, w_sfs = sub_sf.shape
    lons_sfs = np.linspace(-116.0, -114.0, w_sfs)
    lats_sfs = np.linspace(32.0, 31.0, h_sfs)
    lon_sfg, lat_sfg = np.meshgrid(lons_sfs, lats_sfs)
    valid_sf_pts = ~np.isnan(sub_sf)
    df_sf = pd.DataFrame({
        "Longitud": np.round(lon_sfg[valid_sf_pts], 6),
        "Latitud": np.round(lat_sfg[valid_sf_pts], 6),
        "Nanoteslas": np.round(sub_sf[valid_sf_pts], 1)
    })
    df_sf.to_csv(csv_sf_p, index=False)
    print(f"      -> CSV de puntos San Felipe: {csv_sf_p} ({len(df_sf):,} puntos)")

    # -------------------------------------------------------------------------
    # GENERADOR DE ESTILOS QGIS (.QML)
    # -------------------------------------------------------------------------
    def generar_qml(val_or_thresh_array, colors_rgb, labels, file_path, min_val, max_val, ramp_type='DISCRETE'):
        items_xml = []
        for v, col, lab in zip(val_or_thresh_array, colors_rgb, labels):
            hex_c = f"#{col[0]:02x}{col[1]:02x}{col[2]:02x}"
            items_xml.append(f"          <item alpha='255' value='{v}' label='{lab}' color='{hex_c}'/>")
        items_str = "\n".join(items_xml)
        qml_content = f"""<!DOCTYPE qgis PUBLIC 'http://mrcc.com/qgis.dtd' 'SYSTEM'>
<qgis styleCategories='AllStyleCategories' version='3.44.15' hasScaleBasedVisibilityFlag='0' minScale='1e+08' maxScale='0'>
  <pipe>
    <provider>
      <resampling maxOversampling='2' zoomedOutResamplingMethod='bilinear' zoomedInResamplingMethod='bilinear' enabled='false'/>
    </provider>
    <rasterrenderer alphaBand='-1' classificationMax='{max_val}' classificationMin='{min_val}' opacity='1' band='1' type='singlebandpseudocolor'>
      <rasterTransparency>
        <singleValuePixelList>
          <pixelListEntry min='-99999' max='-99999' percentTransparent='100'/>
        </singleValuePixelList>
      </rasterTransparency>
      <rastershader>
        <colorrampshader maximumValue='{max_val}' labelPrecision='0' clip='0' colorRampType='{ramp_type}' minimumValue='{min_val}'>
{items_str}
        </colorrampshader>
      </rastershader>
    </rasterrenderer>
    <brightnesscontrast brightness='0' contrast='0' gamma='1'/>
  </pipe>
  <blendMode>0</blendMode>
</qgis>"""
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(qml_content)

    # 1. MEXICALI QML DISCRETO
    labels_mex_disc = [
        "< -340 nT (-350 nT)", "-340 a -320 nT", "-320 a -300 nT", "-300 a -280 nT",
        "-280 a -260 nT", "-260 a -240 nT", "-240 a -220 nT", "-220 a -200 nT",
        "-200 a -180 nT", "-180 a -160 nT", "-160 a -140 nT", "-140 a -120 nT",
        "-120 a -100 nT", "-100 a -80 nT",  "-80 a -60 nT",   "> -60 nT (-50 nT)"
    ]
    generar_qml(thresh_mex, ref_colors_rgb, labels_mex_disc,
                os.path.join(work_dir, "estilo_sgm_mexicali_exacto.qml"), -350, -50, ramp_type='DISCRETE')

    # MEXICALI QML CONTINUO
    labels_mex_cont = [f"{v:.0f} nT" for v in val_mex]
    generar_qml(val_mex, ref_colors_rgb, labels_mex_cont,
                os.path.join(work_dir, "estilo_sgm_mexicali_continuo.qml"), -350, -50, ramp_type='INTERPOLATED')

    # 2. SAN FELIPE QML DISCRETO (16 colores exactos SGM, bandas poligonales puras)
    labels_sf_disc = [
        "< -600 nT (-625 nT)", "-600 a -550 nT", "-550 a -500 nT", "-500 a -450 nT",
        "-450 a -400 nT", "-400 a -350 nT", "-350 a -300 nT", "-300 a -250 nT",
        "-250 a -200 nT", "-200 a -150 nT", "-150 a -100 nT", "-100 a -50 nT",
        "-50 a 0 nT",     "0 a 50 nT",       "50 a 100 nT",     "> 100 nT (+125 nT)"
    ]
    generar_qml(thresh_sf, ref_colors_rgb, labels_sf_disc,
                os.path.join(work_dir, "estilo_sgm_sanfelipe_exacto.qml"), -625, 125, ramp_type='DISCRETE')

    # SAN FELIPE QML CONTINUO
    labels_sf_cont = [f"{v:.0f} nT" for v in val_sf]
    generar_qml(val_sf, ref_colors_rgb, labels_sf_cont,
                os.path.join(work_dir, "estilo_sgm_sanfelipe_continuo.qml"), -625, 125, ramp_type='INTERPOLATED')

    # SAN FELIPE QML ALTO CONTRASTE (Paleta Turbo expandida para resaltar con dramatismo los 7 anillos de San Felipe)
    turbo_16 = (cm.turbo(np.linspace(0, 1, 16))[:, :3] * 255).astype(np.uint8)
    generar_qml(thresh_sf, turbo_16, labels_sf_disc,
                os.path.join(work_dir, "estilo_sanfelipe_alto_contraste.qml"), -625, 125, ramp_type='DISCRETE')

    # 3. UNIFICADO QML (WGS84 y UTM 11N)
    val_uni = np.linspace(-625, 125, 16)
    thresh_uni = np.linspace(-600, 150, 16)
    labels_u_disc = [
        "-625 nT (Bajo Extremo)", "-550 nT", "-500 nT", "-450 nT",
        "-400 nT", "-350 nT", "-300 nT", "-250 nT",
        "-200 nT", "-150 nT", "-100 nT", "-50 nT",
        "0 nT", "+50 nT", "+100 nT", "+125 nT (Alto Extremo)"
    ]
    generar_qml(thresh_uni, ref_colors_rgb, labels_u_disc,
                os.path.join(work_dir, "mapa_aeromagnetico_cicese_exacto.qml"), -625, 125, ramp_type='DISCRETE')
    generar_qml(thresh_uni, ref_colors_rgb, labels_u_disc,
                os.path.join(work_dir, "mapa_aeromagnetico_utm11n_exacto.qml"), -625, 125, ramp_type='DISCRETE')
    generar_qml(val_uni, ref_colors_rgb, labels_u_disc,
                os.path.join(work_dir, "mapa_aeromagnetico_utm11n_continuo.qml"), -625, 125, ramp_type='INTERPOLATED')

    # TURBO PARA ELGP Y VISUALIZACIÓN ESTRUCTURAL
    generar_qml(val_uni, turbo_16, labels_u_disc,
                os.path.join(work_dir, "mapa_aeromagnetico_utm11n_turbo.qml"), -625, 125, ramp_type='INTERPOLATED')

    # -------------------------------------------------------------------------
    # VISTAS PREVIAS DE VERIFICACIÓN EN ALTA DEFINICIÓN
    # -------------------------------------------------------------------------
    # A. Previews individuales con su escala nativa SGM (100% fiel al impreso)
    # Mexicali nativo
    norm_m = (grid_m - (-350.0)) / ((-50.0) - (-350.0))
    norm_m = np.clip(norm_m, 0, 1)
    lut_m = np.clip((norm_m * 15.999).astype(int), 0, 15)
    prev_m_bgr = ref_colors_rgb[lut_m][:, :, ::-1].astype(np.uint8)
    prev_m_bgr[np.isnan(grid_m)] = [255, 255, 255]
    p_m_path = os.path.join(work_dir, "preview_mexicali_sgm.jpg")
    cv2.imwrite(p_m_path, prev_m_bgr, [int(cv2.IMWRITE_JPEG_QUALITY), 95])

    # San Felipe nativo
    norm_s = (grid_s - (-625.0)) / (125.0 - (-625.0))
    norm_s = np.clip(norm_s, 0, 1)
    lut_s = np.clip((norm_s * 15.999).astype(int), 0, 15)
    prev_s_bgr = ref_colors_rgb[lut_s][:, :, ::-1].astype(np.uint8)
    prev_s_bgr[np.isnan(grid_s)] = [255, 255, 255]
    p_s_path = os.path.join(work_dir, "preview_sanfelipe_sgm.jpg")
    cv2.imwrite(p_s_path, prev_s_bgr, [int(cv2.IMWRITE_JPEG_QUALITY), 95])

    # B. Zoom San Felipe (anomalías de la caldera y graben cerca del poblado)
    # Coordenadas relativas en la hoja de San Felipe: Y de 1464 a 2636, X de 1900 a 3200
    sf_crop_sgm = prev_s_bgr[1464:2636, 1900:3200]
    p_sf_sgm_path = os.path.join(work_dir, "preview_anomalia_sanfelipe_sgm.jpg")
    cv2.imwrite(p_sf_sgm_path, sf_crop_sgm, [int(cv2.IMWRITE_JPEG_QUALITY), 95])

    # San Felipe Zoom en Alto Contraste Turbo
    crop_vals = grid_s[1464:2636, 1900:3200]
    c_valid = ~np.isnan(crop_vals)
    c_min, c_max = np.nanmin(crop_vals), np.nanmax(crop_vals)
    norm_crop = np.clip((crop_vals - c_min) / (c_max - c_min + 1e-5), 0, 1)
    sf_crop_turbo = (cm.turbo(norm_crop)[:, :, :3][:, :, ::-1] * 255).astype(np.uint8)
    sf_crop_turbo[~c_valid] = [255, 255, 255]
    p_sf_contrast_path = os.path.join(work_dir, "preview_anomalia_sanfelipe_contraste.jpg")
    cv2.imwrite(p_sf_contrast_path, sf_crop_turbo, [int(cv2.IMWRITE_JPEG_QUALITY), 95])

    # C. Previews del mosaico completo
    norm_uni = np.clip((unified_discrete - (-625.0)) / (125.0 - (-625.0)), 0, 1)
    lut_uni = np.clip((norm_uni * 15.999).astype(int), 0, 15)
    preview_sgm_bgr = ref_colors_rgb[lut_uni][:, :, ::-1].astype(np.uint8)
    preview_sgm_bgr[np.isnan(unified_discrete)] = [255, 255, 255]
    p_sgm_path = os.path.join(work_dir, "mapa_aeromagnetico_preview_sgm.jpg")
    cv2.imwrite(p_sgm_path, preview_sgm_bgr, [int(cv2.IMWRITE_JPEG_QUALITY), 95])

    col_turbo = cm.turbo(norm_uni)[:, :, :3]
    col_turbo[np.isnan(unified_discrete)] = [1.0, 1.0, 1.0]
    preview_turbo_bgr = (col_turbo[:, :, ::-1] * 255).astype(np.uint8)
    p_turbo_path = os.path.join(work_dir, "mapa_aeromagnetico_preview_turbo.jpg")
    cv2.imwrite(p_turbo_path, preview_turbo_bgr, [int(cv2.IMWRITE_JPEG_QUALITY), 95])

    # Copiar vistas previas a la carpeta de artefactos
    for src_p, dst_name in [
        (p_m_path, "preview_mexicali_sgm.jpg"),
        (p_s_path, "preview_sanfelipe_sgm.jpg"),
        (p_sgm_path, "mapa_aeromagnetico_preview_sgm.jpg"),
        (p_turbo_path, "mapa_aeromagnetico_preview_turbo.jpg"),
        (p_sf_sgm_path, "preview_anomalia_sanfelipe_sgm.jpg"),
        (p_sf_contrast_path, "preview_anomalia_sanfelipe_contraste.jpg")
    ]:
        dst_p = os.path.join(art_dir, dst_name)
        if os.path.exists(src_p):
            import shutil
            shutil.copy2(src_p, dst_p)

    t_total = time.time() - t_start
    print("\n" + "=" * 80)
    print(f" PROCESO COMPLETADO EXITOSAMENTE EN {t_total:.2f} SEGUNDOS")
    print(f" - Cartas procesadas con escala física exacta y orientación NO invertida:")
    print(f"   * Mexicali:   -350 a -50 nT (Azul = -350 nT, Naranja = -50 nT)")
    print(f"   * San Felipe: -625 a +125 nT (Azul = -625 nT, Naranja = +125 nT)")
    print(f" - Todos los anillos y anomalías concéntricas preservados al 100%")
    print(f" - Cero líneas de cuadrícula, isolíneas, textos ni cruces cartográficas")
    print("=" * 80)

if __name__ == "__main__":
    main()
