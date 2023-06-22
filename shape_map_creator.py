import os
import pandas as pd
import geopandas as gpd
from shapely.geometry import Polygon
from pykml import parser
from dotenv import load_dotenv

load_dotenv()

# read the GeoJSON file
gdf = gpd.read_file(
    f"{os.getenv('geojson_route')}/mapas/LIMITES Y ORGANIZACION TERRITORIAL DEL ESTADO 17012023/ORGANIZACION_TERRITORIAL_PARROQUIAL.shp")
# create a boolean mask indicating which row have 'QUTO' in the 'DPA_DESPAR' column
mask0 = (gdf['DPA_DESPAR'] == 'QUITO')
# use the boolean mask to drop the row where 'QUITO' is in the 'DPA_DESPAR' column
gdf = gdf[~mask0]
gdf = gdf.to_crs(4326)

# Read in the KML file using pykml
kml_path1 = f"{os.getenv('geojson_route')}/mapas/Quito DM.kml"
with open(kml_path1) as f:
    kml_data = f.read().encode('utf-8')
    root = parser.fromstring(kml_data)

# Extract coordinates from KML
ns = {'kml': 'http://www.opengis.net/kml/2.2'}
coords = []
for pm in root.xpath('//kml:Placemark/kml:Polygon/kml:outerBoundaryIs/kml:LinearRing/kml:coordinates', namespaces=ns):
    polygon_coords = []
    for co in pm.text.split():
        x, y, *_ = map(float, co.split(','))
        polygon_coords.append((x, y))
    coords.append(Polygon(polygon_coords))

# Create GeoDataFrame with desired columns
gdf_quito = gpd.GeoDataFrame(
    {'DPA_DESPAR': [despro.text for despro in root.xpath('//kml:Placemark/kml:name', namespaces=ns)],
     'DPA_CANTON': '1701', 'DPA_DESCAN': 'DISTRITO METROPOLITANO DE QUITO', 'DPA_PROVIN': '17',
     'DPA_DESPRO': 'PICHINCHA', 'DPA_ANIO': '2023', 'fcode': 'HA004', 'geometry': gpd.GeoSeries(coords)})
gdf_quito['DPA_DESPAR'] = gdf_quito['DPA_DESPAR'].str.upper()
gdf_quito['DPA_DESPAR'] = gdf_quito['DPA_DESPAR'].str.replace('INIAQUITO', 'IÑAQUITO')
gdf_quito['DPA_DESPAR'] = gdf_quito['DPA_DESPAR'].str.replace('S.ISIDRO DEL INC', 'SAN ISIDRO DEL INCA')

