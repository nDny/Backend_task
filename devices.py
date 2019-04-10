import logging

class Devices(object):

    def __init__(self, conn):
        self.devices = []
        self.conn = conn

    def populate_device_list(self):
        '''
        Create a list of all unique device ids
        '''
        cur = self.conn.cursor()
        cur.execute("SELECT device_id FROM positions")

        rows = cur.fetchall()

        for device in rows: 
            if device not in self.devices:
                self.devices.append(device[0])
                    
        #logging.info("\nNumber of devices: " + str(len(self.devices)))

    def get_device_info(self, device_id):
        '''
        Get the timestamps and positions of given device, returned as a tuple
        '''
        cur = self.conn.cursor()
        cur.execute("SELECT timestamp, position FROM positions WHERE device_id = ?", (device_id,))

        rows = cur.fetchall()
        timestamps = []
        points = ""
        for row in rows:
            timestamps.append(row[0])
            points += (row[1])
        return points, timestamps