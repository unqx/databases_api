from django.db import connection
from operator import itemgetter

def get_user_by_email(cursor, email):
    sql = ("SELECT * FROM user WHERE email = %s")
    cursor.execute(sql, (email,))
    data = cursor.fetchone()

    return data


def get_user_by_id(i):
    cursor = connection.cursor()

    sql_raw = ("SELECT * FROM user WHERE id = '{0}'")
    sql = sql_raw.format(i)

    cursor.execute(sql)
    data = cursor.fetchone()

    return data


def get_follow_data(user_id):
    cursor = connection.cursor()

    sql_followers_raw = ("""SELECT user.email
                            FROM user_user_follow
                            LEFT JOIN user on user.id = user_user_follow.from_user_id
                            WHERE user_user_follow.to_user_id = '{0}'""")

    sql_followers = sql_followers_raw.format(user_id)
    cursor.execute(sql_followers)
    followers = cursor.fetchall()

    sql_following_raw = ("SELECT user.email "
                         "FROM user_user_follow "
                         "LEFT JOIN user on user.id = user_user_follow.to_user_id "
                         "WHERE user_user_follow.from_user_id = '{0}'")

    sql_following = sql_following_raw.format(user_id)
    cursor.execute(sql_following)
    following = cursor.fetchall()

    return followers, following


def get_forum_by_shortname(cursor, sn):
    sql_raw = "SELECT * FROM forum WHERE short_name = %s;"
    cursor.execute(sql_raw, (sn,))
    data = cursor.fetchone()

    return data


def get_forum_by_id(forum_id):
    cursor = connection.cursor()
    sql = "SELECT * FROM forum WHERE id = %s;"
    cursor.execute(sql, (forum_id,))
    data = cursor.fetchone()

    return data



def get_thread_by_id(i):
    cursor = connection.cursor()
    sql_raw = "SELECT * FROM thread WHERE id = '{}';"

    sql = sql_raw.format(i)
    cursor.execute(sql)
    data = cursor.fetchone()

    return data


def get_subscriptions(user_id):
    cursor = connection.cursor()
    sql_raw = "SELECT thread_id FROM subscriptions WHERE user_id = '{0}'"

    sql = sql_raw.format(user_id)
    cursor.execute(sql)
    data = cursor.fetchall()

    return data


def get_post_by_id(post_id):
    cursor = connection.cursor()
    sql = "SELECT * FROM post WHERE id = %s"

    cursor.execute(sql, (post_id,))
    data = cursor.fetchone()

    return data