# -*- coding: utf-8 -*-
"""
Module to interact with the bit.ly API functions.
All the functions provided by the API are implemented except 0Auth functions.
"""
#TODO: in methods allowing shorturls or urlhashs: autodetect hashes and urls
#TODO: in methods allowing multiple args: limit to 15 args max (API restriction)
#TODO: implement OAuth methods

from urllib import urlencode
from urllib2 import build_opener

try:
    # Python >= 2.6
    from json import load as json_load
except ImportError:
    # Python < 2.6
    try:
        from simplejson import load as json_load
    except ImportError:
        print("""Could not import the simplejson module.
        You can download simplejson from PyPI or
        install it using your package manager.""")

from errors import ArgTypeError, ArgumentError

ALLOWED_API_DOMAINS = ['bit.ly', 'j.mp']


class RespStatus(object):
    """
    Contains an API response status.
    """
    def __init__(self, status_code, status_txt):
        self.code = status_code
        self.txt = status_txt

    def __str__(self):
        return "<RespStatus(status_code=%d, status_txt='%s')>" % (
            self.code, self.txt
        )

    def is_ok(self):
        return (self.code == 200) and (self.txt == 'OK')


class BitlyApi(object):
    """
    Interact with the bit.ly API functions.
    """
    base_url = "http://api.bit.ly/v3"

    def __init__(self, login, key):
        self.login = login
        self.key = key
        self.opener = build_opener()

    def __repr__(self):
        return "BitlyApi(login='%s', key='%s')" % (self.login, self.key)

    def __str__(self):
        return "<BitlyApi(login='%s', key='%s') at %s>" % (
            self.login, self.key, hex(id(self))
        )

    def _get_resp(self, url):
        """
        Send a query to bit.ly and return the received data.
        """
        resp = self.opener.open(url)
        json_data = json_load(resp)
        status = RespStatus(json_data['status_code'], json_data['status_txt'])
        data = json_data['data']
        return status, data

    def _multi_args(self, argname, args):
        """
        Format URL arguments for queries allowing multiple ones.
        """
        if not args:
            return ''
        arglist = []
        for arg in args:
            arglist.append('%s=%s' % (argname, arg))
        arglist = '&'+'&'.join(arglist)
        return arglist

    def shorten(self, longUrl, domain=None):
        """
        Shorten a given URL.
        """
        if domain is None:
            domain = 'bit.ly'
        if domain not in ALLOWED_API_DOMAINS:
            raise ArgumentError("Unknown domain '%s' "
                                "(allowed: 'bit.ly' and 'j.mp')" % domain)
        url = "%s/shorten?login=%s&apiKey=%s&longUrl=%s&domain=%s" % (
            self.base_url, self.login, self.key, longUrl, domain
        )
        resp = self._get_resp(url)
        return resp

    def expand(self, shortUrls=None, urlHashs=None):
        """
        Expand short URLs/hashs.
        """
        if (shortUrls is None) and (urlHashs is None):
            return {}
        if shortUrls is None:
            urlarg = ''
        else:
            if not isinstance(shortUrls, list):
                raise ArgTypeError('shortUrls', obj_type(shortUrls), 'list')
            urlarg = self._multi_args('shortUrl', shortUrls)
        if urlHashs is None:
            hasharg = ''
        else:
            if not isinstance(urlHashs, list):
                raise ArgTypeError('urlHashs', obj_type(urlHashs), 'list')
            hasharg = self._multi_args('hash', urlHashs)
        url = "%s/expand?login=%s&apiKey=%s%s%s" % (
            self.base_url, self.login, self.key, urlarg, hasharg
        )
        resp = self._get_resp(url)
        return resp

    def validate(self, login, key):
        """
        Validate a bit.ly API account.
        """
        url = "%s/validate?login=%s&apiKey=%s&x_login=%s&x_apiKey=%s" % (
            self.base_url, self.login, self.key, login, key
        )
        resp = self._get_resp(url)
        return resp

    def clicks(self, shortUrls=None, urlHashs=None):
        """
        Get statistics about short URLs/hashs.
        """
        if (shortUrls is None) and (urlHashs is None):
            return {}
        if shortUrls is None:
            urlarg = ''
        else:
            if not isinstance(shortUrls, list):
                raise ArgTypeError('shortUrls', obj_type(shortUrls), 'list')
            urlarg = self._multi_args('shortUrl', shortUrls)
        if urlHashs is None:
            hasharg = ''
        else:
            if not isinstance(urlHashs, list):
                raise ArgTypeError('urlHashs', obj_type(urlHashs), 'list')
            hasharg = self._multi_args('hash', urlHashs)
        url = '%s/clicks?login=%s&apiKey=%s%s%s' % (
            self.base_url, self.login, self.key, urlarg, hasharg
        )
        resp = self._get_resp(url)
        return resp

    def referrers(self, shortUrl=None, urlHash=None):
        """
        Get referring sites and number of clicks per referrer
        for a given short URL or hash.
        """
        if (shortUrl is None) and (urlHash is None):
            return {}
        if (shortUrl is not None) and (urlHash is not None):
            raise ArgumentError("You can submit only one URL or "
                                "hash, not both.")
        if shortUrl is not None:
            url = "%s/referrers?login=%s&apiKey=%s&shortUrl=%s" % (
                self.base_url, self.login, self.key, shortUrl
            )
        if urlHash is not None:
            url = "%s/referrers?login=%s&apiKey=%s&hash=%s" % (
                self.base_url, self.login, self.key, urlHash
            )
        resp = self._get_resp(url)
        return resp

    def countries(self, shortUrl=None, urlHash=None):
        """
        Get a list of countries from which clicks have originated for a given URL or hash.
        """
        if (shortUrl is None) and (urlHash is None):
            return {}
        if (shortUrl is not None) and (urlHash is not None):
            raise ArgumentError("You can submit only one URL or "
                                "hash, not both.")
        if shortUrl is not None:
            url = "%s/countries?login=%s&apiKey=%s&shortUrl=%s" % (
                self.base_url, self.login, self.key, shortUrl
            )
        if urlHash is not None:
            url = "%s/countries?login=%s&apiKey=%s&hash=%s" % (
                self.base_url, self.login, self.key, urlHash
            )
        resp = self._get_resp(url)
        return resp

    def clicks_by_minute(self, shortUrls=None, urlHashs=None):
        """
        Get time series clicks per minute for the last hour
        (most recent to least recent) about short URLs/hashs.
        """
        if (shortUrls is None) and (urlHashs is None):
            return {}
        if shortUrls is None:
            urlarg = ''
        else:
            if not isinstance(shortUrls, list):
                raise ArgTypeError('shortUrls', obj_type(shortUrls), 'list')
            urlarg = self._multi_args('shortUrl', shortUrls)
        if urlHashs is None:
            hasharg = ''
        else:
            if not isinstance(urlHashs, list):
                raise ArgTypeError('urlHashs', obj_type(urlHashs), 'list')
            hasharg = self._multi_args('hash', urlHashs)
        url = "%s/clicks_by_minute?login=%s&apiKey=%s%s%s" % (
            self.base_url, self.login, self.key, urlarg, hasharg
        )
        resp = self._get_resp(url)
        return resp


    def bitly_pro_domain(self, domain):
        """
        Check whether a given short domain is assigned for bitly Pro.
        """
        url = "%s/bitly_pro_domain?login=%s&apiKey=%s&domain=%s" % (
            self.base_url, self.login, self.key, domain
        )
        resp = self._get_resp(url)
        return resp

    def lookup(self, longUrls=None):
        """
        Find short URLs corresponding to given long URLs.
        """
        if longUrls is None:
            return {}
        if not isinstance(longUrls, list):
            raise ArgTypeError('longUrls', obj_type(longUrls), 'list')
        urlarg = self._multi_args('url', longUrls)
        url = "%s/lookup?login=%s&apiKey=%s%s" % (
            self.base_url, self.login, self.key, urlarg
        )
        resp = self._get_resp(url)
        return resp

    def authenticate(self, login, password):
        """
        Lookup a bit.ly API key given an account username and password.
        Access to this function is restricted and must be requested by
        email at api@bit.ly.
        """
        url = "%s/authenticate" % self.base_url
        data = urlencode({
            'login': self.login,
            'apiKey': self.key,
            'x_login': login,
            'x_password': password,
        })
        resp = self._get_resp(url)
        return resp

    def info(self, shortUrls=None, urlHashs=None):
        """
        Get informations about short URLs/hashs (creator, page title, ...).
        """
        if (shortUrls is None) and (urlHashs is None):
            return {}
        if shortUrls is None:
            urlarg = ''
        else:
            if not isinstance(shortUrls, list):
                raise ArgTypeError('shortUrls', obj_type(shortUrls), 'list')
            urlarg = self._multi_args('shortUrl', shortUrls)
        if urlHashs is None:
            hasharg = ''
        else:
            if not isinstance(urlHashs, list):
                raise ArgTypeError('urlHashs', obj_type(urlHashs), 'list')
            hasharg = self._multi_args('hash', urlHashs)
        url = "%s/info?login=%s&apiKey=%s%s%s" % (
            self.base_url, self.login, self.key, urlarg, hasharg
        )
        resp = self._get_resp(url)
        return resp


def obj_type(obj):
    """Return the string representation of a given object's type."""
    return obj.__class__.__name__
