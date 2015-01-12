#!/usr/bin/python
from libs import lib
import getopt, sys

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


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

def main(argv):
    siteurl = ''
    try:
      opts, args = getopt.getopt(argv,"hs:",["siteurl="])
    except getopt.GetoptError:
      print bcolors.WARNING +'memcacher.py -s <siteurl>' + bcolors.ENDC
      sys.exit(2)
    for opt, arg in opts:
      if opt == '-h':
         print bcolors.WARNING +'memcacher.py -s <siteurl>' + bcolors.ENDC
         sys.exit()
      elif opt in ("-s", "--siteurl"):
         siteurl = arg
    putincacheforsite(siteurl)

if __name__ == "__main__":
   main(sys.argv[1:])
