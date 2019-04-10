import sqlite3
from sqlite3 import Error
import logging
import devices
import zones

def execute_program(conn):
    #Initialize
    zon = zones.Zones(conn)
    zon.populate_zone_list()
    dev = devices.Devices(conn)
    dev.populate_device_list()

    #Other stuff

    #for device in dev.devices:
    #    points = timestamps = dev.get_device_info(device)
    #    points = zon.extract_coordinates(points)
    #    points = [[float(j) for j in i] for i in points]

    '''
    points, timestamps = dev.get_device_info(dev.devices[900])
    points = zon.extract_coordinates(points)
    points = [[float(j) for j in i] for i in points]

    zon.check_specific_zones(points, timestamps)
    print(str(len(points)))
    '''

    '''
    times = []
    for i in range(len(points)):
        if (zon.check_in_zone(zon.zones[4], (points[i][0], points[i][1]))):
            times.append(timestamps[i])
    
    if len(times) > 2:
        totaltime = times[-1] - times[0]
        print(totaltime)
    '''


    return


def create_connection(db_file):
    '''
    Create connection with the sqlite3 database
    '''
    try:
        conn = sqlite3.connect(db_file)
        return conn
    except Error as e:
        logging.critical("Failed to access the database!")
        print(e)
    return None


def main():
    logging.basicConfig(level=logging.DEBUG)
    database = "./sensor_data.db"
    conn = create_connection(database)

    with conn:
        execute_program(conn)

if __name__ == '__main__':
    main()