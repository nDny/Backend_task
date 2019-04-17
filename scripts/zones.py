import re
import numpy
import logging
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
        cur = self.conn.cursor()
        cur.execute("SELECT id, polygon FROM zones")

        rows = cur.fetchall()

        # Remove the first and last character per polygon string since they are always '(' and ')'
        # and pass it to extract_coordinates to get it as a list
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
        dev_data = []
        final_device_info = []
        curr_zone = 0
        first_stamp = 0
        last_stamp = 0

        for point, timestamp in zip(point_list, timestamps):
            curr_zone = self.iterate_zones(point)
            # Skip if point is outside a zone
            if curr_zone is None:
                continue
            dev_data.append([curr_zone, timestamp])

        for i in range(len(dev_data)):
            # First case
            if i < 1:
                first_stamp = dev_data[i][1]

            # Check if device moved to different zone
            if dev_data[i][0] != dev_data[i-1][0]:
                last_stamp = dev_data[i][1]
                final_device_info.append([device_id, first_stamp, last_stamp, dev_data[i-1][0]])
                first_stamp = dev_data[i][1]
            
            # Check if device timed out, then set i to the start of the next zone
            if dev_data[i][1] - first_stamp > self.TIMEOUT_LIMIT:
                last_stamp = dev_data[i][1]
                final_device_info.append([device_id, first_stamp, last_stamp, dev_data[i-1][0]])

                for j in range(i, len(dev_data)):
                    if dev_data[i][0] != dev_data[j][0]:
                        first_stamp = dev_data[j][1]
                        i = j
                        break
        return final_device_info


    def iterate_zones(self, point):
        for zone_id, zone in self.zones.items():
            if self.check_in_zone(zone, point):
                return zone_id
