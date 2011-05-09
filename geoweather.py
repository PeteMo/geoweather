#!/usr/bin/python

import urllib2, pygeoip, os.path

cache_dir = os.path.expanduser('~') + '/.geoweather'
geodata = cache_dir + '/GeoLiteCity.dat'


def getExternalIP():
    src = 'http://www.whatismyip.com/automation/n09230945.asp'
    return urllib2.urlopen(src).read()


ip = getExternalIP()
gic = pygeoip.GeoIP(geodata)
loc = gic.record_by_addr(ip)

print "%s, %s %s" % (loc['city'], loc['region_name'], loc['postal_code'])
