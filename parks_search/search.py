import sqlite3
import re
from .db import haversine_distance

def regexp(pattern, subject):
    reg = re.compile(pattern)
    return reg.search(subject) is not None

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

    answer = []
    querylist = []

    connection = sqlite3.connect('data/parks.db')
    connection.row_factory = sqlite3.Row       
    connection.create_function('haversine_distance', 4, haversine_distance)
    connection.create_function('regexp', 2, regexp)
    cursor = connection.cursor()
    

    myquery = 'SELECT '
    if 'near' in params.keys():
        myquery = myquery + 'haversine_distance(?, ?, latitude, longitude) AS distance, '
        querylist.extend([params['near'][0],params['near'][1]])
    myquery = myquery + 'parks.name, parks.description, parks.history, parks.address, parks.url '
    if 'open_at' in params.keys():
        myquery = myquery + ', park_times.day, park_times.open_time, park_times.close_time FROM parks JOIN park_times ON parks.id = park_times.park_id WHERE '
    else:
        myquery = myquery + 'FROM parks WHERE '
    for k,v in params.items():
        if k == 'open_at':
            myquery = myquery + ' day = ? AND open_time <= ? AND close_time >= ? AND '
            querylist.extend([v[0],v[1],v[1]])
        elif k == 'name':
            myquery = myquery + ' name like ' + '\'' + v + '%\' AND '
        elif k == 'query_terms':
            for i in v:
                myquery = myquery + " tokens regexp '[.]* " + i + " [.]*' AND "
        elif k == 'zip_code':
            myquery = myquery + " address regexp '[.]*" + v + "[.]*' AND "
        elif k == 'near':
            myquery = myquery + 'distance <= ? AND '
            querylist.append(v[2])

    myquery = myquery[:-5] 


    cursor.execute(myquery,querylist)
    for row in cursor.fetchall():
        answer.append(row)

    return answer