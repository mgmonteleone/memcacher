#!/usr/bin/python
from libs import lib
from libs.lib import print_error, print_ok, print_warn
import getopt, sys
import logging
import logging.handlers
syslogger = logging.getLogger('syslogger')
syslogger.setLevel(logging.DEBUG)
#handler = logging.handlers.SysLogHandler(address = '/dev/log')
handler = logging.handlers.WatchedFileHandler("log.log")
syslogger.addHandler(handler)


def putincacheforsite(siteurl):
    """
    Gets resources listed in config file for the passed siteurl and puts them into memcached, with the correct prefix.

    :param siteurl: The full site url (with http:// or https://)
    :raise KeyError: If
    """
    syslogger.debug("....Starting Memcached Fetch....")
    print siteurl
    try:
        uris = lib.config[siteurl]["uris"]
        prefix = lib.config[siteurl]["prefix"]
        if uris is None:
            raise KeyError
    except KeyError:
        print_error( "The site " + siteurl + " was not found in config, or no URIs are defined")

    for key, value in uris.iteritems():
        syslogger.debug("Fetching and setting "+ siteurl+key)
        lib.putitemincache(siteurl, key, value, prefix)
    syslogger.debug("....Comleted Memcache Fetch....")
def main(argv):
    siteurl = ''
    try:
      opts, args = getopt.getopt(argv,"h",["siteurl="])
    except getopt.GetoptError:
      print_error('memcacher.py --siteurl <siteurl>')
      sys.exit(2)
    for opt, arg in opts:
      if opt == '-h':
          print_warn('memcacher.py --siteurl <siteurl>')
          sys.exit()
      elif opt in ("--siteurl"):
         siteurl = arg
    putincacheforsite(siteurl)

if __name__ == "__main__":
   main(sys.argv[1:])
