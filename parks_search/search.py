import sqlite3
from .db import haversine_distance


def search_parks(params):
    """
    Search for parks based on the given parameters.

    Parameters
    ----------
    params : dict
        A dictionary of parameters to search for. The keys are the
        field names and the values are the values to search for.

        If a key is not present, it should not be used in the search.

        Keys:
            name: str
                If included, results should be filtered to only include parks that start with
                the provided string.  (Case-insensitive.)
            query_terms: list
                If included, a list of terms to search for in the park's description.
            zip_code: str
                If included, only parks with an address in the given zip code should be returned.
            open_at: tuple(str, str)
                If included, only parks that are open at the given time should be returned.

                A tuple of two strings, the first is the day of the week and the second is the
                time.  The day of the week will be "mon", "tue", "wed", "thu", "fri", "sat", or
                "sun".  The time will be a value between 0000 and 2359 representing a time.
            near: tuple(float, float, float)
                lat, lon, distance
                If included, only parks that are within the given distance (in miles) of the
                given latitude and longitude should be returned.

    Returns
    -------
    list
        A list of parks that match the given parameters.  Each park should be an instance of
        `sqlite.Row` with the appropriate fields (see "What attributes should be returned?"
         in the README).
    """
    # TODO: implement this function

    # Start by opening a connection to the database and registering the haversine_distance
    # function with the connection. This will allow you to use the haversine_distance function
    # in your SQL queries as shown in the README.

    connection = sqlite3.connect('data/parks.db')
    connection.create_function('haversine_distance', 4, haversine_distance)
    connection.row_factory = sqlite3.Row        
    cursor = connection.cursor()

    answer = []
    querylist = []


    select_query = 'SELECT'
    # from_query = ' FROM parks as p JOIN park_times as t '
    where_query = ' WHERE '

    if 'near' in params:
        select_query += ' haversine_distance(?, ?, latitude, longitude) AS distance, p.name, p.address, p.description, p.history, p.url '
        querylist.extend([params['near'][0], params['near'][1]])
    else:
        select_query += ' p.name, p.address, p.description, p.history, p.url '

    if 'open_at' in params:
        select_query += ', t.day, t.open_time, t.close_time FROM parks as p JOIN park_times as t ON p.id = t.park_id' 
    else:
        select_query += 'FROM parks as p'
    
    for k, v in params.items():
        if k == 'name':
            where_query += ' name LIKE ? AND '
            v = v + '%'
            querylist.append(v)
        
        elif k == 'query_terms':
            for token in v:
                where_query += ' tokens LIKE ? AND '
                token = '% ' + token + ' %'
                querylist.append(token)

        elif k == 'zip_code':
            where_query += ' address LIKE ? AND '
            v = '%' + v + '%'
            querylist.append(v)

        elif k == 'open_at':
            where_query += ' day = ? AND open_time <= ? AND close_time >= ? AND '
            querylist.extend([v[0], v[1], v[1]])
        
        elif k == 'near':
            where_query += ' distance <= ? AND '
            querylist.append(v[2])
            

    myquery = select_query + where_query 
    myquery = myquery[ : -5]


    cursor.execute(myquery, querylist)
    for row in cursor.fetchall():
        answer.append(row)
    

    return answer
  

    
    