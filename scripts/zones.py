import re
import numpy
import logging
import sqlite3
import matplotlib.path as mplib


class Zones(object):
    TIMEOUT_LIMIT = 5000

    def __init__(self, conn):
        self.zones = {}
        self.conn = conn

    def populate_zone_list(self):
        '''
        Create a list of all available zones
        '''
        rows = None
        try:
            cur = self.conn.cursor()
            cur.execute("SELECT id, polygon FROM zones")
            rows = cur.fetchall()
        except sqlite3.Error as e:
            logging.warning("SQL query failed: " + e)
        
        # Remove the first and last character per polygon string since they are always '(' and ')'
        # and pass it to extract_coordinates() to get it as a list
        for row in rows:
            self.zones[row[0]] = self.extract_coordinates(row[1][1:-1])

    def extract_coordinates(self, coords):
        '''
        Make regex to extract the coordinates from the database string.
        Using python list comprehension, iterate through this list to
        get 2d array where every coordinate is accessible separately
        ''' 
        pattern = re.compile(r"\((.*?)\)")
        coord_list = [[tup for tup in t.split(",")] for t in pattern.findall(coords)]
        return coord_list
    
    def check_in_zone(self, zone_coords, point):
        '''
        Takes in 2d array and converts it to numpy array.
        Using matplotlib trace a path of the polygon
        and check if specified point is inside said polygon
        '''
        numpy_polygon_array = numpy.array(zone_coords)
        polygon_path = mplib.Path(numpy_polygon_array)
        return polygon_path.contains_point(point)


    def get_final_device_data(self, point_list, timestamps, device_id):
        device_data = []
        final_device_data = []
        curr_zone = 0
        first_stamp = 0
        last_stamp = 0

        # Create a list of timestamps and the corresponding zone
        for point, timestamp in zip(point_list, timestamps):
            curr_zone = self.iterate_zones(point)
            # Skip if point is outside a zone
            if curr_zone is None:
                continue
            device_data.append([curr_zone, timestamp])

        # Check zone visits and extract appropriate data
        for i in range(len(device_data)):
            # First case
            if i < 1:
                first_stamp = device_data[i][1]

            # Check if device moved to different zone
            if device_data[i][0] != device_data[i-1][0]:
                last_stamp = device_data[i][1]
                final_device_data.append([device_id, first_stamp, last_stamp, device_data[i-1][0]])
                first_stamp = device_data[i][1]
            
            # Check if device timed out 
            if device_data[i][1] - first_stamp > self.TIMEOUT_LIMIT:
                logging.debug("Device " + device_id + " timed out in zone " + str(device_data[i][0]))
                last_stamp = device_data[i][1]
                final_device_data.append([device_id, first_stamp, last_stamp, device_data[i-1][0]])
                # Set i to the start of the next zone
                for j in range(i, len(device_data)):
                    if device_data[i][0] != device_data[j][0]:
                        first_stamp = device_data[j][1]
                        i = j
                        break
        return final_device_data


    def iterate_zones(self, point):
        # Check which zone a given point is in
        for zone_id, zone in self.zones.items():
            if self.check_in_zone(zone, point):
                return zone_id
