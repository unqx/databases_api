import json
import datetime
from django.http import JsonResponse
from django.db import connection
from django.views.decorators.csrf import csrf_exempt
from dbproject.api.utils import get_user_by_email, get_user_by_id, get_forum_by_shortname, get_subscriptions, get_follow_data, get_thread_by_id


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

            sql = "SELECT id, owner_id FROM forum WHERE name = %s"
            cursor.execute(sql, (name,))

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


            sql = "INSERT INTO forum (name, short_name, owner_id) VALUES (%s, %s, %s);"

            cursor.execute(sql, (name, short_name, user_data[0]))

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


@csrf_exempt
def forum_details(request):
    response = {}
    if not request.method == 'GET':
        return JsonResponse({
            'code': 2,
            'response': 'Method in not supported'
        })

    if 'forum' not in request.GET:
        return JsonResponse({
            'code': 3,
            'response': 'Missing field'
        })

    forum = request.GET.get('forum')

    forum_data = get_forum_by_shortname(forum)
    if not forum_data:
        return JsonResponse({
            'code': 1,
            'response': 'Forum does not exist'
        })

    user_data = get_user_by_id(forum_data[3])

    if 'related' in request.GET:
        if request.GET['related'] != 'user':
            return JsonResponse({
                'code': 3,
                'response': 'Wrong related parameter'
            })

        followers, following = get_follow_data(user_data[0])
        subs = get_subscriptions(user_data[0])
        user_info = {
            'username': user_data[1],
            'email': user_data[2],
            'name': user_data[3],
            'about': user_data[4],
            'isAnonymous': user_data[5],
            'id': user_data[0],
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

    else:
        user_info = user_data[2]

    response = {
        'id': forum_data[0],
        'name': forum_data[1],
        'short_name': forum_data[4],
        'user': user_info,
    }

    return JsonResponse({
        'code': 0,
        'response': response,
    })


@csrf_exempt
def forum_list_users(request):
    response = []
    if not request.method == 'GET':
        return JsonResponse({
            'code': 2,
            'response': 'Method in not supported'
        })

    if 'forum' not in request.GET:
        return JsonResponse({
            'code': 3,
            'response': 'Missing field'
        })

    forum = request.GET.get('forum')

    forum_data = get_forum_by_shortname(forum)
    if not forum_data:
        return JsonResponse({
            'code': 1,
            'response': 'Forum does not exist'
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

    sql = "SELECT * FROM user LEFT JOIN post p ON user.id = p.user_id WHERE p.forum_id = %s and user_id >= %s GROUP BY email ORDER BY name "
    sql += order

    if limit:
        sql += " LIMIT %s"
        cursor.execute(sql, (forum_data[0], since_id, limit))
    else:
        cursor.execute(sql, (forum_data[0], since_id))

    data = cursor.fetchall()

    for u in data:
        followers, following = get_follow_data(u[0])
        subs = get_subscriptions(u[0])
        response.append({
            'username': u[1],
            'email': u[2],
            'name': u[3],
            'about': u[4],
            'isAnonymous': u[5],
            'id': u[0],
            'followers': [
                f[0] for f in followers
            ],
            'following': [
                f[0] for f in following
            ],
            'subscriptions': [
                s[0] for s in subs
            ]
        })

    return JsonResponse({
        'code': 0,
        'response': response,
    })


@csrf_exempt
def forum_list_threads(request):
    response = []
    if not request.method == 'GET':
        return JsonResponse({
            'code': 2,
            'response': 'Method in not supported'
        })

    if 'forum' not in request.GET:
        return JsonResponse({
            'code': 3,
            'response': 'Missing field'
        })

    forum = request.GET.get('forum')

    forum_data = get_forum_by_shortname(forum)
    if not forum_data:
        return JsonResponse({
            'code': 1,
            'response': 'Forum does not exist'
        })

    if "since" in request.GET:
        since = request.GET['since']
        try:
            since = datetime.datetime.strptime(since, '%Y-%m-%d %H:%M:%S')
        except ValueError:
            return JsonResponse({
                'code': 3,
                'response': 'Since id param is wrong'
            })
    else:
        since = 0

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

    related_forum = False
    related_user = False

    if 'related' in request.GET:
        related = request.GET.getlist('related')
        for r in related:
            if r != 'user' and r != 'forum':
                return JsonResponse({
                    'code': 3,
                    'response': 'Related param is wrong'
                })
        if 'user' in related:
            related_user = True

        if 'forum' in related:
            related_forum = True

    cursor = connection.cursor()

    sql = "SELECT * FROM thread WHERE forum_id = %s AND date>=%s ORDER BY date "
    sql += order

    if limit:
        sql += " LIMIT %s"
        cursor.execute(sql, (forum_data[0], since, limit))
    else:
        cursor.execute(sql, (forum_data[0], since))

    data = cursor.fetchall()

    for t in data:
        if related_forum:
            forum_info = {
                'id': forum_data[0],
                'name': forum_data[1],
                'short_name': forum_data[4],
                'user': get_user_by_id(forum_data[3])[2],
            }
        else:
            forum_info = forum_data[4]

        user_data = get_user_by_id(t[4])
        if related_user:
            followers, following = get_follow_data(t[4])
            subs = get_subscriptions(t[4])
            user_info = {
                'username': user_data[1],
                'email': user_data[2],
                'name': user_data[3],
                'about': user_data[4],
                'isAnonymous': user_data[5],
                'id': user_data[0],
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
        else:
            user_info = user_data[2]

        response.append({
            'user': user_info,
            'forum': forum_info,
            'id': t[0],
            'title': t[2],
            'isClosed': bool(t[3]),
            'date': t[5].strftime('%Y-%m-%d %H:%M:%S'),
            'message': t[6],
            'slug': t[7],
            'isDeleted': bool(t[8]),
            'posts': t[12],
            'likes': t[10],
            'dislikes': t[9],
            'points': t[11],
        })

    return JsonResponse({
        'code': 0,
        'response': response,
    })


@csrf_exempt
def forum_list_posts(request):
    response = []
    if not request.method == 'GET':
        return JsonResponse({
            'code': 2,
            'response': 'Method in not supported'
        })

    if 'forum' not in request.GET:
        return JsonResponse({
            'code': 3,
            'response': 'Missing field'
        })

    forum = request.GET.get('forum')
    forum_data = get_forum_by_shortname(forum)
    if not forum_data:
        return JsonResponse({
            'code': 1,
            'response': 'Forum not found'
        })

    if "since" in request.GET:
        since = request.GET['since']
        try:
            since = datetime.datetime.strptime(since, '%Y-%m-%d %H:%M:%S')
        except ValueError:
            return JsonResponse({
                'code': 3,
                'response': 'Since id param is wrong'
            })
    else:
        since = 0

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

    user_related = False
    forum_related = False
    thread_related = False

    if 'related' in request.GET:
        related = request.GET.getlist('related')

        for r in related:
            if r != 'forum' and r != 'user' and r != 'thread':
                return JsonResponse({
                    'code': 3,
                    'response': 'Wrong related params'
                })
        if 'forum' in related:
            forum_related = True
        if 'thread' in related:
            thread_related = True
        if 'user' in related:
            user_related = True

    cursor = connection.cursor()

    sql = "SELECT * FROM post WHERE forum_id = %s AND date>=%s ORDER BY date "
    sql += order

    if limit:
        sql += " LIMIT %s"
        cursor.execute(sql, (forum_data[0], since, limit))
    else:
        cursor.execute(sql, (forum_data[0], since))

    posts = cursor.fetchall()

    for p in posts:
        if forum_related:
            forum_info = {
                'id': forum_data[0],
                'name': forum_data[1],
                'short_name': forum_data[4],
                'user': get_user_by_id(forum_data[3])[2],
                'isDeleted': bool(forum_data[2])
            }
        else:
            forum_info = forum_data[4]

        thread_data = get_thread_by_id(p[2])
        if thread_related:

            thread_info = {
                'id': thread_data[0],
                'forum': forum_data[4],
                'title': thread_data[2],
                'isClosed': bool(thread_data[3]),
                'user': get_user_by_id(thread_data[4])[2],
                'date': thread_data[5].strftime('%Y-%m-%d %H:%M:%S'),
                'message': thread_data[6],
                'slug': thread_data[7],
                'isDeleted': bool(thread_data[8]),
                'dislikes': thread_data[9],
                'likes': thread_data[10],
                'points': thread_data[11],
                'posts': thread_data[12]
            }
        else:
            thread_info = thread_data[0]

        user_data = get_user_by_id(p[3])
        if user_related:
            followers, following = get_follow_data(user_data[0])
            subs = get_subscriptions(user_data[0])
            user_info = {
                'id': user_data[0],
                'username': user_data[1],
                'email': user_data[2],
                'name': user_data[3],
                'about': user_data[4],
                'isAnonymous': bool(user_data[5]),
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
        else:
            user_info = user_data[2]

        response.append({
            'id': p[0],
            'forum': forum_info,
            'thread': thread_info,
            'user': user_info,
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
        'response': response
    })