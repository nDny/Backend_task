import re
import numpy
import matplotlib

class Zones(object):


    def __init__(self, conn):
        self.zones = []
        self.conn = conn


    def populate_zone_list(self):
        zones = []
        zoneInfo = {}
        cur = self.conn.cursor()
        cur.execute("SELECT id, polygon FROM zones")

        rows = cur.fetchall()

        for row in rows:
            zoneInfo[row[0]] = row[1][1:-1]
        
        for key, val in zoneInfo.items():
            zones.append(self.extract_coordinates(val))


    def extract_coordinates(self, zoneCoords):
        '''
        Make regex to extract the coordinates from the database string.
        Using python list comprehension, iterate through this list to get 2d array 
        where every coordinate is accessible separately
        ''' 
        pattern = re.compile("\((.*?)\)")
        coordList = [[tup for tup in t.split(",")] for t in pattern.findall(zoneCoords)]
        return coordList
    

    def check_in_zone(self, zoneCoords, point):
        '''
        Takes in 2d array and converts it to numpy array.
        Using matplotlib trace a path of the polygon
        and check if specified point is inside said polygon
        '''
        polyNumpy = numpy.array(zoneCoords)
        polyPath = matplotlib.path.Path(polyNumpy)
        return(polyPath.contains_point(point))
