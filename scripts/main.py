import sqlite3
from sqlite3 import Error
import logging
import sys
import devices
import zones


def insert_zone_visit(conn, zoneInfo):
    conn.execute("INSERT INTO zone_visits(device_id,start_time,end_time,zone_id) VALUES(?,?,?,?)", zoneInfo)
    return

def execute_program(conn):
    '''
    Iterate everything to achieve the final result
    '''
    #Initialize
    logging.info("Initializing")
    logging.debug("Debug mode enabled")
    logging.info("Retrieving data from database")

    zone = zones.Zones(conn)
    zone.populate_zone_list()
    dev = devices.Devices(conn)
    dev.populate_device_list()
    logging.info("\nLists populated\n")

    #Run every known position for each device through each of the zone polygons
    count = 0
    logging.info("Running")
    for device in dev.devices:
        count += 1
        logging.info("Device #"+str(count)+" "+device)
        points, timestamps = dev.get_device_info(device)
        points = zone.extract_coordinates(points)
        points = [[float(j) for j in i] for i in points]
        results = zone.check_specific_zones(points, timestamps, device)

        if results:
            logging.debug("Inserting device #" + str(count) + " into database")
        for res in results:
            insert_zone_visit(conn, res)

        #if count > 9:
        #    break
    
    logging.info("Execution finished successfully")
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
    '''
    Start program, check for args
    '''
    if len(sys.argv) > 1:
        if sys.argv[1] == "-v" or sys.argv[1] == "--verbose":
            print("Verbose mode enabled")
            logging.basicConfig(level=logging.DEBUG)

        elif sys.argv[1] == "-h" or sys.argv[1] == "--help":
            print("Add option -v or --verbose for output information")
            logging.basicConfig(level=logging.WARNING)
    else:
        print("No args given, output will be silent.")
        logging.basicConfig(level=logging.WARNING)

    #URL to database
    database = "./platform_engineer_2018_interview.db"
    conn = create_connection(database)

    with conn:
        execute_program(conn)
    
    conn.close()

if __name__ == '__main__':
    main()