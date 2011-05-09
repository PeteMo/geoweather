#!/usr/bin/python

import sys, urllib2, os, datetime
import pygeoip

cache_dir = os.path.expanduser('~') + '/.geoweather'


def getExternalIP():
    src = 'http://www.whatismyip.com/automation/n09230945.asp'
    ip_cache = cache_dir + '/ip.txt'
    cache_timeout = datetime.timedelta(seconds=300)

    # Get the last modified time from the cache file if it exists; otherwise, 
    # fake the mtime to ensure the cache is created.
    try:
        stat = os.stat(ip_cache)
        mtime = datetime.datetime.fromtimestamp(stat.st_mtime)
    except OSError:
        mtime = datetime.datetime(1980, 01, 01)

    # Use the cache if it is valid.
    if datetime.datetime.today() < mtime + cache_timeout:
        print "Using cached IP"
        f = open(ip_cache, 'r')
        ip = f.readline()
    else:
        ip = urllib2.urlopen(src).read()
        f = open(ip_cache, 'w')
        f.write("%s\n" % ip)

    f.close()
    return ip


def getLoc():
    geodata = cache_dir + '/GeoLiteCity.dat'
    try:
        gic = pygeoip.GeoIP(geodata)
    except:
        print "Unable to open the GeoIP database at %s." % geodata
        sys.exit(1)

    loc = gic.record_by_addr(getExternalIP())
    return loc['postal_code']


def getWeather(zip):
    src = "http://mobile.weather.gov/port_zc.php?inputstring=%s&Go2=Go" % zip
    weather = urllib2.urlopen(src).read()
    return weather


def main():
    zip = getLoc()
    print getWeather(zip)


if __name__ == "__main__":
    main()