# create a boolean mask indicating which row have 'ALANGASI', ... in the 'DPA_DESPAR' column
mask1 = (gdf_quito['DPA_DESPAR'] == 'ALANGASI') | (gdf_quito['DPA_DESPAR'] == 'AMAGUANIA') | (
        gdf_quito['DPA_DESPAR'] == 'CALACALI') | (gdf_quito['DPA_DESPAR'] == 'CALDERON') | (
                gdf_quito['DPA_DESPAR'] == 'CUMBAYA') | (gdf_quito['DPA_DESPAR'] == 'NAYON') | (
                gdf_quito['DPA_DESPAR'] == 'NONO') | (gdf_quito['DPA_DESPAR'] == 'PUELLARO') | (
                gdf_quito['DPA_DESPAR'] == 'YARUQUI') | (gdf_quito['DPA_DESPAR'] == 'ZAMBIZA') | (
                gdf_quito['DPA_DESPAR'] == 'PACTO') | (gdf_quito['DPA_DESPAR'] == 'GUALEA') | (
                gdf_quito['DPA_DESPAR'] == 'NANEGALITO') | (gdf_quito['DPA_DESPAR'] == 'NANEGAL') | (
                gdf_quito['DPA_DESPAR'] == 'S.JOSE DE MINAS') | (gdf_quito['DPA_DESPAR'] == 'ATAHUALPA') | (
                gdf_quito['DPA_DESPAR'] == 'CHAVEZPAMBA') | (gdf_quito['DPA_DESPAR'] == 'PERUCHO') | (
                gdf_quito['DPA_DESPAR'] == 'SAN ANTONIO') | (gdf_quito['DPA_DESPAR'] == 'GUAYLLABAMBA') | (
                gdf_quito['DPA_DESPAR'] == 'EL QUINCHE') | (gdf_quito['DPA_DESPAR'] == 'CHECA') | (
                gdf_quito['DPA_DESPAR'] == 'TABABELA') | (gdf_quito['DPA_DESPAR'] == 'PUEMBO') | (
                gdf_quito['DPA_DESPAR'] == 'LLOA') | (gdf_quito['DPA_DESPAR'] == 'LLANO CHICO') | (
                gdf_quito['DPA_DESPAR'] == 'TUMBACO') | (gdf_quito['DPA_DESPAR'] == 'GUANGOPOLO') | (
                gdf_quito['DPA_DESPAR'] == 'LA MERCED') | (gdf_quito['DPA_DESPAR'] == 'PINTAG') | (
                gdf_quito['DPA_DESPAR'] == 'CONOCOTO') | (gdf_quito['DPA_DESPAR'] == 'PIFO') | (
                gdf_quito['DPA_DESPAR'] == 'POMASQUI')

# use the boolean mask to drop the rows where 'ALANGASI', ... in the 'DPA_DESPAR' column
gdf_quito = gdf_quito[~mask1]

# Dissolve on DPA_DESPAR to combine all polygons within each district
gdf_quito = gdf_quito.dissolve(by='DPA_DESPAR')

# Reorder columns and reset index
gdf_quito = gdf_quito.reset_index().reindex(
    columns=['DPA_DESPAR', 'DPA_CANTON', 'DPA_DESCAN', 'DPA_PROVIN', 'DPA_DESPRO', 'DPA_ANIO', 'fcode', 'geometry'])

# Set CRS to EPSG:4326
gdf_quito.crs = 'EPSG:4326'

# Read in the KML file using pykml
kml_path2 = f"{os.getenv('geojson_route')}/mapas/Esmeraldas 2019.kml"
with open(kml_path2) as f:
    kml_data = f.read().encode('utf-8')
    root = parser.fromstring(kml_data)

# Extract coordinates from KML
ns = {'kml': 'http://www.opengis.net/kml/2.2'}
coords = []
for pm in root.xpath('//kml:Placemark/kml:Polygon/kml:outerBoundaryIs/kml:LinearRing/kml:coordinates', namespaces=ns):
    polygon_coords = []
    for co in pm.text.split():
        x, y, *_ = map(float, co.split(','))
        polygon_coords.append((x, y))
    coords.append(Polygon(polygon_coords))

# Create GeoDataFrame with desired columns
gdf_esm = gpd.GeoDataFrame(
    {'DPA_DESPAR': [despro.text for despro in root.xpath('//kml:Placemark/kml:name', namespaces=ns)],
     'DPA_CANTON': '0801', 'DPA_DESCAN': 'ESMERALDAS', 'DPA_PROVIN': '08', 'DPA_DESPRO': 'ESMERALDAS', 'DPA_ANIO': 2023,
     'fcode': 'HA004', 'geometry': gpd.GeoSeries(coords)})
gdf_esm['DPA_DESPAR'] = gdf_esm['DPA_DESPAR'].str.upper()
gdf_esm['DPA_DESPAR'] = gdf_esm['DPA_DESPAR'].str.replace('ESM - PARROQUIA ', '')
gdf_esm['DPA_DESPAR'] = gdf_esm['DPA_DESPAR'].str.replace('ESMERALDAS', 'PARROQUIA ESMERALDAS')

# Dissolve on DPA_DESPAR to combine all polygons within each district
gdf_esm = gdf_esm.dissolve(by='DPA_DESPAR')

