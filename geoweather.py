#!/usr/bin/python

import sys, urllib2, os.path
import pygeoip

cache_dir = os.path.expanduser('~') + '/.geoweather'


def getExternalIP():
    src = 'http://www.whatismyip.com/automation/n09230945.asp'
    ip_cache = cache_dir + '/ip.txt'

    # Use cached data if we checked recently, otherwise hit src.

    return urllib2.urlopen(src).read()


def getLoc():
    geodata = cache_dir + '/GeoLiteCity.dat'
    try:
        gic = pygeoip.GeoIP(geodata)
    except:
        print "Unable to open the GeoIP database at %s." % geodata
        sys.exit(1)

    loc = gic.record_by_addr(getExternalIP())
    return (loc['city'], loc['region_name'])


def main():
    city, state = getLoc()
    print "%s, %s" % (city, state)


if __name__ == "__main__":
    main()
