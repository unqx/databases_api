import json
from django.http import HttpResponse
from django.db import connection
from django.views.decorators.csrf import csrf_exempt


@csrf_exempt
def forum_create(request):
    response = {}
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            cursor = connection.cursor()

            sql_raw = "INSERT INTO forum (name, short_name) VALUES ('{0}', '{1}');"

            sql = sql_raw.format(data['name'], data['short_name'])
            cursor.execute(sql)

            row = cursor.fetchone()
            print row
            response['code'] = 0

        except ValueError:
            response.update({
                'code': 2,
                'error': 'No JSON object could be decoded'
            })


    else:
        response.update({
            'code': 3,
            'error': "Method is unsupported"
        })
    return HttpResponse(json.dumps(response), content_type='application/json')