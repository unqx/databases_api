import json
from django.http import JsonResponse
from django.db import connection
from django.views.decorators.csrf import csrf_exempt
from dbproject.api.utils import get_user_by_email, get_user_by_id


@csrf_exempt
def forum_create(request):
    response = {}
    if request.method == 'POST':
        try:
            data = json.loads(request.body)

            name = data.get('name', None)
            short_name = data.get('short_name', None)
            user = data.get('user', None)

            if not (name and user and short_name):
                response.update({
                    'code': 3,
                    'response': 'Missing field'
                })
                return JsonResponse(response)

            cursor = connection.cursor()

            user_data = get_user_by_email(user)
            if not user_data:
                response.update({
                    'code': 1,
                    'response': 'User not found'
                })
                return JsonResponse(response)

            sql_select_raw = "SELECT id, owner_id FROM forum WHERE name = '{0}'"

            sql = sql_select_raw.format(name)
            cursor.execute(sql)

            sql_response = cursor.fetchone()
            if sql_response:
                response['code'] = 0
                response['response'] = {
                    'id': sql_response[0],
                    'name': name,
                    'short_name': short_name,
                    'user': get_user_by_id(sql_response[1])[2]
                }
                return JsonResponse(response)


            sql_insert_raw = "INSERT INTO forum (name, short_name, owner_id) VALUES ('{0}', '{1}', '{2}');"

            sql = sql_insert_raw.format(name, short_name, user_data[0])
            cursor.execute(sql)

            response['code'] = 0
            response['response'] = {
                'id': cursor.lastrowid,
                'name': name,
                'short_name': short_name,
                'user': user
            }

        except ValueError:
            response = {
                'code': 3,
                'response': 'No JSON object could be decoded'
            }

    else:
        response.update({
            'code': 2,
            'response': "Method is unsupported"
        })
    return JsonResponse(response)