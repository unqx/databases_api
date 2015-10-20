from django.http import JsonResponse
from django.db import connection
from django.views.decorators.csrf import csrf_exempt


@csrf_exempt
def clear(request):
    if not request.method == 'POST':
        return JsonResponse({
            'code': 2,
            'response': 'Method in not supported'
        })

    cursor = connection.cursor()

    cursor.execute("SET foreign_key_checks = 0")
    cursor.execute("TRUNCATE TABLE subscriptions")
    cursor.execute("TRUNCATE TABLE thread")
    cursor.execute("TRUNCATE TABLE forum")
    cursor.execute("TRUNCATE TABLE post")
    cursor.execute("TRUNCATE TABLE user_user_follow")
    cursor.execute("TRUNCATE TABLE user")
    cursor.execute("SET foreign_key_checks = 1")

    return JsonResponse({
        'code': 0,
        'response': 'OK',
    })


@csrf_exempt
def status(request):
    if not request.method == 'GET':
        return JsonResponse({
            'code': 2,
            'response': 'Method in not supported'
        })

    cursor = connection.cursor()
    cursor.execute("SELECT COUNT(*) FROM post")
    posts = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM thread")
    threads = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM forum")
    forums = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM user")
    users = cursor.fetchone()[0]

    response = {
        "post": posts or 0,
        "thread": threads or 0,
        "forum": forums or 0,
        "user": users or 0
    }

    return JsonResponse({
        'code': 0,
        'response': response,
    })