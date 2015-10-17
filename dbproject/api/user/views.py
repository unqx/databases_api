import json
from django.http import JsonResponse
from django.db import connection
from django.views.decorators.csrf import csrf_exempt
from dbproject.api.utils import get_user_by_email, get_follow_data


@csrf_exempt
def user_create(request):
    response = {}
    if not request.method == 'POST':
        return JsonResponse({
            'code': 2,
            'response': 'Method in not supported'
        })

    try:
        request_params = json.loads(request.body)

        username = request_params.get('username', None)
        about = request_params.get('about', None)
        name = request_params.get('name', None)
        email = request_params.get('email', None)

        if not (username and about and name and email):
            return JsonResponse({
                'code': 3,
                'response': 'Missing field'
            })

        anon = request_params.get('isAnonymous', False)
        if type(anon) is not bool:
            return JsonResponse({
                'code': 3,
                'response': 'Wrong isAnonymous parameter type'
            })

        cursor = connection.cursor()

        if get_user_by_email(email):
            return JsonResponse({
                'code': 5,
                'response': 'User with provided email already exists'
            })

        sql_raw = "INSERT INTO user VALUES (null,'{0}','{1}','{2}','{3}','{4}')"
        sql = sql_raw.format(username, email, name, about, anon)
        cursor.execute(sql)

        response.update({
            'email': email,
            'username': username,
            'about': about,
            'name': name,
            'isAnonymous': anon,
            'id': cursor.lastrowid,
        })

    except ValueError:
        return JsonResponse({
            'code': 3,
            'response': 'No JSON object could be decoded'
        })

    return JsonResponse({'code': 0, 'response': response})


@csrf_exempt
def user_follow(request):
    response = {}
    if not request.method == 'POST':
        return JsonResponse({
            'code': 2,
            'response': 'Method in not supported'
        })

    try:
        request_params = json.loads(request.body)
        follower = request_params.get('follower', None)
        followee = request_params.get('followee', None)

        if not (followee and follower):
            return JsonResponse({
                'code': 3,
                'response': 'Missing field'
            })

        cursor = connection.cursor()

        follower_user = get_user_by_email(follower)
        followee_user = get_user_by_email(followee)

        if not (followee_user and follower_user):
            return JsonResponse({
                'code': 1,
                'response': 'User does not exist'
            })

        sql_raw = "INSERT IGNORE INTO user_user_follow VALUES (null, '{0}', '{1}');"

        sql = sql_raw.format(follower_user[0], followee_user[0])
        cursor.execute(sql)

        followers, following = get_follow_data(follower_user[0])

        response = {
            'id': follower_user[0],
            'username': follower_user[1],
            'email': follower_user[2],
            'name': follower_user[3],
            'about': follower_user[4],
            'isAnonymous': follower_user[5],
            'followers': [
                f[0] for f in followers
            ],
            'following': [
                f[0] for f in following
            ]
        }


    except ValueError:
        return JsonResponse({
            'code': 3,
            'response': 'No JSON object could be decoded'
        })

    return JsonResponse({'code': 0, 'response':response})