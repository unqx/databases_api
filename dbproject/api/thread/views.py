import json
import datetime
from django.http import JsonResponse
from django.db import connection
from django.views.decorators.csrf import csrf_exempt
from dbproject.api.utils import get_user_by_email, get_user_by_id, get_forum_by_shortname, get_thread_by_id, get_forum_by_id, get_follow_data, get_subscriptions


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

        sql_select = "SELECT * FROM thread WHERE title = %s AND forum_id = %s"

        cursor.execute(sql_select, (title, forum_data[0]))
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

        sql_insert = "INSERT INTO thread VALUES (null, %s, %s, %s, %s, %s, %s, %s, %s, 0, 0, 0, 0)"
        sql_insert_data = (forum_data[0], title, is_closed, user_data[0], date, message, slug, is_deleted)

        cursor.execute(sql_insert, sql_insert_data)

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


@csrf_exempt
def thread_details(request):
    response = {}
    if not request.method == 'GET':
        return JsonResponse({
            'code': 2,
            'response': 'Method in not supported'
        })

    if 'thread' not in request.GET:
        return JsonResponse({
            'code': 3,
            'response': 'Missing field'
        })

    thread_id = request.GET.get('thread')

    thread_data = get_thread_by_id(thread_id)
    if not thread_data:
        return JsonResponse({
            'code': 1,
            'response': 'Thread not found'
        })

    related = request.GET.getlist('related')
    forum_data = get_forum_by_id(thread_data[1])
    user_data = get_user_by_id(thread_data[4])

    for case in related:
        if case not in ['user', 'forum']:
            return JsonResponse({
                'code': 3,
                'response': 'Wrong related param'
            })

    if 'forum' in related:
        forum_info = {
            'id': forum_data[0],
            'name': forum_data[1],
            'short_name': forum_data[4],
            'user': get_user_by_id(forum_data[3])[2],
            'isDeleted': bool(forum_data[2])
        }
    else:
        forum_info = forum_data[4]

    if 'user' in related:
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
        'user': user_info,
        'forum': forum_info,
        'id': thread_data[0],
        'title': thread_data[2],
        'isClosed': bool(thread_data[3]),
        'date': thread_data[5].strftime('%Y-%m-%d %H:%M:%S'),
        'message': thread_data[6],
        'slug': thread_data[7],
        'isDeleted': bool(thread_data[8]),
        'posts': thread_data[12] if not thread_data[8] else 0,
        'likes': thread_data[10],
        'dislikes': thread_data[9],
        'points': thread_data[11],
    }

    return JsonResponse({
        'code': 0,
        'response': response,
    })


