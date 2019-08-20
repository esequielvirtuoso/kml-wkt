from django.contrib.gis.geos import GEOSGeometry
import json, unidecode, re

# TODO: check out the error: OGC WKT expected, EWKT provided - use GeomFromEWKT() for this that generates on inserts


def slugify(text):
    text = unidecode.unidecode(text).lower()
    return re.sub(r'[\W_]+', '_', text)

def create_table_sql(table_name, temp):
    if temp:
        temp_table = 'temp'
    else:
        temp_table = ''
        table_name = 'sd_producao.' + table_name

    return '''create {1} table {0}
        (
            id_geoprocessamento varchar(255) not null,
            file_name          varchar(255),
            geom                geometry
        );

        create index on {0} (id_geoprocessamento);
        create index on {0} (file_name);

        '''.format(table_name, temp_table)


def insert_geom_sql(feat_json, buffer, filename):
    filename_slug = slugify(filename)
    geom = json.dumps(feat_json['geometry'])
    pnt = GEOSGeometry(geom)

    if buffer:
        comando_sql = "('{0}', '{1}', ST_Buffer(ST_GeomFromText('{2}',4326)::geography, {3})::GEOMETRY)"
    else:
        comando_sql = "('regional_{0}', '{1}', ST_GeomFromText('{2}',4326))"

    return comando_sql.format(filename_slug, filename, pnt, buffer)


def final_insert_sql(table_name, aggregate):
    union, group = '', ''

    if aggregate:
        union = 'st_union(geom)'
        group = 'group by id_geoprocessamento'
    return '''
        insert into sd_producao.{0} (id_geoprocessamento, file_name, geom) 
        select id_geoprocessamento id_geoprocessamento, file_name file_name,  {1} geom 
        from {0} {2};
    '''.format(table_name, union, group)
