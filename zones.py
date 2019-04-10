import re
import numpy
import logging
import matplotlib.path as mplib

class Zones(object):
    TIME_LIMIT = 6000

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

        #Remove the first and last character per polygon string since they are always '(' and ')'
        for row in rows:
            self.zones[row[0]] = self.extract_coordinates(row[1][1:-1])
        
        #for key, val in zoneInfo.items():
        #    self.zones.append(self.extract_coordinates(val))


    def extract_coordinates(self, coords):
        '''
        Make regex to extract the coordinates from the database string.
        Using python list comprehension, iterate through this list to get 2d array 
        where every coordinate is accessible separately
        ''' 
        pattern = re.compile("\((.*?)\)")
        coordList = [[tup for tup in t.split(",")] for t in pattern.findall(coords)]
        return coordList
    

    def check_in_zone(self, zoneCoords, point):
        '''
        Takes in 2d array and converts it to numpy array.
        Using matplotlib trace a path of the polygon
        and check if specified point is inside said polygon
        '''
        polyNumpy = numpy.array(zoneCoords)
        polyPath = mplib.Path(polyNumpy)
        return(polyPath.contains_point(point))

    
    def check_specific_zones(self, pointList, timestamps, device_id):
        zoneInfo = []
        for zoneID, zone in self.zones.items():
            time_spent = []
            for i in range(len(pointList)):
                if self.check_in_zone(zone, pointList[i]):
                    time_spent.append(timestamps[i])
                    if len(time_spent) > 1: 
                        if (time_spent[len(time_spent)-1] - time_spent[0]) > self.TIME_LIMIT:
                            logging.info("Time limit reached") 
                            break
            if len(time_spent) == 0:
                continue
            elif len(time_spent) > 1:
                zoneInfo.append([device_id, int(time_spent[0]), int(time_spent[-1]), int(zoneID)])
                #print("Zone:", zoneID, "--- Starttime:", time_spent[0], ", Endtime:", time_spent[-1])
            elif len(time_spent) == 1:
                zoneInfo.append([device_id, int(time_spent[0]), int(time_spent[0]), int(zoneID)])
                #print("Zone:", zoneID,"--- Start- and endtime: ", time_spent[0])
            else:
                logging.warning("Failed to recognize time data")
        return zoneInfo