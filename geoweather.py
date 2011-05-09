#!/usr/bin/python

import sys, urllib2, os, datetime
import pygeoip

cache_dir = os.path.expanduser('~') + '/.geoweather'


# Returns true if the cache is valid, false if the cache has expired or doesn't exist.
def valid_cache(cache, timeout):
    cache_timeout = datetime.timedelta(seconds=timeout)

    try:
        stat = os.stat(cache)
        ctime = datetime.datetime.fromtimestamp(stat.st_ctime)
    except:
        return False

    if datetime.datetime.today() < ctime + cache_timeout:
        return True
    else:
        return False


def getExternalIP():
    src = 'http://www.whatismyip.com/automation/n09230945.asp'
    ip_cache = cache_dir + '/ip.txt'
    cache_timeout = 300

    if valid_cache(ip_cache, cache_timeout):
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


def getWeather(zip=None):
    weather_cache = cache_dir + '/weather.txt'
    cache_timeout = 1800

    if valid_cache(weather_cache, cache_timeout):
        print "Using cached weather"
        f = open(weather_cache, 'r')
        weather = f.readlines()
    else:
        src = "http://mobile.weather.gov/port_zc.php?inputstring=%s&Go2=Go" % getLoc()
        weather = urllib2.urlopen(src).read()
        f = open(weather_cache, 'w')
        f.write("%s\n" % weather)

    f.close()
    return weather


def main():
    print getWeather()


if __name__ == "__main__":
    main()
