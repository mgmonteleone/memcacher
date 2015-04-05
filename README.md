

# memcacher
## A python utility for putting static web files into memcached
### Primarily for use with NGINX memcache module

This script was created to solve a basic issue with hosting a variety of web applications behing a NGINX loadbalancer/accellerator.

* Issue: Not all applications handle their static files optimally, especially when using node.js backends, which kinda suck when serving static files.

NGINX goes a great job of serving directly out of memcached, but if you are in DevOps, and the developers are to busy, overworked or lazy to build mechanisms to load assets, what do you do?

Hack it, of course, elegantly (i hope).

#Features
* Simple configuration of sites and uris through yaml
* Configurable timeouts
* Support for multiple servers
* [Datadog](https://www.datadoghq.com/) instrumentation support
* Logging to syslog support


# Configuration
The script uses a config.yaml file in the root folder. In this file ,multiple sites can be defined as well defining the array of memcache servers you want to write to.

```
---
http://www.aut-aut.hr:
    prefix: aa
    uris:
        / : 60000
        /style.min.css: 90000
        /index.min.js: 90000
        /content.details.js : 90000
        /res/jquery.mobile-1.1.0.min.js : 90000
        /jquery.magnific-popup.min.js : 90000
        /index.html : 7000
mcservers:
    memcache1 : 11211
    memcache2 : 11211
fetchtimeout : 5
datadogenabled : True
# Either "syslog" or a file path with filename to log, or "None" for no logging
logto : logging.log


```
* The base url of the site starts the config
* a prefix is designated for the site, which will be appended to the uri, to ensure they are unique
* a list of tuples for each resource to be memcached, specify the uri, with the memcache expiry time (in seconds) as the send parameter.
* The mcservers section allows you to list multiple memcache servers with their port. Assets will be written to all servers listed.
* fetchtimeout set the number of seconds to wait before giving up on retreiving a uri.
* datadogenabled : Set to true to send metrics to your datadog implementation. All metrics are tagged with the siteurl tag, to allow you to analyze by site.
    * memcacher.cached_page : Number of pages cached
    * memcacher.cached_bytes : number of bytes cached
    * memcacher.run_duration : time in seconds it takes to run memcacher
* logto, Either "syslog" or a file path with filename to log, or "None" for no logging.


# Usage
Called from the command line (should run on all platforms Python does), only one paramter is needed --siteurl. This needs to match the baseurl specified in the config.yaml.

```
python memcacher.py --siteurl http://www.aut-aut.hr
```
