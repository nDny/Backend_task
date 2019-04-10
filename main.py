import sqlite3
from sqlite3 import Error
import matplotlib.path as mplPath
import numpy as np
import re
import logging


def create_connection(db_file):
    try:
        conn = sqlite3.connect(db_file)
        return conn
    except Error as e:
        print(e)
    return None

def get_devices(conn):
    cur = conn.cursor()
    cur.execute("SELECT device_id, timestamp, position FROM positions")

    rows = cur.fetchall()
    
    devices = []
    deviceInfo = []
    entries = 0

    for row in rows: 
        deviceInfo.append(row)
        if row[0] not in devices:
            devices.append(row[0])

    for dev in devices:
        for row in deviceInfo:
            if dev == row[0]:
                entries += 1
                logging.debug(dev + ": " + str(row[1]) + ", zone: " + row[2])
        logging.debug("\n")
                

    logging.info("\nNumber of devices: " + str(len(devices)))
    logging.info("\nTotal entries: " + str(len(deviceInfo)))

def get_all_zones(conn):
    zones = []
    zoneInfo = {}
    cur = conn.cursor()
    cur.execute("SELECT id, polygon FROM zones")

    rows = cur.fetchall()

    for row in rows:
        zoneInfo[row[0]] = row[1][1:-1]
    
    for key, val in zoneInfo.items():
        zones.append(extract_coordinates(val))

    print(zones[0][0][0])


def extract_coordinates(listOfCoords):
    #Make regex to extract the coordinates from the database string 
    pattern = re.compile("\((.*?)\)")
    #Using python list comprehension, iterate through this list to get 2d array with every coord accessible
    coordList = [[tup for tup in t.split(",")] for t in pattern.findall(listOfCoords)]
    return coordList


def check_in_zone(coordList):
    '''
    Takes in 2d array and converts it to numpy array.
    Using matplotlib trace a path of the polygon
    and check if specified point is inside said polygon
    '''
    polygon = coordList
    polyNumpy = np.array(polygon)

    polyPath = mplPath.Path(polyNumpy)
    print(polyPath.contains_point((59.24213618155,34.28641435502)))




def main():
    logging.basicConfig(level=logging.DEBUG)
    database = "./sensor_data.db"

    #check_in_zone()

    conn = create_connection(database)
    with conn:
        #get_all_zones(conn)
        get_devices(conn)

if __name__ == '__main__':
    main()