# Reorder columns and reset index
gdf_esm = gdf_esm.reset_index().reindex(
    columns=['DPA_DESPAR', 'DPA_CANTON', 'DPA_DESCAN', 'DPA_PROVIN', 'DPA_DESPRO', 'DPA_ANIO', 'fcode', 'geometry'])

# Set CRS to EPSG:4326
gdf_esm.crs = 'EPSG:4326'

# Read in the KML file using pykml
kml_path3 = f"{os.getenv('geojson_route')}/mapas/Ibarra Parroquias urbanas.kml"
with open(kml_path3) as f:
    kml_data = f.read().encode('utf-8')
    root = parser.fromstring(kml_data)

# Extract coordinates from KML
ns = {'kml': 'http://www.opengis.net/kml/2.2'}
coords = []
for pm in root.xpath('//kml:Placemark/kml:Polygon/kml:outerBoundaryIs/kml:LinearRing/kml:coordinates', namespaces=ns):
    polygon_coords = []
    for co in pm.text.split():
        x, y, *_ = map(float, co.split(','))
        polygon_coords.append((x, y))
    coords.append(Polygon(polygon_coords))

# Create GeoDataFrame with desired columns
gdf_imb = gpd.GeoDataFrame(
    {'DPA_DESPAR': [despro.text for despro in root.xpath('//kml:Placemark/kml:name', namespaces=ns)],
     'DPA_CANTON': '1001', 'DPA_DESCAN': 'IBARRA', 'DPA_PROVIN': '10', 'DPA_DESPRO': 'IMBABURA', 'DPA_ANIO': 2023,
     'fcode': 'HA004', 'geometry': gpd.GeoSeries(coords)})
gdf_imb['DPA_DESPAR'] = gdf_imb['DPA_DESPAR'].str.upper()

# Dissolve on DPA_DESPAR to combine all polygons within each district
gdf_imb = gdf_imb.dissolve(by='DPA_DESPAR')

# Reorder columns and reset index
gdf_imb = gdf_imb.reset_index().reindex(
    columns=['DPA_DESPAR', 'DPA_CANTON', 'DPA_DESCAN', 'DPA_PROVIN', 'DPA_DESPRO', 'DPA_ANIO', 'fcode', 'geometry'])

# Set CRS to EPSG:4326
gdf_imb.crs = 'EPSG:4326'

# Read in the KML file using pykml
kml_path4 = f"{os.getenv('geojson_route')}/mapas/Cayambe Parroquias.kml"
with open(kml_path4) as f:
    kml_data = f.read().encode('utf-8')
    root = parser.fromstring(kml_data)

# Extract coordinates from KML
ns = {'kml': 'http://www.opengis.net/kml/2.2'}
coords = []
for pm in root.xpath('//kml:Placemark/kml:Polygon/kml:outerBoundaryIs/kml:LinearRing/kml:coordinates', namespaces=ns):
    polygon_coords = []
    for co in pm.text.split():
        x, y, *_ = map(float, co.split(','))
        polygon_coords.append((x, y))
    coords.append(Polygon(polygon_coords))

# Create GeoDataFrame with desired columns
gdf_cay = gpd.GeoDataFrame(
    {'DPA_DESPAR': [despro.text for despro in root.xpath('//kml:Placemark/kml:name', namespaces=ns)],
     'DPA_CANTON': '1702', 'DPA_DESCAN': 'CAYAMBE', 'DPA_PROVIN': '17', 'DPA_DESPRO': 'PICHINCHA', 'DPA_ANIO': 2023,
     'fcode': 'HA004', 'geometry': gpd.GeoSeries(coords)})
gdf_cay['DPA_DESPAR'] = gdf_cay['DPA_DESPAR'].str.upper()

mask3 = (gdf_cay['DPA_DESPAR'] == 'JUAN MONTALVO')
gdf_cay = gdf_cay[mask3]

