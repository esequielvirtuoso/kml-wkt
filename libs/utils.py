import unidecode, re, json, os, shutil, zipfile
from osgeo import ogr
from .models import create_sql


def slugify(text):
    text = unidecode.unidecode(text).lower()
    return re.sub(r'[\W_]+', '_', text)


def fix_multigeometric(feat_json, table_name, filename_slug, buffer):
    polygons_coordinates = []
    linestrings_coordinates = []
    geometries = feat_json['geometry']['geometries']

    for shape in geometries:
        if shape['type'] == 'LineString':
            linestrings_coordinates.append(shape['coordinates'])
        elif shape['type'] == 'Polygon':
            polygons_coordinates.append(shape['coordinates'])

    del feat_json['geometry']['geometries']

    if len(polygons_coordinates):
        feat_json['geometry']['type'] = 'MultiPolygon'
        feat_json['geometry']['coordinates'] = polygons_coordinates
        return create_sql(feat_json, table_name, filename_slug, buffer)
    if len(linestrings_coordinates):
        feat_json['geometry']['type'] = 'MultiLineString'
        feat_json['geometry']['coordinates'] = linestrings_coordinates
        return create_sql(feat_json, table_name, filename_slug, buffer)

def create_inserts(temp_folder, table_name, buffer) -> list:
    sql_inserts = []
    for filename in os.listdir(temp_folder):
        filename_slug = slugify(filename.lower().split(".")[0].replace(" ", ""))
        print("--> " + filename_slug)
        # Read XML file into python
        driver = ogr.GetDriverByName('KML')
        datasource = driver.Open(temp_folder + '/' + filename)

        layers_count = datasource.GetLayerCount()

        for i in range(layers_count):
            layer = datasource.GetLayerByIndex(i)
            feat = layer.GetNextFeature()

            while feat:
                feat_json = json.loads(feat.ExportToJson())

                if 'geometries' in feat_json['geometry']:
                    insert_statement = fix_multigeometric(feat_json, table_name, filename_slug, buffer)
                else:
                    insert_statement = create_sql(feat_json, table_name, filename_slug, buffer)

                sql_inserts.append(insert_statement)

                feat = layer.GetNextFeature()
    return sql_inserts


def create_dir(dir_path):
    if not os.path.exists(dir_path):
        os.mkdir(dir_path)
def remove_dir(dir_path):
    if os.path.exists(dir_path):
        shutil.rmtree(dir_path)


def extract_kmz(upload_folder, temp_folder):
    for filename in os.listdir(upload_folder):
        if filename.lower().endswith(".kmz"):
            with zipfile.ZipFile(os.path.join(upload_folder, filename), 'r') as zip_ref:
                zip_ref.extractall(temp_folder)
                shutil.move(temp_folder + '/doc.kml', temp_folder + '/' + filename.split('.')[0] + '.kml')
        elif filename.lower().endswith(".kml"):
            shutil.copy(os.path.join(upload_folder, filename), os.path.join(temp_folder, filename))

def create_dir_structure(app, folder_name_hash_id):
    upload_folder = './temp/' + folder_name_hash_id + '/' + app.config['UPLOAD_FOLDER']
    temp_folder = './temp/' + folder_name_hash_id + '/' + app.config['TEMP_FOLDER']
    out_folder = './temp/' + folder_name_hash_id + '/' + app.config['OUT_FOLDER']
    create_dir('./temp/' + folder_name_hash_id)
    create_dir(upload_folder)
    create_dir(temp_folder)
    create_dir(out_folder)

