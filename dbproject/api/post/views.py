import json
import datetime
from django.http import JsonResponse
from django.db import connection
from django.views.decorators.csrf import csrf_exempt
from dbproject.api.utils import get_user_by_email, get_forum_by_id, get_forum_by_shortname, get_user_by_id, \
    get_thread_by_id, get_post_by_id, get_follow_data, get_subscriptions


@csrf_exempt
def post_create(request):
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

    if not ('date' in request_params and 'thread' in request_params and 'message' in request_params
        and 'user' in request_params and 'forum' in request_params):
        return JsonResponse({
            'code': 3,
            'response': 'Missing field'
        })

    date = request_params.get('date')
    thread_id = request_params.get('thread')
    message = request_params.get('message')
    user_email = request_params.get('user')
    forum_name = request_params.get('forum')

    cursor = connection.cursor()

    # Optional params:
    if 'isApproved' in request_params:
        is_approved = request_params.get('isApproved')

        if type(is_approved) is not bool:
            cursor.close()
            return JsonResponse({
                'code': 3,
                'response': 'Wrong isApproved parameter type'
            })
    else:
        is_approved = False

    if 'isHighlighted' in request_params:
        is_highlited = request_params.get('isHighlighted')

        if type(is_highlited) is not bool:
            cursor.close()
            return JsonResponse({
                'code': 3,
                'response': 'Wrong isHighlited parameter type'
            })
    else:
        is_highlited = False

    if 'isEdited' in request_params:
        is_edited = request_params.get('isEdited')

        if type(is_edited) is not bool:
            cursor.close()
            return JsonResponse({
                'code': 3,
                'response': 'Wrong isEdited parameter type'
            })
    else:
        is_edited = False

    if 'isSpam' in request_params:
        is_spam = request_params.get('isSpam')

        if type(is_spam) is not bool:
            cursor.close()
            return JsonResponse({
                'code': 3,
                'response': 'Wrong isSpam parameter type'
            })
    else:
        is_spam = False

    if 'isDeleted' in request_params:
        is_deleted = request_params.get('isDeleted')

        if type(is_deleted) is not bool:
            cursor.close()
            return JsonResponse({
                'code': 3,
                'response': 'Wrong isDeleted parameter type'
            })
    else:
        is_deleted = False

    if 'parent' in request_params:
        parent = request_params.get('parent')
    else:
        parent = None

    forum_data = get_forum_by_shortname(cursor, forum_name)
    if not forum_data:
        cursor.close()
        return JsonResponse({
            'code': 1,
            'response': 'Forum does not exist'
        })

    cursor.execute("SELECT id, posts FROM thread WHERE id=%s AND forum_id=%s", (thread_id, forum_data[0]))
    thread_data = cursor.fetchone()
    if not thread_data:
        cursor.close()
        return JsonResponse({
            'code': 1,
            'response': 'Thread does not exist or no such thread in provided forum'
        })

    user_data = get_user_by_email(cursor, user_email)
    if not user_data:
        cursor.close()
        return JsonResponse({
            'code': 1,
            'response': 'User does not exist'
        })

    if not parent:
        posts_count = int(thread_data[1])
        post_path = '{0:011d}'.format(posts_count + 1)

    else:
        try:
            parent = int(parent)
        except ValueError:
            cursor.close()
            return JsonResponse({
                'code': 3,
                'response': 'Wrong parent parameter type'
            })

        cursor.execute("SELECT path FROM post WHERE id = %s AND thread_id = %s", (parent,thread_id))

        parent_post_data = cursor.fetchone()
        if not parent_post_data:
            cursor.close()
            return JsonResponse({
                'code': 1,
                'response': 'Post not found or post required is in another thread'
            })

        cursor.execute("SELECT COUNT(*) FROM post WHERE parent = %s", (parent,))

        parent_childs = int(cursor.fetchone()[0])
        post_path = parent_post_data[0] + '.' + '{0:011d}'.format(parent_childs + 1)


    sql = "INSERT INTO post VALUES (null, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 0, 0, 0)"

    insert_data = (forum_data[0], thread_data[0], user_data[0], message, date, parent, post_path, is_approved,
                   is_highlited, is_spam, is_edited, is_deleted)

    cursor.execute(sql, insert_data)

    response.update({
        'id': cursor.lastrowid,
        'forum': forum_name,
        'thread': thread_id,
        'user': user_email,
        'message': message,
        'parent': parent,
        'isSpam': is_spam,
        'isHighlighted': is_highlited,
        'isEdited': is_edited,
        'isApproved': is_approved,
        'date': date,
    })

    cursor.execute("UPDATE thread SET posts = posts+1 WHERE id = %s", (thread_id,))

    return JsonResponse({
        'code': 0,
        'response': response,
    })


