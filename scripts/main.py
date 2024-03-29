import sqlite3
import logging
import sys
import devices
import zones

DATABASE_PATH = "../platform_engineer_2018_interview.db"


def insert_zone_visit(conn, zone_info):
    try:
        conn.execute("INSERT INTO zone_visits(device_id,start_time,end_time,zone_id) VALUES(?,?,?,?)", zone_info)
    except sqlite3.Error as e:
        logging.warning("SQL query failed: " + e)


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

    # Check if device positions are in a zone and gather the necessary data
    count = 0
    logging.info("Running")
    for device in dev.devices:
        count += 1
        logging.info("Checking device #"+str(count)+" "+device)
        points, timestamps = dev.get_device_info(device)
        points = zone.extract_coordinates(points)
        points = [[float(j) for j in i] for i in points]
        results = zone.get_final_device_data(points, timestamps, device)

        if results:
            logging.debug("Inserting device #" + str(count) + " into database")
        for res in results:
            insert_zone_visit(conn, res)
    
    logging.info("Execution finished successfully")
    return


def create_connection(db_file):
    '''
    Create connection with the sqlite3 database
    '''
    try:
        conn = sqlite3.connect('file:'+db_file+'?mode=rw', uri=True)
        return conn
    except sqlite3.Error as e:
        logging.critical("Failed to access the database. Is the path correct?")
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
    database = DATABASE_PATH
    conn = create_connection(database)

    with conn:
        execute_program(conn)
    
    conn.close()


if __name__ == '__main__':
    main()