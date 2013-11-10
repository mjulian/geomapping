#!/usr/bin/python
# Created by Mike Julian (mike@mikejulian.com)
# Requirements: pygeocoder, simplekml -- Install both via PyPi
# Usage: 'python createMap.py' from the command line

from pygeocoder import Geocoder
import simplekml
import time
import MySQLdb
import sys
import socket

CARBON_SERVER = "graphite"
CARBON_PORT = 2003
ADDRESSES_FILE = "addresses.txt"
KML_FILE = "members.kml"
SQL_HOST = "host"
SQL_USER = "user"
SQL_PASSWORD = "password"
SQL_DATABASE = "database"

def grab_data():
    con = MySQLdb.Connection('SQL_HOST', 'SQL_USER', 'SQL_PASSWORD', 'SQL_DATABASE')
    cursor = con.cursor()
    sql = "select civicrm_address.city, civicrm_address.postal_code from civicrm_address, civicrm_membership where civicrm_address.contact_id=civicrm_membership.contact_id and civicrm_membership.status_id='2';"
    cursor.execute(sql)
    result = cursor.fetchall()
    output_file = open(ADDRESSES_FILE, 'a')
    for geo1,geo2 in result:
        print "%s,%s" % (geo1, geo2)
        output_file.write(geo1,geo2)
    output_file.close()

def create_map(address_file):
    kml = simplekml.Kml(open=1)
    points = []

    # Open our input file, read each line and strip line break characters
    with open(ADDRESSES_FILE) as file:
        lines = file.read().splitlines()
    file.close()

    for address in lines:
        if "None" in address:
            print "Not mapped %s" % address
            continue
        else:
            points.append(Geocoder.geocode(address).coordinates)
        # If an exception is encountered (eg, no matches), the program will stop.
        # This tells it to ignore exceptions
        except:
            print "NOT MAPPED %s" % address
            pass
        # Throttle the lookup in seconds. Google gets upset if you don't.
        time.sleep(0.25)

    for lat,lon in points:
        pnt = kml.newpoint()
        pnt.name = "Member"
        # pygeocoder outputs as lat,lon, while the KML needs lon, lat
        pnt.coords = [(lon, lat)]

    kml.save(KML_FILE)

if __name__ == "__main__":
    grab_data()
    create_map()
