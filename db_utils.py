DATABASE = "BankDatabase.db"


def selection_query_db(connection, query, params=(), one=False):
    cursor = connection.cursor()
    cursor.execute(query, params)
    result = cursor.fetchone() if one else cursor.fetchall()
    return result


def action_query_db(connection, query, params):
    cursor = connection.cursor()
    cursor.execute(query, params)
    connection.commit()
