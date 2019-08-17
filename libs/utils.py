import unidecode, re, json, os, shutil, zipfile
from osgeo import ogr
from .sql_generators import insert_geom_sql

ALLOWED_EXTENSIONS = {'zip'}


def slugify(text):
    text = unidecode.unidecode(text).lower()
    return re.sub(r'[\W_]+', '_', text)


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[-1].lower() in ALLOWED_EXTENSIONS


def fix_multigeometric(feat_json, filename_slug, buffer):
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
        return insert_geom_sql(feat_json, filename_slug, buffer)
    if len(linestrings_coordinates):
        feat_json['geometry']['type'] = 'MultiLineString'
        feat_json['geometry']['coordinates'] = linestrings_coordinates
        return insert_geom_sql(feat_json, filename_slug, buffer)


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
                    insert_statement = fix_multigeometric(feat_json, filename_slug, buffer)
                else:
                    insert_statement = insert_geom_sql(feat_json, filename_slug, buffer)

                sql_inserts.append(insert_statement)

                feat = layer.GetNextFeature()

    return '''
        insert into {0} (id_geoprocessamento, nm_cliente, geom) 
        values {1} ;
    '''.format(table_name,','.join(sql_inserts))

