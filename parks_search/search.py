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

    # opening a connection to the database and registering the haversine_distance
    connection = sqlite3.connect('data/parks.db')
    connection.create_function('haversine_distance', 4, haversine_distance)
    connection.row_factory = sqlite3.Row        
    cursor = connection.cursor()

    # track the query objects
    answer = []
    querylist = []

    select_query = 'SELECT'
    where_query = ' WHERE '

    # confirm the select query 
    # 1. haversine_distance 
    if 'near' in params:
        select_query += ' haversine_distance(?, ?, latitude, longitude) AS distance, p.name, p.address, p.description, p.history, p.url '
        querylist.extend([params['near'][0], params['near'][1]])
    else:
        select_query += ' p.name, p.address, p.description, p.history, p.url '
    # 2. join two tables or not
    if 'open_at' in params:
        select_query += ', t.day, t.open_time, t.close_time FROM parks as p JOIN park_times as t ON p.id = t.park_id' 
    else:
        select_query += 'FROM parks as p'
    
    # run through params
    for k, v in params.items():
        if k == 'name':
            where_query += ' name LIKE ? AND '
            name = v + '%'
            querylist.append(name)
        
        elif k == 'query_terms':
            for token in v:
                where_query += ' tokens LIKE ? AND '
                token = '% ' + token + ' %'
                querylist.append(token)

        elif k == 'zip_code':
            where_query += ' address LIKE ? AND '
            zipcode = '%' + v + '%'
            querylist.append(zipcode)

        elif k == 'open_at':
            where_query += ' day = ? AND open_time <= ? AND close_time >= ? AND '
            day = v[0]
            open_time = v[1]
            close_time = v[1]
            querylist.extend([day, open_time, close_time])
        
        elif k == 'near':
            where_query += ' distance <= ? AND '
            distance = v[2]
            querylist.append(distance)
            
    # intergrate the queries
    myquery = select_query + where_query 
    # get rid of the last " AND "
    myquery = myquery[ : -5]

    # execute and fetchall
    cursor.execute(myquery, querylist)
    for row in cursor.fetchall():
        answer.append(row)

    return answer
