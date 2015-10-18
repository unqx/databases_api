import json
import datetime
from django.http import JsonResponse
from django.db import connection
from django.views.decorators.csrf import csrf_exempt
from dbproject.api.utils import get_user_by_email, get_user_by_id, get_forum_by_shortname, get_thread_by_id


@csrf_exempt
def thread_create(request):
    response = {}
    if not request.method == 'POST':
        return JsonResponse({
            'code': 2,
            'response': 'Method in not supported'
        })

    try:
        request_params = json.loads(request.body)

        forum = request_params.get('forum', None)
        title = request_params.get('title', None)
        user = request_params.get('user', None)
        message = request_params.get('message', None)
        slug = request_params.get('slug', None)
        date = request_params.get('date', None)

        is_deleted = request_params.get('isDeleted', False)
        if type(is_deleted) is not bool:
            return JsonResponse({
                'code': 3,
                'response': 'Wrong isDeleted parameter type'
            })

        if not 'isClosed' in request_params or not (forum and title and user and message and slug and date):
            return JsonResponse({
                'code': 3,
                'response': 'Missing field'
            })

        is_closed = request_params.get('isClosed')
        if type(is_closed) is not bool:
            return JsonResponse({
                'code': 3,
                'response': 'Wrong isClosed parameter type'
            })

        try:
            datetime.datetime.strptime(date, '%Y-%m-%d %H:%M:%S')
        except ValueError:
            return JsonResponse({
                'code': 3,
                'response': 'Wrong date format'
            })

        user_data = get_user_by_email(user)
        if not user_data:
            return JsonResponse({
                'code': 1,
                'response': 'User not found'
            })

        forum_data = get_forum_by_shortname(forum)
        if not forum_data:
            return JsonResponse({
                'code': 1,
                'response': 'Forum not found'
            })

        cursor = connection.cursor()

        sql_select_raw = "SELECT * FROM thread WHERE title = '{0}' AND forum_id = '{1}'"

        sql_select = sql_select_raw.format(title, forum_data[0])
        cursor.execute(sql_select)
        sql_response = cursor.fetchone()

        if sql_response:
            response = {
                'title': title,
                'forum': forum_data[4],
                'message': sql_response[6],
                'slug': sql_response[7],
                'isClosed': bool(sql_response[3]),
                'isDeleted': bool(sql_response[8]),
                'id': sql_response[0],
                'date': sql_response[5].strftime('%Y-%m-%d %H:%M:%S'),
                'user': get_user_by_id(sql_response[4])[2]

            }
            return JsonResponse({'code': 0, 'response': response})

        sql_insert_raw = "INSERT INTO thread VALUES (null, '{0}','{1}','{2}','{3}','{4}','{5}','{6}','{7}')"
        sql_insert = sql_insert_raw.format(forum_data[0], title, is_closed, user_data[0], date, message, slug, is_deleted)

        cursor.execute(sql_insert)

        response.update({
            'title': title,
            'forum': forum_data[4],
            'message': message,
            'slug': slug,
            'isClosed': is_closed,
            'isDeleted': is_deleted,
            'id': cursor.lastrowid,
            'date': date,
            'user': user_data[2]
        })

    except ValueError:
        return JsonResponse({
            'code': 3,
            'response': 'No JSON object could be decoded'
        })

    return JsonResponse({
        'code': 0,
        'response': response
    })


@csrf_exempt
def thread_subscribe(request):
    response = {}
    if not request.method == 'POST':
        return JsonResponse({
            'code': 2,
            'response': 'Method in not supported'
        })

    try:
        request_params = json.loads(request.body)

        user_email = request_params.get('user', None)
        thread_id = request_params.get('thread', None)

        if not (user_email and thread_id):
            return JsonResponse({
                'code': 3,
                'response': 'Missing field'
            })

        user_data = get_user_by_email(user_email)
        if not user_data:
            return JsonResponse({
                'code': 1,
                'response': 'User not found'
            })

        try:
            thread_id = int(thread_id)
        except ValueError:
            return JsonResponse({
                'code': 3,
                'response': 'Wrong thread id param'
            })

        thread_data = get_thread_by_id(thread_id)
        if not thread_data:
            return JsonResponse({
                'code': 1,
                'response': 'Thread not found'
            })

        cursor = connection.cursor()
        sql_raw = "INSERT IGNORE INTO subscriptions VALUES (null, '{0}', '{1}');"
        sql = sql_raw.format(thread_id, user_data[0])
        cursor.execute(sql)

        response.update({
            'user': user_data[2],
            'thread': thread_id,
        })

    except ValueError:
        return JsonResponse({
            'code': 3,
            'response': 'No JSON object could be decoded'
        })

    return JsonResponse({
        'code': 0,
        'response': response
    })


@csrf_exempt
def thread_unsubscribe(request):
    response = {}
    if not request.method == 'POST':
        return JsonResponse({
            'code': 2,
            'response': 'Method in not supported'
        })

    try:
        request_params = json.loads(request.body)

        user_email = request_params.get('user', None)
        thread_id = request_params.get('thread', None)

        if not (user_email and thread_id):
            return JsonResponse({
                'code': 3,
                'response': 'Missing field'
            })

        user_data = get_user_by_email(user_email)
        if not user_data:
            return JsonResponse({
                'code': 1,
                'response': 'User not found'
            })

        try:
            thread_id = int(thread_id)
        except ValueError:
            return JsonResponse({
                'code': 3,
                'response': 'Wrong thread id param'
            })

        thread_data = get_thread_by_id(thread_id)
        if not thread_data:
            return JsonResponse({
                'code': 1,
                'response': 'Thread not found'
            })

        cursor = connection.cursor()
        sql_raw = "DELETE FROM subscriptions WHERE thread_id = '{0}' AND user_id = '{1}';"
        sql = sql_raw.format(thread_id, user_data[0])
        cursor.execute(sql)

        response.update({
            'user': user_data[2],
            'thread': thread_id,
        })

    except ValueError:
        return JsonResponse({
            'code': 3,
            'response': 'No JSON object could be decoded'
        })

    return JsonResponse({
        'code': 0,
        'response': response
    })