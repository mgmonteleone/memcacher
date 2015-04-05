#!/usr/bin/python
from libs import lib
from libs.lib import print_error, print_ok, print_warn, datadogenabled,logto
import getopt, sys
import logging
import logging.handlers
from libs.tendo import singleton
import time
from libs import statsd
#Set up logging
syslogger = logging.getLogger('syslogger')
syslogger.setLevel(logging.DEBUG)
if logto == "syslog":
    handler = logging.handlers.SysLogHandler(address = '/dev/log')
    syslogger.addHandler(handler)
elif logto != "None":
    handler = logging.handlers.WatchedFileHandler("logto")
    syslogger.addHandler(handler)

me = singleton.SingleInstance()

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
          time.sleep(20)
          sys.exit()
      elif opt in ("--siteurl"):
        siteurl = arg
        start_time=time.time()
        putincacheforsite(siteurl)
        duration = time.time() - start_time
        tags = 'siteurl: '+ siteurl
        if datadogenabled == True:
            print "Informing DataDog"
	    try:
                statsd.statsd.connection(host="aa-gce-dkr-004")
                statsd.statsd.histogram('memcacher.run_duration',duration,tags=[tags])
                statsd.statsd.event("Memcacher Run","Memcacher Ran for "+siteurl,alert_type="info",priority="low")
            except Exception as e:
                print "Could not send stats: "+e.message 

if __name__ == "__main__":
   main(sys.argv[1:])
