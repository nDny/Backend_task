import logging
import sqlite3

class Devices(object):

    def __init__(self, conn):
        self.devices = []
        self.conn = conn


    def populate_device_list(self):
        '''
        Create a list of all unique device ids
        '''
        rows = None
        try:
            cur = self.conn.cursor()
            cur.execute("SELECT device_id FROM positions")
            rows = cur.fetchall()
        except sqlite3.Error as e:
            logging.warning("SQL query failed: " + e)

        for device in rows: 
            if device[0] not in self.devices:
                self.devices.append(device[0])
        
        logging.info("\nNumber of devices: " + str(len(self.devices)))


    def get_device_info(self, device_id):
        '''
        Get the timestamps and positions of given device, returned as a tuple
        '''
        rows = None
        try:
            cur = self.conn.cursor()
            cur.execute("SELECT timestamp, position FROM positions WHERE device_id = ?", (device_id,))

            rows = cur.fetchall()
        except sqlite3.Error as e:
            logging.warning("SQL query failed: " + e)

        timestamps = []
        points = ""
        for row in rows:
            timestamps.append(row[0])
            points += (row[1])
        return points, timestamps