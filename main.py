import sqlite3
from sqlite3 import Error
import logging
import devices
import zones

def execute_program(conn):
    zon = zones.Zones(conn)
    dev = devices.Devices(conn)
    dev.populate_device_list()
    zon.populate_zone_list()
    dev.get_device_info(dev.devices[612])
    return

def create_connection(db_file):
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