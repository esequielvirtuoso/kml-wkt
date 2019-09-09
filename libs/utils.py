import os
from osgeo import ogr
from .sql_generators import insert_geom_sql
import re

ALLOWED_EXTENSIONS = {'zip'}


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[-1].lower() in ALLOWED_EXTENSIONS

def get_styles(file_path):
    styles = []

    with open(file_path, 'r') as f:
        for line in f:
            if line.find('<styleUrl>') != -1:
                styleName = re.findall(r'>(.+)<', line)[0]
                styles.append(styleName)
    return styles

def create_inserts(temp_folder, table_name, buffer) -> list:
    sql_inserts = []
    for filename in os.listdir(temp_folder):
        print("--> " + filename)

        driver = ogr.GetDriverByName('KML')
        datasource = driver.Open(temp_folder + '/' + filename)
        styles = get_styles(temp_folder + '/' + filename)
        layers_count = datasource.GetLayerCount()

        for i in range(layers_count):
            layer = datasource.GetLayerByIndex(i)
            feat_count = layer.GetFeatureCount()
            feat = layer.GetNextFeature()

            o = 0
            while feat:

                geometry = feat.geometry()
                if buffer:
                    geometry = geometry.Buffer(buffer)
                insert_statement = insert_geom_sql(geometry, buffer, filename, styles[o])

                sql_inserts.append(insert_statement)
                feat = layer.GetNextFeature()
                o += 1

    return '''
        insert into {0} (id_geoprocessamento, file_name, geom, style) 
        values {1} ;
    '''.format(table_name, ','.join(sql_inserts))
