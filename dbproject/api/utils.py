from django.db import connection


def get_user_by_email(email):
    cursor = connection.cursor()

    sql_raw = ("SELECT * FROM user WHERE email = '{0}'")
    sql = sql_raw.format(email)

    cursor.execute(sql)
    data = cursor.fetchone()

    return data


def get_user_by_id(i):
    cursor = connection.cursor()

    sql_raw = ("SELECT * FROM user WHERE id = '{0}'")
    sql = sql_raw.format(i)

    cursor.execute(sql)
    data = cursor.fetchone()

    return data


def get_follow_data(id):
    cursor = connection.cursor()

    sql_followers_raw = ("SELECT user.email "
                         "FROM user_user_follow "
                         "LEFT JOIN user on user.id = user_user_follow.from_user_id "
                         "WHERE user_user_follow.to_user_id = '{0}'")

    sql_followers = sql_followers_raw.format(id)
    cursor.execute(sql_followers)
    followers = cursor.fetchall()

    sql_following_raw = ("SELECT user.email "
                         "FROM user_user_follow "
                         "LEFT JOIN user on user.id = user_user_follow.to_user_id "
                         "WHERE user_user_follow.from_user_id = '{0}'")

    sql_following = sql_following_raw.format(id)
    cursor.execute(sql_following)
    following = cursor.fetchall()

    return followers, following

