import os
from osgeo import ogr
from .sql_generators import insert_geom_sql
import xml.etree.ElementTree as ET


ALLOWED_EXTENSIONS = {'zip'}


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[-1].lower() in ALLOWED_EXTENSIONS

def get_folders_or_document_elements(file_path, layers):
    tree = ET.parse(file_path)
    root = tree.getroot()

    name_space = './/{http://www.opengis.net/kml/2.2}'
    if layers > 1:
        root = root.findall(name_space + 'Folder')

    return root


def get_folder_or_document_styles(root):

    name_space = './/{http://www.opengis.net/kml/2.2}'
    styles = root.findall(name_space + 'Style')
    placemarks = root.findall(name_space + 'Placemark')



    style_table = {}
    for style in styles:
        id = style.attrib['id']
        style_table[id] = {
            'LineStyle': style.find(name_space + 'LineStyle').find(name_space + 'color').text,
            'PolyStyle': style.find(name_space + 'PolyStyle').find(name_space + 'color').text,
        }


    placemarks_styles = []
    for placemark in placemarks:
        id = placemark.attrib['id']
        style_url_id = placemark.find(name_space + 'styleUrl').text[1:]  # Removendo o hash do id

        placemarks_styles.append({
            id : {
                'LineStyle': style_table[style_url_id]['LineStyle'],
                'PolyStyle': style_table[style_url_id]['PolyStyle'],
            }

        })

    return placemarks_styles

def create_inserts(temp_folder, table_name, buffer) -> list:
    sql_inserts = []
    for filename in os.listdir(temp_folder):
        print("--> " + filename)

        driver = ogr.GetDriverByName('KML')
        datasource = driver.Open(temp_folder + '/' + filename)
        layers_count = datasource.GetLayerCount()
        folders = get_folders_or_document_elements(temp_folder + '/' + filename, layers_count)


        for i in range(layers_count):
            layer = datasource.GetLayerByIndex(i)
            feat_count = layer.GetFeatureCount()
            feat = layer.GetNextFeature()
            styles = get_folder_or_document_styles(folders[i])

            if len(styles) and len(styles):
                print(len(styles),len(styles)) #TODO: fazer checagem se features igual a placemarkers

            s = 0
            while feat:

                geometry = feat.geometry()
                if buffer:
                    geometry = geometry.Buffer(buffer)
                insert_statement = insert_geom_sql(geometry, buffer, filename, styles[s])

                sql_inserts.append(insert_statement)
                feat = layer.GetNextFeature()
                s += 1

    return '''
        insert into {0} (id_geoprocessamento, file_name, geom, style) 
        values {1} ;
    '''.format(table_name, ','.join(sql_inserts))


# TODO: implement styles importer