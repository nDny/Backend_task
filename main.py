import sqlite3
from sqlite3 import Error
import matplotlib.path as mplPath
import numpy as np
import re


def create_connection(db_file):
    try:
        conn = sqlite3.connect(db_file)
        return conn
    except Error as e:
        print(e)
    
    return None


def get_all_zones(conn):
    cur = conn.cursor()
    cur.execute("SELECT id, polygon FROM zones")

    mydict = {}

    rows = cur.fetchall()

    for row in rows:
        mydict[row[0]] = row[1][1:-1]
    
    #print(mydict[396])
    extract_coordinates(mydict[396])
    #print(mydict)


def extract_coordinates(listOfCoords):
    pat = re.compile("\((.*?)\)")
    coordList = [t.strip() for t in pat.findall(listOfCoords)]
    print(coordList)


def check_in_zone():
    polygon = [[59.241880814564,34.285395115614], 
                [59.241808041218,34.28546820581], 
                [59.242064401143,34.286487445235],
                [59.24213618156,34.28641435504],
                [59.241880814564,34.285395115614]]

    polyNumpy = np.array(polygon)

    polyPath = mplPath.Path(polyNumpy)
    print(polyPath.contains_point((59.24213618155,34.28641435502)))



def main():
    database = "./positiondata.db"

    #check_in_zone()

    conn = create_connection(database)
    with conn:
        get_all_zones(conn)


if __name__ == '__main__':
    main()