__author__ = 'mgm'
import sys
import urllib2
import yaml
import json
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

except IOError, (instance):
    raise CustomException("Could not find the required configuration file expected at /etc/memcacher/config.yaml")
    print_error("Configuration Error !!")


class ContentItem(object):
    def __init__(self, uri, content, size, contenttype):
        self.uri = uri
        self.content = content
        self.size = size
        self.contenttype = contenttype


def getcontent(baseurl, uri):
    """
    Retrieves a file from the given url, from the defined base url.
    :rtype : ContentItem(object)
    :param uri: the uri to be retrieved
    :return:
    """
    print_info("Retrieving url: " + baseurl + uri)
    try:
        resource = urllib2.urlopen(baseurl + uri, None, config["fetchtimeout"])
    except IOError:
        print_error( "--Timed out when retrieving item, consider lengthening timeout.--")
        return ContentItem(uri, None, 0, None)
    if resource.getcode() not in [404, 500]:
        meta = resource.info()
        try:
            print_ok( "Retrieved " + str((int(meta.getheaders("Content-Length")[0]) / 1000)) + "kB")
            size = int(meta.getheaders("Content-Length")[0])
            contenttype = meta.getheaders("Content-Type")[0]
            content = resource.read()
            return ContentItem(uri, content, size, contenttype)
        except :
            print_warn("--Could not parse the received object, length or contenttype was bad...--")
            return ContentItem(uri, None, 0, None)
    else:
        print_warn("----Can not retrieve resource----")
    return ContentItem(uri, None, 0, None)


def putitemincache(baseurl, uri, expires, prefix):
    """
    Puts a single content item, specified by a uri, into the designated

    :rtype : str
    :param baseurl: The base of the query
    :param uri: the uri of the resource to retrieve and store
    :param expires: object expiration time, in seconds
    :param prefix: the prefix to append to the uri to create the key in memcached, this is the key that needs to be appended in NGINX
    :return: Returns the content of the item retrieved, to enable integration to LB.
    """
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
        # Then go get the content item
    contentitem = getcontent(baseurl, uri)
    if contentitem.size > 0:
        for key, value in mcservers.iteritems():
            print "Processing Server: " + key + " port " + str(value)
            try:
                mc = Client((key, value))
            except IOError:
                raise
            try:
                print_ok( "Setting " + prefix + contentitem.uri)
                mc.set(prefix + contentitem.uri, contentitem.content, expires)
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