# Dissolve on DPA_DESPAR to combine all polygons within each district
gdf_cay = gdf_cay.dissolve(by='DPA_DESPAR')

# Reorder columns and reset index
gdf_cay = gdf_cay.reset_index().reindex(
    columns=['DPA_DESPAR', 'DPA_CANTON', 'DPA_DESCAN', 'DPA_PROVIN', 'DPA_DESPRO', 'DPA_ANIO', 'fcode', 'geometry'])

# Set CRS to EPSG:4326
gdf_cay.crs = 'EPSG:4326'

# Read in the KML file using pykml
kml_path5 = f"{os.getenv('geojson_route')}/mapas/Rumiñahui 2018.kml"
with open(kml_path5) as f:
    kml_data = f.read().encode('utf-8')
    root = parser.fromstring(kml_data)

# Extract coordinates from KML
ns = {'kml': 'http://www.opengis.net/kml/2.2'}
coords = []
for pm in root.xpath('//kml:Placemark/kml:Polygon/kml:outerBoundaryIs/kml:LinearRing/kml:coordinates', namespaces=ns):
    polygon_coords = []
    for co in pm.text.split():
        x, y, *_ = map(float, co.split(','))
        polygon_coords.append((x, y))
    coords.append(Polygon(polygon_coords))

# Create GeoDataFrame with desired columns
gdf_rum = gpd.GeoDataFrame(
    {'DPA_DESPAR': [despro.text for despro in root.xpath('//kml:Placemark/kml:name', namespaces=ns)],
     'DPA_CANTON': '1705', 'DPA_DESCAN': 'RUMIÑAHUI', 'DPA_PROVIN': '17', 'DPA_DESPRO': 'PICHINCHA', 'DPA_ANIO': 2023,
     'fcode': 'HA004', 'geometry': gpd.GeoSeries(coords)})
gdf_rum['DPA_DESPAR'] = gdf_rum['DPA_DESPAR'].str.upper()
gdf_rum['DPA_DESPAR'] = gdf_rum['DPA_DESPAR'].str.replace(' - RUMIÑAHUI', '')

mask4 = (gdf_rum['DPA_DESPAR'] == 'SANGOLQUÍ') | (gdf_rum['DPA_DESPAR'] == 'COTOGCHOA') | (
        gdf_rum['DPA_DESPAR'] == 'RUMIPAMBA')

gdf_rum = gdf_rum[~mask4]

# Dissolve on DPA_DESPAR to combine all polygons within each district
gdf_rum = gdf_rum.dissolve(by='DPA_DESPAR')

# Reorder columns and reset index
gdf_rum = gdf_rum.reset_index().reindex(
    columns=['DPA_DESPAR', 'DPA_CANTON', 'DPA_DESCAN', 'DPA_PROVIN', 'DPA_DESPRO', 'DPA_ANIO', 'fcode', 'geometry'])

# Set CRS to EPSG:4326
gdf_rum.crs = 'EPSG:4326'

# Append the new GeoDataFrame to the existing one
gdf = pd.concat([gdf, gdf_quito, gdf_esm, gdf_imb, gdf_cay, gdf_rum], ignore_index=True)
gdf = gdf.sort_values(['DPA_DESPRO', 'DPA_DESCAN', 'DPA_DESPAR'])

# Remove the previous html file if already exist
if os.path.exists(f"{os.getenv('geojson_route')}/shapefile.shp"):
    os.remove(f"{os.getenv('geojson_route')}/shapefile.cpg")
    os.remove(f"{os.getenv('geojson_route')}/shapefile.dbf")
    os.remove(f"{os.getenv('geojson_route')}/shapefile.prj")
    os.remove(f"{os.getenv('geojson_route')}/shapefile.shp")
    os.remove(f"{os.getenv('geojson_route')}/shapefile.shx")

# save the final shape file
gdf.to_file(f"{os.getenv('geojson_route')}/shapefile.shp", driver='ESRI Shapefile')
