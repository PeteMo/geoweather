#!/usr/bin/python
import sys, os, getopt, textwrap
import datetime, base64, xml.dom.minidom
import urllib2, urllib

# http://code.google.com/p/pygeoip/
import pygeoip

cache_dir = os.path.expanduser('~') + '/.geoweather'
geodata = os.path.join(cache_dir, 'GeoLiteCity.dat')

def usage(program):
    print "Usage: %s [-a|-c|-f] [-h] [location]" % os.path.basename(program)
    print "  -a  --all         Both current conditions and the forecast (default)"
    print "  -c  --current     Current conditions"
    print "  -f  --forecast    Forecast"
    print "  -h  --help        Print this help message"
    print "  location          Zip code or city, state; performs geolocation via your"
    print "                    current IP address by default."

# Returns true if the cache is valid, false if the cache has expired or doesn't exist.
def valid_cache(cache, timeout=1800):
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


# Delete all files in the cache older than the cache timeout, except the geodata db.
def clean_cache():
    # Clean the cache of old files.
    for f in os.listdir(cache_dir):
        fp = os.path.join(cache_dir, f)
        if not valid_cache(fp) and fp != geodata:
            os.unlink(fp)


# Returns the contents of url, possibly from a cache.
def getUrl(url, cache_timeout=0):
    cache_loc = os.path.join(cache_dir, base64.urlsafe_b64encode(url))

    if valid_cache(cache_loc, cache_timeout):
        f = open(cache_loc, 'r')
        html = f.read()
    else:
        try:
            html = urllib2.urlopen(url).read()
        except urllib2.URLError, e:
            print e
            sys.exit(1)
        f = open(cache_loc, 'w')
        f.write("%s\n" % html)
    f.close()

    return html


def getExternalIP():
    src = 'http://automation.whatismyip.com/n09230945.asp'
    return getUrl(src, 300)


def getLocByIP():
    try:
        gic = pygeoip.GeoIP(geodata)
    except:
        print "Unable to open the GeoIP database at %s." % geodata
        sys.exit(1)

    loc = gic.record_by_addr(getExternalIP())
    return loc['postal_code']


def getCurrent(loc):
    baseurl = 'http://api.wunderground.com/auto/wui/geo/WXCurrentObXML/index.xml?%s'
    query = urllib.urlencode({'query' : loc})

    wxml = getUrl(baseurl % query)
    dom = xml.dom.minidom.parseString(wxml)

    for node in dom.getElementsByTagName("current_observation"):
        location = node.getElementsByTagName("full")[0].childNodes[0].nodeValue
        if location == ", ":
            print "Invalid location " + loc
            sys.exit(1)
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

    wxml = getUrl(baseurl % query)
    dom = xml.dom.minidom.parseString(wxml)

    for node in dom.getElementsByTagName("forecastday"):
        day = node.getElementsByTagName("title")
        if day:
            print day[0].childNodes[0].nodeValue
            forecast = node.getElementsByTagName("fcttext")[0]
            print textwrap.fill(forecast.childNodes[0].nodeValue, 80) + '\n'
            

def main():
    # Process options.
    try:
        opts, args = getopt.gnu_getopt(sys.argv[1:], "acfh", ["all", "current", "forecast", "help"])
    except getopt.GetoptError, e:
        print str(e)
        usage(sys.argv[0])
        sys.exit(1)

    # Get all weather data by default.
    if len(opts) == 0:
        opts.append(('-a', ''))

    current = False
    forecast = False
    for o, _ in opts:
        if o in ("-a", "--all"):
            current = True
            forecast = True
        elif o in ("-c", "--current"):
            current = True
        elif o in ("-f", "--forecast"):
            forecast = True
        elif o in ("-h", "--help"):
            usage(sys.argv[0])
            sys.exit(0)
        else:
            print "Unknown option " + o
            usage(sys.argv[0])
            sys.exit(1)

    # Process arguments
    if len(args) > 0:
        loc = ' '.join(args)
    else:
        loc = getLocByIP()
        if loc is None:
            print "Unable to determine your location. Try specifying it on the command line."
            sys.exit(0)

    # Print the requested weather data.
    if current:
        getCurrent(loc)
    if forecast:
        getForecast(loc)

    clean_cache()
    

if __name__ == "__main__":
    main()
