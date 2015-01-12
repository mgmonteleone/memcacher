#!/usr/bin/python
from libs import lib


def putincacheforsite(siteurl):
    """
    Gets resources listed in config file for the passed siteurl and puts them into memcached, with the correct prefix.

    :param siteurl: The full site url (with http:// or https://)
    :raise KeyError: If
    """
    print siteurl
    try:
        uris = lib.config[siteurl]["uris"]
        prefix = lib.config[siteurl]["prefix"]
        if uris is None:
            raise KeyError
    except KeyError:
        print "The site " + siteurl + " was not found in config, or no URIs are defined"

    for key, value in uris.iteritems():
        lib.putitemincache(siteurl, key, value, prefix)


putincacheforsite("http://www.aut-aut.hr")
