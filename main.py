import sqlite3
from sqlite3 import Error
import logging
import devices
import zones

def insert_zone_visit(conn, zoneInfo):
    conn.execute("INSERT INTO zone_visits(device_id,start_time,end_time,zone_id) VALUES(?,?,?,?)", zoneInfo)
    return

def execute_program(conn):
    #Initialize
    zon = zones.Zones(conn)
    zon.populate_zone_list()
    dev = devices.Devices(conn)
    dev.populate_device_list()

    #Other stuff

    for device in dev.devices:
        points, timestamps = dev.get_device_info(device)
        points = zon.extract_coordinates(points)
        points = [[float(j) for j in i] for i in points]
        results = zon.check_specific_zones(points, timestamps, device)

        for res in results:
            insert_zone_visit(conn, res)

    '''
    points, timestamps = dev.get_device_info(dev.devices[78])
    points = zon.extract_coordinates(points)
    points = [[float(j) for j in i] for i in points]

    results = zon.check_specific_zones(points, timestamps, dev.devices[78])
    for res in results:
        insert_zone_visit(conn, res)
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