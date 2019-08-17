from django.contrib.gis.geos import GEOSGeometry
import json


def create_table_sql(table_name, temp):
    temp_table = 'sd_producao.' + table_name
    create_index = ''
    if temp:
        temp_table = 'temp'
    return '''create {1} table {0}
        (
            id_geoprocessamento varchar(255) not null,
            nm_cliente          varchar(255),
            geom                geometry
        );

        create index on {0} (id_geoprocessamento);
        create index on {0} (nm_cliente);

        '''.format(table_name, temp_table, create_index)


def insert_geom_sql(feat_json, table_name, filename_slug, buffer):
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


def final_insert_sql(table_name, aggregate):
    union, group = '', ''

    if aggregate:
        union = 'st_union(geom)'
        group = 'group by nm_cliente, id_geoprocessamento'
    return '''
        insert into sd_producao.{0} (id_geoprocessamento, nm_cliente, geom) 
        select id_geoprocessamento id_geoprocessamento, nm_cliente nm_cliente,  {1} geom 
        from {0} {2};
    '''.format(table_name, union, group)
