import json
from django.http import JsonResponse
from django.db import connection
from django.views.decorators.csrf import csrf_exempt
from dbproject.api.utils import get_user_by_email, get_follow_data, get_subscriptions


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

        if not ('username' in request_params and 'about' in request_params and 'name' in request_params and 'email' in request_params):
            return JsonResponse({
                'code': 3,
                'response': 'Missing field'
            })

        username = request_params.get('username')
        about = request_params.get('about')
        name = request_params.get('name')
        email = request_params.get('email')

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

        sql = "INSERT INTO user VALUES (null,%s,%s,%s,%s,%s)"
        cursor.execute(sql, (username, email, name, about, anon))

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

        sql = "INSERT IGNORE INTO user_user_follow VALUES (null, %s, %s);"
        cursor.execute(sql, (follower_user[0], followee_user[0]))

        followers, following = get_follow_data(follower_user[0])
        subs = get_subscriptions(follower_user[0])

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
            ],
            'subscriptions': [
                s[0] for s in subs
            ]

        }


    except ValueError:
        return JsonResponse({
            'code': 3,
            'response': 'No JSON object could be decoded'
        })

    return JsonResponse({'code': 0, 'response':response})


@csrf_exempt
def user_unfollow(request):
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

        sql = "DELETE FROM user_user_follow WHERE from_user_id = %s AND to_user_id = %s;"
        cursor.execute(sql, (follower_user[0], followee_user[0]))

        followers, following = get_follow_data(follower_user[0])
        subs = get_subscriptions(follower_user[0])

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
            ],
            'subscriptions': [
                s[0] for s in subs
            ]
        }

    except ValueError:
        return JsonResponse({
            'code': 3,
            'response': 'No JSON object could be decoded'
        })

    return JsonResponse({'code': 0, 'response': response})


@csrf_exempt
def user_details(request):
    response = {}
    if not request.method == 'GET':
        return JsonResponse({
            'code': 2,
            'response': 'Method in not supported'
        })

    user_email = request.GET.get('user', None)

    if not user_email:
        return JsonResponse({
            'code': 3,
            'response': 'Missing field'
        })

    user_data = get_user_by_email(user_email)
    if not user_data:
        return JsonResponse({
            'code': 1,
            'response': 'User does not exist'
        })

    followers, following = get_follow_data(user_data[0])
    subs = get_subscriptions(user_data[0])

    response = {
        'id': user_data[0],
        'username': user_data[1],
        'email': user_data[2],
        'name': user_data[3],
        'about': user_data[4],
        'isAnonymous': user_data[5],
        'followers': [
            f[0] for f in followers
        ],
        'following': [
            f[0] for f in following
        ],
        'subscriptions': [
            s[0] for s in subs
        ]
    }

    return JsonResponse({'code': 0, 'response': response})
