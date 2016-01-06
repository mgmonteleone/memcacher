__author__ = 'mgm'
import sys
import urllib2
import yaml
import json
from libs import statsd
from libs.pymemcache.client import Client
from libs.termcolor import colored, cprint
print_error = lambda x: cprint(x,"red","on_grey")
print_warn = lambda x: cprint(x,"yellow","on_grey")
print_ok = lambda x: cprint(x,"green","on_grey")
print_info = lambda x: cprint(x,"blue","on_grey")

class CustomException(Exception):
    def __init__(self, value):
        self.parameter = value

    def __str__(self):
        return repr(self.parameter)


try:
    configfile = open("/etc/memcacher/config.yaml", "r")
    config = yaml.load(configfile)
    mcservers = config["mcservers"]
    datadogenabled = config["datadogenabled"]
    logto = config["logto"]

except IOError, (instance):
    raise CustomException("Could not find the required configuration file expected at /etc/memcacher/config.yaml")
    print_error("Configuration Error !!")


class ContentItem(object):
    def __init__(self, uri, content=None, size=None, contenttype=None):
        self.uri = uri
        self.content = content
        self.size = size
        self.contenttype = contenttype


def getcontent(upstream, uri):
    """
    Retrieves a file from the given url, from the defined base url.
    :rtype : ContentItem(object)
    :param uri: the uri to be retrieved
    :return:
    """
    print_info("Retrieving url: " + upstream + uri)
    try:
        resource = urllib2.urlopen(upstream + uri, None, config["fetchtimeout"])
    except IOError as e:
        print e.message
        print_error( "--Timed out when retrieving item, consider lengthening timeout.--")

        return ContentItem(uri, None, 0, None)
    if resource.getcode() not in [404, 500]:
        meta = resource.info()
        try:
            content = resource.read()
            try:
                size = int(meta.getheaders("Content-Length")[0])
            except:
                size = len(content)/1000
            try:
                contenttype = meta.getheaders("Content-Type")[0]
            except:
                contenttype = "text/html"

            print_ok( "Retrieved " + str(size) + "kB")
            return ContentItem(uri, content, size, contenttype)
        except Exception as e:
            print_warn("--Could not parse the received object, length or contenttype was bad...--")
            print_warn(e.message)
            return ContentItem(uri, None, 0, None)
    else:
        print_warn("----Can not retrieve resource----")
    return ContentItem(uri, None, 0, None)


def putitemincache(baseurl, upstream, uri, expires, prefix):
    """
    Puts a single content item, specified by a uri, into the designated

    :rtype : str
    :param baseurl: The base of the query
    :param upstream: The upstream base to pull from
    :param uri: the uri of the resource to retrieve and store
    :param expires: object expiration time, in seconds
    :param prefix: the prefix to append to the uri to create the key in memcached, this is the key that needs to be appended in NGINX
    :return: Returns the content of the item retrieved, to enable integration to LB.
    """
    # Lets retrieve the item first....
    contentitem = getcontent(upstream=upstream, uri=uri)
    if contentitem.size > 0:
        # First delete the item from memcache
        for key, value in mcservers.iteritems():
            print("Processing Server: " + key + " port " + str(value))
            try:
                mc = Client((key, value))
            except IOError:
                raise
            try:
                print "Deleting " + prefix + uri
                mc.delete(prefix + uri)
            except IOError:
                raise
        for key, value in mcservers.iteritems():
            print "Processing Server: " + key + " port " + str(value)
            try:
                mc = Client((key, value))
            except IOError:
                raise
            try:
                print_ok( "Setting " + prefix + contentitem.uri)
                mc.set(prefix + contentitem.uri, contentitem.content, expires)
                if datadogenabled == True:
                    #Do instrumentation
                    tags = 'siteurl: '+ baseurl
                    statsd.statsd.increment("memcacher.cached_bytes",contentitem.size,tags=[tags])
                    statsd.statsd.increment("memcacher.cached_page",1,tags=[tags])
            except IOError:
                raise
        return contentitem.content
    else:
        print_warn( "----The item with uri: " + uri + " could not be retrieved----")
        return


def putitemsincache(baseurl, uris):
    """
    Grabs the content from a passed list urls, puts them into all configured memcached servers.
    First retrieves from the site, then processes each file.
    :param baseurl: The base URL to fetch from
    :param uris: a list of URLIS
    """
    try:
        for uri in uris:
            print "Processing " + uri
            putitemincache(baseurl, uri, config["expire_secs"])
    except IOError:
        raise
