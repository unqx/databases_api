import json
import datetime
from django.http import JsonResponse
from django.db import connection, IntegrityError
from django.views.decorators.csrf import csrf_exempt
from dbproject.api.utils import get_user_by_email, get_follow_data, get_subscriptions, get_forum_by_id


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

        try:
            sql = "INSERT INTO user VALUES (null,%s,%s,%s,%s,%s)"
            cursor.execute(sql, (username, email, name, about, anon))
        except IntegrityError as e:
            cursor.close()
            return JsonResponse({
                'code': 5,
                'response': 'User with provided email already exists'
            })

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

        follower_user = get_user_by_email(cursor, follower)
        followee_user = get_user_by_email(cursor, followee)

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

        follower_user = get_user_by_email(cursor, follower)
        followee_user = get_user_by_email(cursor, followee)

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

    cursor = connection.cursor()
    user_data = get_user_by_email(cursor, user_email)
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


@csrf_exempt
def user_list_followers(request):
    response = []
    if not request.method == 'GET':
        return JsonResponse({
            'code': 2,
            'response': 'Method in not supported'
        })

    if 'user' not in request.GET:
        return JsonResponse({
            'code': 3,
            'response': 'Missing field'
        })

    if "since_id" in request.GET:
        since_id = request.GET['since_id']
        try:
            since_id = int(since_id)
        except ValueError:
            return JsonResponse({
                'code': 3,
                'response': 'Since id param is wrong'
            })
    else:
        since_id = 0

    if "limit" in request.GET:
        limit = request.GET['limit']
        try:
            limit = int(limit)
        except ValueError:
            return JsonResponse({
                'code': 3,
                'response': 'Limit param is wrong'
            })
    else:
        limit = None

    if "order" in request.GET:
        order = request.GET['order']
        if order != 'asc' and order != 'desc':
            return JsonResponse({
                'code': 3,
                'response': 'Order param is wrong'
            })
    else:
        order = 'desc'

    cursor = connection.cursor()

    user_data = get_user_by_email(cursor, request.GET.get('user'))
    if not user_data:
        cursor.close()
        return JsonResponse({
            'code': 1,
            'response': 'User does not exist'
        })

    sql = """SELECT u.id, u.username, u.email, u.name, u.about, u.is_anonymous
             FROM user_user_follow
             LEFT JOIN user u ON from_user_id = u.id
             WHERE to_user_id = %s AND from_user_id>=%s
             ORDER BY u.name """

    sql += order

    if limit:
        sql += " LIMIT %s"
        cursor.execute(sql, (user_data[0], since_id, limit))
    else:
        cursor.execute(sql, (user_data[0], since_id))

    followers = cursor.fetchall()

    for f in followers:
        followers, following = get_follow_data(f[0])
        subs = get_subscriptions(f[0])
        response.append({
            'username': f[1],
            'email': f[2],
            'name': f[3],
            'about': f[4],
            'isAnonymous': f[5],
            'id': f[0],
            'followers': [
                follower[0] for follower in followers
            ],
            'following': [
                follower[0] for follower in following
            ],
            'subscriptions': [
                s[0] for s in subs
            ]
        })

    return JsonResponse({
        'code': 0,
        'response': response
    })


@csrf_exempt
def user_list_following(request):
    response = []
    if not request.method == 'GET':
        return JsonResponse({
            'code': 2,
            'response': 'Method in not supported'
        })

    if 'user' not in request.GET:
        return JsonResponse({
            'code': 3,
            'response': 'Missing field'
        })

    if "since_id" in request.GET:
        since_id = request.GET['since_id']
        try:
            since_id = int(since_id)
        except ValueError:
            return JsonResponse({
                'code': 3,
                'response': 'Since id param is wrong'
            })
    else:
        since_id = 0

    if "limit" in request.GET:
        limit = request.GET['limit']
        try:
            limit = int(limit)
        except ValueError:
            return JsonResponse({
                'code': 3,
                'response': 'Limit param is wrong'
            })
    else:
        limit = None

    if "order" in request.GET:
        order = request.GET['order']
        if order != 'asc' and order != 'desc':
            return JsonResponse({
                'code': 3,
                'response': 'Order param is wrong'
            })
    else:
        order = 'desc'

    cursor = connection.cursor()

    user_data = get_user_by_email(cursor, request.GET.get('user'))
    if not user_data:
        return JsonResponse({
            'code': 1,
            'response': 'User does not exist'
        })


    sql = """SELECT u.id, u.username, u.email, u.name, u.about, u.is_anonymous
             FROM user_user_follow
             LEFT JOIN user u ON to_user_id = u.id
             WHERE from_user_id = %s AND to_user_id>=%s
             ORDER BY u.name """

    sql += order

    if limit:
        sql += " LIMIT %s"
        cursor.execute(sql, (user_data[0], since_id, limit))
    else:
        cursor.execute(sql, (user_data[0], since_id))

    followers = cursor.fetchall()

    for f in followers:
        followers, following = get_follow_data(f[0])
        subs = get_subscriptions(f[0])
        response.append({
            'username': f[1],
            'email': f[2],
            'name': f[3],
            'about': f[4],
            'isAnonymous': f[5],
            'id': f[0],
            'followers': [
                follower[0] for follower in followers
            ],
            'following': [
                follower[0] for follower in following
            ],
            'subscriptions': [
                s[0] for s in subs
            ]
        })

    return JsonResponse({
        'code': 0,
        'response': response
    })


