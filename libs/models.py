from django.contrib.gis.geos import GEOSGeometry
import json


def create_sql(feat_json, table_name, filename_slug, buffer):
    geom = json.dumps(feat_json['geometry'])
    pnt = GEOSGeometry(geom)

    if buffer:
        comando_sql = '''
        insert into {0} (id_geoprocessamento, nm_cliente, geom) 
        values ('algar_mpe_{1}', 'ALGAR', ST_Buffer(ST_GeomFromText('{2}',4326)::geography, {3})::GEOMETRY);\n
        '''
    else:
        comando_sql = '''
        insert into {0} (id_geoprocessamento, nm_cliente, geom)
        values ('regional_{1}', 'ALGAR', ST_GeomFromText('{2}',4326));\n
        '''

    return comando_sql.format(table_name, filename_slug, pnt, buffer)


def create_table_statement(table_name, temp):
    temp_table = ''
    primary_key = ''
    create_index = ''
    if temp:
        temp_table = 'temp'
        create_index = 'create index on {0} (id_geoprocessamento);'.format(table_name)
    else:
        table_name = 'sd_producao.' + table_name
        primary_key = 'primary key'
    return '''create {1} table {0}
        (
            id_geoprocessamento varchar(255) not null {2},
            nm_cliente          varchar(255),
            geom                geometry
        );

        {3}
        create index on {0} (nm_cliente);

        '''.format(table_name, temp_table, primary_key, create_index)


def create_table_agregator(table_name):
    return '''
        insert into sd_producao.{0} (id_geoprocessamento, nm_cliente, geom) 
        select id_geoprocessamento id_geoprocessamento, nm_cliente nm_cliente,  st_union(geom) geom 
        from {0} group by nm_cliente, id_geoprocessamento;
    '''.format(table_name)
