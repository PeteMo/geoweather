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


# Returns the contents of url, possibly from a cache.
def getHtml(url):
    cache_timeout = 1800
    cache_loc = os.path.join(cache_dir, base64.urlsafe_b64encode(url))

    if valid_cache(cache_loc, cache_timeout):
        f = open(cache_loc, 'r')
        html = f.readlines()
    else:
        html = urllib2.urlopen(url).read()
        f = open(cache_loc, 'w')
        f.write("%s\n" % html)
    f.close()

    return html


def getWeather(zip=None):
    baseurl = 'http://mobile.weather.gov'
    cache_timeout = 1800

    # The main page contains links to the forecast and the current conditions.
    main_loc = "%s/port_zc.php?inputstring=%s&Go2=Go" % (baseurl, getLoc())
    main = getHtml(main_loc)

    # Follow the links to the forecast and current conditions.
    soup = BeautifulSoup(' '.join(main))
    links = [each.get('href') for each in soup.findAll('a')]
    forecast = getHtml("%s/%s" % (baseurl,links[0]))
    current = getHtml("%s/%s" % (baseurl,links[2]))
    return forecast, current


def main():
    forecast, current = getWeather()
    soup = BeautifulSoup(' '.join(forecast))
    print soup.prettify()
    print
    soup = BeautifulSoup(' '.join(current))
    print soup.prettify()


if __name__ == "__main__":
    main()
