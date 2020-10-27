# $ ./manage.py shell < myscript.py
# You could also do:

# $ ./manage.py shell
# ...
# >>> execfile('myscript.py')
# For python3 you would need to use

#>>> exec(open('myscript.py').read())
#
#
from django.db import connection
from metax_api.models.catalog_record import CatalogRecord as CR


syke_catalog = 5

sql_get_syke_deprecated = '''
    select id
    from metax_api_catalogrecord
    where research_dataset->'other_identifier'->>'notation' <> ''
        and metax_api_catalogrecord.data_catalog_id = %d
'''

with connection.cursor() as cr:
    cr.execute(sql_get_syke_deprecated, [syke_catalog])
    records = cr.fetchall() # [ v[0] for v in cr.fetchall() ]

records = CR.objects.filter(pk__in=[records])

for record in records:
    record.delete()