@csrf_exempt
def thread_close(request):
    response = {}
    if not request.method == 'POST':
        return JsonResponse({
            'code': 2,
            'response': 'Method in not supported'
        })

    try:
        request_params = json.loads(request.body)

        if 'thread' not in request_params:
            return JsonResponse({
                'code': 3,
                'response': 'Missing field'
            })

        thread_id = request_params.get('thread')
        thread_data = get_thread_by_id(thread_id)

        if not thread_data:
            return JsonResponse({
                'code': 1,
                'response': 'Thread not found'
            })

        cursor = connection.cursor()
        sql = "UPDATE thread SET is_closed = 1 WHERE id = %s"
        cursor.execute(sql, (thread_id,))

        response.update({
            'thread': thread_id,
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
def thread_open(request):
    response = {}
    if not request.method == 'POST':
        return JsonResponse({
            'code': 2,
            'response': 'Method in not supported'
        })

    try:
        request_params = json.loads(request.body)

        if 'thread' not in request_params:
            return JsonResponse({
                'code': 3,
                'response': 'Missing field'
            })

        thread_id = request_params.get('thread')
        thread_data = get_thread_by_id(thread_id)

        if not thread_data:
            return JsonResponse({
                'code': 1,
                'response': 'Thread not found'
            })

        cursor = connection.cursor()
        sql = "UPDATE thread SET is_closed = 0 WHERE id = %s"
        cursor.execute(sql, (thread_id,))

        response.update({
            'thread': thread_id,
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
def thread_remove(request):
    response = {}
    if not request.method == 'POST':
        return JsonResponse({
            'code': 2,
            'response': 'Method in not supported'
        })

    try:
        request_params = json.loads(request.body)

        if 'thread' not in request_params:
            return JsonResponse({
                'code': 3,
                'response': 'Missing field'
            })

        thread_id = request_params.get('thread')
        thread_data = get_thread_by_id(thread_id)

        if not thread_data:
            return JsonResponse({
                'code': 1,
                'response': 'Thread not found'
            })

        cursor = connection.cursor()
        sql = "UPDATE thread SET is_deleted = 1 WHERE id = %s"
        cursor.execute(sql, (thread_id,))

        cursor.execute("UPDATE post SET is_deleted = 1 WHERE thread_id = %s", (thread_id, ))

        response.update({
            'thread': thread_id,
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
def thread_restore(request):
    response = {}
    if not request.method == 'POST':
        return JsonResponse({
            'code': 2,
            'response': 'Method in not supported'
        })

    try:
        request_params = json.loads(request.body)

        if 'thread' not in request_params:
            return JsonResponse({
                'code': 3,
                'response': 'Missing field'
            })

        thread_id = request_params.get('thread')
        thread_data = get_thread_by_id(thread_id)

        if not thread_data:
            return JsonResponse({
                'code': 1,
                'response': 'Thread not found'
            })

        cursor = connection.cursor()
        sql = "UPDATE thread SET is_deleted = 0 WHERE id = %s"
        cursor.execute(sql, (thread_id,))

        cursor.execute("UPDATE post SET is_deleted = 0 WHERE thread_id = %s", (thread_id, ))

        response.update({
            'thread': thread_id,
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
def thread_update(request):
    response = {}
    if not request.method == 'POST':
        return JsonResponse({
            'code': 2,
            'response': 'Method in not supported'
        })
    try:
        request_params = json.loads(request.body)

        if not ('thread' in request_params and 'message' in request_params and 'slug' in request_params):
            return JsonResponse({
                'code': 3,
                'response': 'Missing field'
            })

        thread_id = request_params.get('thread')
        message = request_params.get('message')
        slug = request_params.get('slug')

        thread_data = get_thread_by_id(thread_id)
        if not thread_data:
            return JsonResponse({
                'code': 1,
                'response': 'Thread not found'
            })

        sql = "UPDATE thread SET message = %s, slug = %s WHERE id = %s"

        cursor = connection.cursor()

        cursor.execute(sql, (message, slug, thread_id))

        response = {
            'user': get_user_by_id(thread_data[4])[2],
            'forum': get_forum_by_id(thread_data[1])[4],
            'id': thread_id,
            'title': thread_data[2],
            'isClosed': bool(thread_data[3]),
            'date': thread_data[5].strftime('%Y-%m-%d %H:%M:%S'),
            'message': message,
            'slug': slug,
            'isDeleted': bool(thread_data[8]),
            'posts': thread_data[12] if not thread_data[8] else 0,
            'likes': thread_data[10],
            'dislikes': thread_data[9],
            'points': thread_data[11],
        }

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
def thread_vote(request):
    response = {}
    if not request.method == 'POST':
        return JsonResponse({
            'code': 2,
            'response': 'Method in not supported'
        })
    try:
        request_params = json.loads(request.body)
    except ValueError:
        return JsonResponse({
            'code': 3,
            'response': 'No JSON object could be decoded'
        })

    if not ('thread' in request_params and 'vote' in request_params):
        return JsonResponse({
                'code': 3,
                'response': 'Missing field'
            })

    thread_id = request_params.get('thread')

    thread_data = get_thread_by_id(thread_id)
    if not thread_data:
        return JsonResponse({
                'code': 1,
                'response': 'Thread not found'
            })

    vote = request_params.get('vote')

    try:
        vote = int(vote)
    except ValueError:
        return JsonResponse({
                'code': 3,
                'response': 'Wrong vote param'
            })
    if vote != 1 and vote != -1:
        return JsonResponse({
                'code': 3,
                'response': 'Wrong vote param'
            })

    cursor = connection.cursor()

    if vote == 1:
        cursor.execute("UPDATE thread SET likes=likes+1 WHERE id=%s", (thread_id,))
    else:
        cursor.execute("UPDATE thread SET dislikes=dislikes+1 WHERE id=%s", (thread_id,))

    cursor.execute("UPDATE thread SET points=points+%s WHERE id=%s", (vote, thread_id))

    thread_data = get_thread_by_id(thread_id)

    response.update({
        'user': get_user_by_id(thread_data[4])[2],
        'forum': get_forum_by_id(thread_data[1])[4],
        'id': thread_id,
        'title': thread_data[2],
        'isClosed': bool(thread_data[3]),
        'date': thread_data[5].strftime('%Y-%m-%d %H:%M:%S'),
        'message': thread_data[6],
        'slug': thread_data[7],
        'isDeleted': bool(thread_data[8]),
        'posts': thread_data[12],
        'likes': thread_data[10],
        'dislikes': thread_data[9],
        'points': thread_data[11],
    })

    return JsonResponse({
        'code': 0,
        'response': response
    })


@csrf_exempt
def thread_list(request):
    response = []
    if not request.method == 'GET':
        return JsonResponse({
            'code': 2,
            'response': 'Method in not supported'
        })

    if not ('forum' in request.GET or 'user' in request.GET):
        return JsonResponse({
            'code': 3,
            'response': 'Missing field'
        })

    if 'forum' in request.GET and 'user' in request.GET:
        return JsonResponse({
            'code': 3,
            'response': 'Provide only forum or user'
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

    by_forum = 'forum' in request.GET

    search_by = None

    if by_forum:
        forum = request.GET.get('forum')
        forum_data = get_forum_by_shortname(forum)
        if not forum_data:
            return JsonResponse({
                'code': 1,
                'response': 'Forum not found'
            })
        search_by = forum_data[0]
    else:
        user_email = request.GET.get('user')
        user_data = get_user_by_email(user_email)
        if not user_data:
            return JsonResponse({
                'code': 1,
                'response': 'Thread not found'
            })
        search_by = user_data[0]

    cursor = connection.cursor()

    sql = "SELECT * FROM thread WHERE date>=%s AND "

    sql += " forum_id = %s" if by_forum else " user_id = %s"
    sql += " ORDER BY date "
    sql += order

    if limit:
        sql += " LIMIT %s"
        cursor.execute(sql, (since, search_by, limit))
    else:
        cursor.execute(sql, (since, search_by))

    data = cursor.fetchall()

    for t in data:
        response.append({
            'user': get_user_by_id(t[4])[2],
            'forum': get_forum_by_id(t[1])[4],
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
        'response': response
    })


@csrf_exempt
def thread_list_posts(request):
    response = []
    if not request.method == 'GET':
        return JsonResponse({
            'code': 2,
            'response': 'Method in not supported'
        })

    if 'thread' not in request.GET:
        return JsonResponse({
            'code': 3,
            'response': 'Missing field'
        })

    thread_id = request.GET.get('thread')
    thread_data = get_thread_by_id(thread_id)

    if not thread_data:
        return JsonResponse({
                'code': 1,
                'response': 'Thread not found'
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

    if "sort" in request.GET:
        sort = request.GET['sort']
        if sort != 'flat' and sort != 'tree' and sort != 'parent_tree':
            return JsonResponse({
                'code': 3,
                'response': 'Sort param is wrong'
            })
    else:
        sort = 'flat'

    cursor = connection.cursor()

    if sort == 'flat':
        sql = "SELECT * FROM post WHERE thread_id = %s AND date>=%s ORDER BY date "
        sql += order

        if limit:
            sql += " LIMIT %s"
            cursor.execute(sql, (thread_id, since, limit))
        else:
            cursor.execute(sql, (thread_id, since))

        data = cursor.fetchall()

    elif sort == 'tree':
        if order == 'asc':
            sql = "SELECT * FROM post WHERE thread_id = %s AND date>=%s ORDER BY path ASC"

            if limit:
                sql += " LIMIT %s"
                cursor.execute(sql, (thread_id, since, limit))
            else:
                cursor.execute(sql, (thread_id, since))

            data = cursor.fetchall()

        else:
            # tree -> desc
            query = "SELECT * FROM post " \
                    "WHERE date>=%s AND thread_id=%s AND parent IS NULL ORDER BY path DESC"
            query += " LIMIT %s" if limit is not None else ""
            sql_data = (since, thread_id, limit) if limit is not None else (since, thread_id)

            cursor.execute(query, sql_data)
            roots = cursor.fetchall()
            data = []
            if limit:
                # tree -> desc -> limit
                posts = 0
                for root in roots:
                    if posts < limit:
                        data.append(root)
                        posts += 1
                        if posts < limit:
                            parent_path = root[7] + '.%'
                            query = "SELECT * FROM post " \
                                    "WHERE path LIKE %s ORDER BY path ASC LIMIT %s"
                            sql_data = (parent_path, limit)
                            cursor.execute(query, sql_data)
                            children = cursor.fetchall()
                            for child in children:
                                if posts < limit:
                                    data.append(child)
                                    posts += 1
            else:
                # tree -> desc -> no limit
                for p in roots:
                    data.append(p)
                    parent_path = p[7] + '.%'
                    query = "SELECT * FROM post " \
                            "WHERE path LIKE %s ORDER BY path ASC"
                    sql_data = (parent_path,)
                    cursor.execute(query, sql_data)
                    data2 = cursor.fetchall()
                    for p1 in data2:
                        data.append(p1)
    else:
        # parent_tree
        query = "SELECT * FROM post " \
                "WHERE date>=%s AND thread_id=%s AND parent IS NULL ORDER BY date "
        query += order
        query += " LIMIT %s" if limit is not None else ""
        sql_data = (since, thread_id, limit) if limit is not None else (since, thread_id)
        cursor.execute(query, sql_data)
        data1 = cursor.fetchall()
        data = []
        for p in data1:
            data.append(p)
            parent_path = p[7] + '.%'
            query = "SELECT * FROM post " \
                    "WHERE path LIKE %s ORDER BY path ASC"
            sql_data = (parent_path,)
            cursor.execute(query, sql_data)
            data2 = cursor.fetchall()
            for p1 in data2:
                data.append(p1)


    for p in data:
        response.append({
            'id': p[0],
            'forum': get_forum_by_id(p[1])[4],
            'thread': thread_id,
            'user': get_user_by_id(p[3])[2],
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