@csrf_exempt
def user_update_profile(request):
    response = {}
    if not request.method == 'POST':
        return JsonResponse({
            'code': 2,
            'response': 'Method in not supported'
        })

    try:
        request_params = json.loads(request.body)

        if not ('name' in request_params and 'about' in request_params and 'user' in request_params):
            return JsonResponse({
                'code': 3,
                'response': 'Missing field'
            })

        user_email = request_params.get('user')
        about = request_params.get('about')
        name = request_params.get('name')

        cursor = connection.cursor()

        user_data = get_user_by_email(cursor, user_email)
        if not user_data:
            cursor.close()
            return JsonResponse({
                'code': 1,
                'response': 'User does not exist'
            })

        sql = "UPDATE user SET name = %s, about = %s WHERE email = %s"
        cursor.execute(sql, (name, about, user_email))

        followers, following = get_follow_data(user_data[0])
        subs = get_subscriptions(user_data[0])

        response.update({
            'name': name,
            'about': about,
            'email': user_email,
            'isAnonymous': user_data[5],
            'username': user_data[1],
            'id': user_data[0],
            'followers': [
                f for f in followers
            ],
            'following': [
                f for f in following
            ],
            'subscriptions': [
                s for s in subs
            ]
        })

    except ValueError:
        return JsonResponse({
            'code': 3,
            'response': 'No JSON object could be decoded'
        })

    return JsonResponse({
        'code': 0,
        'response': response,
    })


@csrf_exempt
def user_list_posts(request):
    response = []
    if not request.method == 'GET':
        return JsonResponse({
            'code': 2,
            'response': 'Method in not supported'
        })


    if 'user' not in request.GET:
        return JsonResponse({
            'code': 3,
            'response': 'Missing field'
        })

    user_email = request.GET.get('user')
    cursor = connection.cursor()

    user_data = get_user_by_email(cursor, user_email)
    if not user_data:
        cursor.close()
        return JsonResponse({
            'code': 1,
            'response': 'User not found'
        })

    if 'since' in request.GET:
        since = request.GET.get('since')
        try:
            datetime.datetime.strptime(since, '%Y-%m-%d %H:%M:%S')
        except ValueError:
            return JsonResponse({
                'code': 3,
                'response': 'Wrong since date param'
            })
    else:
        since = 0

    if "limit" in request.GET:
        limit = request.GET.get('limit')
        try:
            limit = int(limit)
        except ValueError:
            return JsonResponse({
                'code': 3,
                'response': 'Wrong limit param'
            })
    else:
        limit = None

    if "order" in request.GET:
        order = request.GET.get('order')
        if order != 'asc' and order != 'desc':
            return JsonResponse({
                'code': 3,
                'response': 'Wrong order param'
            })
    else:
        order = 'desc'

    cursor = connection.cursor()

    sql = "SELECT * FROM post WHERE user_id = %s AND date>=%s ORDER BY date "
    sql += order

    if limit:
        sql += " LIMIT %s"
        cursor.execute(sql, (user_data[0], since, limit))
    else:
        cursor.execute(sql, (user_data[0], since))

    posts = cursor.fetchall()

    for p in posts:
        response.append({
            'id': p[0],
            'user': user_email,
            'forum': get_forum_by_id(p[1])[4],
            'thread': p[2],
            'message': p[4],
            'date': p[5].strftime('%Y-%m-%d %H:%M:%S'),
            'parent': p[6],
            'isApproved': bool(p[8]),
            'isHighlighted': bool(p[9]),
            'isSpam': bool(p[10]),
            'isEdited': bool(p[11]),
            'isDeleted': bool(p[12]),
            'likes': p[13],
            'dislikes': p[14],
            'points': p[15],
        })


    return JsonResponse({
        'code': 0,
        'response': response,
    })