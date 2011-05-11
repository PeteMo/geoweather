#!/usr/bin/python

import sys, urllib2, os, datetime, base64
import pygeoip
from BeautifulSoup import BeautifulSoup

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


# Returns the contents of url, possibly from a cache.
def getHtml(url, cache_timeout=0):
    cache_loc = os.path.join(cache_dir, base64.urlsafe_b64encode(url))

    if valid_cache(cache_loc, cache_timeout):
        print "Fetching %s from cache" % url
        f = open(cache_loc, 'r')
        html = f.read()
    else:
        html = urllib2.urlopen(url).read()
        f = open(cache_loc, 'w')
        f.write("%s\n" % html)
    f.close()

    return html


def getExternalIP():
    src = 'http://www.whatismyip.com/automation/n09230945.asp'
    cache_timeout = 300
    return getHtml(src, cache_timeout)


def getLoc():
    geodata = cache_dir + '/GeoLiteCity.dat'
    try:
        gic = pygeoip.GeoIP(geodata)
    except:
        print "Unable to open the GeoIP database at %s." % geodata
        sys.exit(1)

    loc = gic.record_by_addr(getExternalIP())
    return loc['postal_code']


def getWeather(zcode):
    baseurl = 'http://mobile.weather.gov'
    cache_timeout = 1800

    # The main page contains links to the forecast and the current conditions.
    main_loc = "%s/port_zc.php?inputstring=%s&Go2=Go" % (baseurl, zcode)
    main = getHtml(main_loc, cache_timeout)

    # Follow the links to the forecast and current conditions.
    soup = BeautifulSoup(main)
    links = [each.get('href') for each in soup.findAll('a')]
    forecast = getHtml("%s/%s" % (baseurl,links[0]), cache_timeout)
    current = getHtml("%s/%s" % (baseurl,links[2]), cache_timeout)
    return forecast, current


def main():
    if len(sys.argv) == 2:
        loc = sys.argv[1]
    else:
        loc = getLoc()

    forecast, current = getWeather(loc)
    soup = BeautifulSoup(forecast)
    print soup.prettify()
    print
    soup = BeautifulSoup(current)
    print soup.prettify()


if __name__ == "__main__":
    main()
