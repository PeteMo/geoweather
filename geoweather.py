#!/usr/bin/python

import sys, os, urllib2, urllib, datetime, base64, xml.dom.minidom
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


# Returns the contents of url, possibly from a cache.
def getHtml(url, cache_timeout=0):
    cache_loc = os.path.join(cache_dir, base64.urlsafe_b64encode(url))

    if valid_cache(cache_loc, cache_timeout):
#        print "Fetching %s from cache" % url
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


def getLocByIP():
    geodata = cache_dir + '/GeoLiteCity.dat'
    try:
        gic = pygeoip.GeoIP(geodata)
    except:
        print "Unable to open the GeoIP database at %s." % geodata
        sys.exit(1)

    loc = gic.record_by_addr(getExternalIP())
    return loc['postal_code'], loc['city'] + ", " + loc['region_name']


def getCurrent(loc):
    baseurl = 'http://api.wunderground.com/auto/wui/geo/WXCurrentObXML/index.xml?%s'
    query = urllib.urlencode({'query' : loc})
    cache_timeout = 1800

    wxml = getHtml(baseurl % query, cache_timeout)
    dom = xml.dom.minidom.parseString(wxml)

    for node in dom.getElementsByTagName("current_observation"):
        location = node.getElementsByTagName("full")[0].childNodes[0].nodeValue
        if location == ", ":
            print "Invalid location " + loc
        else:
            print "Current Conditions for " + location
            print node.getElementsByTagName("weather")[0].childNodes[0].nodeValue
            print node.getElementsByTagName("temp_f")[0].childNodes[0].nodeValue + " F"
            print "Wind " + node.getElementsByTagName("wind_string")[0].childNodes[0].nodeValue
            print node.getElementsByTagName("relative_humidity")[0].childNodes[0].nodeValue + " Humidity"
            print


def getForecast(loc):
    baseurl = 'http://api.wunderground.com/auto/wui/geo/ForecastXML/index.xml?%s'
    query = urllib.urlencode({'query' : loc})
    cache_timeout = 1800

    wxml = getHtml(baseurl % query, cache_timeout)
    dom = xml.dom.minidom.parseString(wxml)

    for node in dom.getElementsByTagName("forecastday"):
        day = node.getElementsByTagName("title")
        if day:
            print day[0].childNodes[0].nodeValue
            forecast = node.getElementsByTagName("fcttext")[0]
            print forecast.childNodes[0].nodeValue + '\n'
            

def main():
    if len(sys.argv) == 2:
        zcode = loc = sys.argv[1]
    else:
        zcode, loc = getLocByIP()

    getCurrent(zcode)
    getForecast(zcode)
    

if __name__ == "__main__":
    main()
