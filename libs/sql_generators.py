from django.contrib.gis.geos import GEOSGeometry
import json


def create_table_sql(table_name, temp):
    if temp:
        temp_table = 'temp'
    else:
        temp_table = ''
        table_name = 'sd_producao.' + table_name  # TODO: fix bug

    return '''create {1} table {0}
        (
            id_geoprocessamento varchar(255) not null,
            nm_cliente          varchar(255),
            geom                geometry
        );

        create index on {0} (id_geoprocessamento);
        create index on {0} (nm_cliente);

        '''.format(table_name, temp_table)


def insert_geom_sql(feat_json, filename_slug, buffer):
    geom = json.dumps(feat_json['geometry'])
    pnt = GEOSGeometry(geom)

    if buffer: #TODO: remover todos os inserts de nome do cliente e adicionar do nome do arquivo
        comando_sql = '''
        ('algar_mpe_{0}', 'ALGAR', ST_Buffer(ST_GeomFromText('{1}',4326)::geography, {2})::GEOMETRY) 
        '''
    else:
        comando_sql = '''
        ('regional_{0}', 'ALGAR', ST_GeomFromText('{1}',4326))
        '''

    return comando_sql.format(filename_slug, pnt, buffer)


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