@csrf_exempt
def post_remove(request):
    response = {}
    if not request.method == 'POST':
        return JsonResponse({
            'code': 2,
            'response': 'Method in not supported'
        })

    try:
        request_params = json.loads(request.body)

        if 'post' not in request_params:
            return JsonResponse({
                'code': 3,
                'response': 'Missing field'
            })

        post_id = request_params.get('post')
        post_data = get_post_by_id(post_id)

        if not post_data:
            return JsonResponse({
                'code': 1,
                'response': 'Post not found'
            })

        cursor = connection.cursor()
        sql = "UPDATE post SET is_deleted = 1 WHERE id = %s"
        cursor.execute(sql, (post_id,))

        cursor.execute("UPDATE thread SET posts = posts-1 WHERE id = %s", (post_data[2],))

        response.update({
            'post': post_id,
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
def post_restore(request):
    response = {}
    if not request.method == 'POST':
        return JsonResponse({
            'code': 2,
            'response': 'Method in not supported'
        })

    try:
        request_params = json.loads(request.body)

        if 'post' not in request_params:
            return JsonResponse({
                'code': 3,
                'response': 'Missing field'
            })

        post_id = request_params.get('post')
        post_data = get_post_by_id(post_id)

        if not post_data:
            return JsonResponse({
                'code': 1,
                'response': 'Post not found'
            })

        cursor = connection.cursor()
        sql = "UPDATE post SET is_deleted = 0 WHERE id = %s"
        cursor.execute(sql, (post_id,))

        cursor.execute("UPDATE thread SET posts = posts+1 WHERE id = %s", (post_data[2],))

        response.update({
            'post': post_id,
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
def post_details(request):
    response = {}
    if not request.method == 'GET':
        return JsonResponse({
            'code': 2,
            'response': 'Method in not supported'
        })

    if 'post' not in request.GET:
        return JsonResponse({
                'code': 3,
                'response': 'Missing field'
            })

    post_id = request.GET.get('post')
    post_data = get_post_by_id(post_id)

    if not post_data:
        return JsonResponse({
                'code': 1,
                'response': 'Post not found'
            })
    user_data = get_user_by_id(post_data[3])
    thread_data = get_thread_by_id(post_data[2])
    forum_data = get_forum_by_id(post_data[1])

    if 'related' in request.GET:
        related = request.GET.getlist('related')

        for r in related:
            if r != 'forum' and r != 'user' and r != 'thread':
                return JsonResponse({
                    'code': 3,
                    'response': 'Wrong related params'
                })

        if 'user' in related:
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

        if 'thread' in related:
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
    else:
        user_info = user_data[2]
        thread_info = thread_data[0]
        forum_info = forum_data[4]


    response.update({
        'id': int(post_id),
        'forum': forum_info,
        'thread': thread_info,
        'user': user_info,
        'message': post_data[4],
        'date': post_data[5].strftime('%Y-%m-%d %H:%M:%S'),
        'parent': post_data[6],
        'isApproved': bool(post_data[8]),
        'isHighlighted': bool(post_data[9]),
        'isSpam': bool(post_data[10]),
        'isEdited': bool(post_data[11]),
        'isDeleted': bool(post_data[12]),
        'likes': post_data[13],
        'dislikes': post_data[14],
        'points': post_data[15],
    })

    return JsonResponse({
        'code': 0,
        'response': response
    })


@csrf_exempt
def post_vote(request):
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

    if not ('post' in request_params and 'vote' in request_params):
        return JsonResponse({
                'code': 3,
                'response': 'Missing field'
            })

    post_id = request_params.get('post')

    post_data = get_post_by_id(post_id)
    if not post_data:
        return JsonResponse({
                'code': 1,
                'response': 'Post not found'
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
        cursor.execute("UPDATE post SET likes=likes+1 WHERE id=%s", (post_id,))
    else:
        cursor.execute("UPDATE post SET dislikes=dislikes+1 WHERE id=%s", (post_id,))

    cursor.execute("UPDATE post SET points=points+%s WHERE id=%s", (vote, post_id))

    post_data = get_post_by_id(post_id)

    response.update({
        'id': int(post_id),
        'forum': get_forum_by_id(post_data[1])[4],
        'thread': post_data[2],
        'user': get_user_by_id(post_data[3])[2],
        'message': post_data[4],
        'date': post_data[5].strftime('%Y-%m-%d %H:%M:%S'),
        'parent': post_data[6],
        'isApproved': bool(post_data[8]),
        'isHighlighted': bool(post_data[9]),
        'isSpam': bool(post_data[10]),
        'isEdited': bool(post_data[11]),
        'isDeleted': bool(post_data[12]),
        'likes': post_data[13],
        'dislikes': post_data[14],
        'points': post_data[15],
    })

    return JsonResponse({
        'code': 0,
        'response': response
    })


@csrf_exempt
def post_update(request):
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

    if not ('post' in request_params and 'message' in request_params):
        return JsonResponse({
                'code': 3,
                'response': 'Missing field'
            })
    post_id = request_params.get('post')

    post_data = get_post_by_id(post_id)
    if not post_data:
        return JsonResponse({
                'code': 1,
                'response': 'Post not found'
            })

    message = request_params.get('message')

    cursor = connection.cursor()
    sql = "UPDATE post SET message=%s WHERE id = %s"

    cursor.execute(sql, (message, post_id))

    response.update({
        'id': int(post_id),
        'forum': get_forum_by_id(post_data[1])[4],
        'thread': post_data[2],
        'user': get_user_by_id(post_data[3])[2],
        'message': message,
        'date': post_data[5].strftime('%Y-%m-%d %H:%M:%S'),
        'parent': post_data[6],
        'isApproved': bool(post_data[8]),
        'isHighlighted': bool(post_data[9]),
        'isSpam': bool(post_data[10]),
        'isEdited': bool(post_data[11]),
        'isDeleted': bool(post_data[12]),
        'likes': post_data[13],
        'dislikes': post_data[14],
        'points': post_data[15],
    })

    return JsonResponse({
        'code': 0,
        'response': response
    })


@csrf_exempt
def post_list(request):
    response = []
    if not request.method == 'GET':
        return JsonResponse({
            'code': 2,
            'response': 'Method in not supported'
        })

    if not ('forum' in request.GET or 'thread' in request.GET):
        return JsonResponse({
            'code': 3,
            'response': 'Missing field'
        })

    if 'forum' in request.GET and 'thread' in request.GET:
        return JsonResponse({
            'code': 3,
            'response': 'Provide only forum or thread'
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
    cursor = connection.cursor()

    if by_forum:
        forum = request.GET.get('forum')
        forum_data = get_forum_by_shortname(cursor, forum)
        if not forum_data:
            return JsonResponse({
                'code': 1,
                'response': 'Forum not found'
            })
        search_by = forum_data[0]
    else:
        thread_id = request.GET.get('thread')
        thread_data = get_thread_by_id(thread_id)
        if not thread_data:
            return JsonResponse({
                'code': 1,
                'response': 'Thread not found'
            })
        search_by = thread_id

    sql = "SELECT * FROM post WHERE date>=%s AND "

    sql += " forum_id = %s" if by_forum else " thread_id = %s"
    sql += " ORDER BY date "
    sql += order

    if limit:
        sql += " LIMIT %s"
        cursor.execute(sql, (since, search_by, limit))
    else:
        cursor.execute(sql, (since, search_by))

    data = cursor.fetchall()

    for p in data:
        response.append({
            'id': int(p[0]),
            'forum': get_forum_by_id(p[1])[4],
            'thread': p[2],
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