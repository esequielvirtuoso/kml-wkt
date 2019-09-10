# from django.contrib.gis.geos import GEOSGeometry
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
        table_name = 'sd_processamentos.' + table_name

    return '''create {1} table {0}
        (
            id_geoprocessamento text,
            file_name           text,
            geom                geometry,
            style               json
        );

        create index on {0} (id_geoprocessamento);
        create index on {0} (file_name);

        '''.format(table_name, temp_table)


def insert_geom_sql(feat_json, buffer, filename, style):
    filename_slug = slugify(filename)

    comando_sql = "('{0}', '{1}', ST_GeomFromText('{2}',4326), '{4}')\n"
    print(style)
    return comando_sql.format(filename_slug, filename, feat_json.ExportToWkt(), buffer, json.dumps(style))


def final_insert_sql(table_name, aggregate):
    union, group = '', ''

    if aggregate:
        union = 'st_union(geom)'
        group = 'group by id_geoprocessamento, file_name'
    return '''
        insert into sd_processamentos.{0} (id_geoprocessamento, file_name, geom, style) 
        select id_geoprocessamento id_geoprocessamento, file_name file_name,  {1} geom, style style 
        from {0} {2};
    '''.format(table_name, union, group)
