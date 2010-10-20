#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#    Copyright (c) 2010 MatToufoutu
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>
#
"""
Module to interact with the bit.ly API functions.
All the functions provided by the API are implemented except 0Auth functions.
"""

__all__ = ('Api', 'ApiError', 'ArgTypeError')

import json
from urllib import urlencode
from urllib2 import build_opener


class ApiError(Exception):
    """
    Generic exception for API errors.
    """
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)


class ArgTypeError(ApiError):
    """
    An argument does not have the expected type.
    """
    def __init__(self, arg, given, expected):
        self.value = "Argument '%s' has type '%s', expected '%s'." % (arg, given, expected)

    def __str__(self):
        return repr(self.value)


class Api(object):
    """
    Interact with the bit.ly API functions.
    """
    baseURL = "http://api.bit.ly/v3"

    def __init__(self, login, key):
        """
        @param login: API login
        @type login: str
        @param key: API key
        @type key:  str
        """
        self.login = login
        self.key = key
        self.opener = build_opener()

    def _checkResp(self, data):
        """
        Check query status and raise an ApiError if not OK.

        @param data: query response
        @type data: dict
        """
        if data['status_code'] != 200:
            message = "Error %d: %s." % (data['status_code'], data['status_txt'])
            raise ApiError(message)

    def _multiArgs(self, argname, args):
        """
        Format URL arguments for queries allowing multiple ones.

        @param argname: argument name
        @type argname: str
        @param args: arguments to format
        @type args: list

        @return: formatted arguments
        @rtype: str
        """
        if len(args) == 0:
            return ''
        arglist = []
        for arg in args:
            arglist.append('%s=%s' % (argname, arg))
        arglist = '&'+'&'.join(arglist)
        return arglist

    def _typeStr(self, obj):
        """
        Get the string representation of an object's type.

        @param obj: object to get type from
        @type obj: object

        @return: type string
        @rtype: str
        """
        return str(type(obj)).split("'")[1]

    def shorten(self, longUrl, domain="bit.ly"):
        """
        Shorten a given URL.

        @param longUrl: url to shorten
        @type longUrl: str
        @param domain: domain to use for the short URL ('bit.ly' or 'j.mp')
        @type domain: str

        @return: informations about shortened URL
        @rtype: dict
        """
        if domain not in ("bit.ly", "j.mp"):
            raise ApiError("Unknown domain: %s (allowed: 'bit.ly' and 'j.mp')" % domain)
        url = "%s/shorten?login=%s&apiKey=%s&longUrl=%s&domain=%s" % (self.baseURL, self.login, self.key, longUrl, domain)
        resp = json.load(self.opener.open(url))
        self._checkResp(resp)
        return resp['data']

    def expand(self, shortUrls=None, urlHashs=None):
        """
        Expand short URLs/hashs.

        @param shortUrls: zero or more short URLs to expand
        @type shortUrls: list
        @param urlHashs: zero or more URL hashs to expand
        @type urlHashs: list

        @return: informations about expanded URLs
        @rtype: dict
        """
        if (shortUrls is None) and (urlHashs is None):
            return {}
        if shortUrls is None:
            urlarg = ''
        else:
            if not isinstance(shortUrls, list):
                raise ArgTypeError('shortUrls', self._typeStr(shortUrls), 'list')
            urlarg = self._multiArgs('shortUrl', shortUrls)
        if urlHashs is None:
            hasharg = ''
        else:
            if not isinstance(urlHashs, list):
                raise ArgTypeError('urlHashs', self._typeStr(urlHashs), 'list')
            hasharg = self._multiArgs('hash', urlHashs)
        url = "%s/expand?login=%s&apiKey=%s%s%s" % (self.baseURL, self.login, self.key, urlarg, hasharg)
        resp = json.load(self.opener.open(url))
        self._checkResp(resp)
        data = resp['data']['expand']
        if len(data) == 1:
            data = data[0]
        return data

    def validate(self, login, key):
        """
        Validate a bit.ly API account.

        @param login: login for the account to check
        @type login: str
        @param key: key for the account to check
        @type key: str

        @return: True if the account is valid
        @rtype: bool
        """
        url = "%s/validate?login=%s&apiKey=%s&x_login=%s&x_apiKey=%s" % (self.baseURL, self.login, self.key, login, key)
        resp = json.load(self.opener.open(url))
        self._checkResp(resp)
        return True if (resp['data']['valid'] == 1) else False

    def clicks(self, shortUrls=None, urlHashs=None):
        """
        Get statistics about short URLs/hashs.

        @param shortUrls: zero or more short URLs to expand
        @type shortUrls: list
        @param urlHashs: zero or more URL hashs to expand
        @type urlHashs: list

        @return: statistics about short URLs
        @rtype: dict
        """
        if (shortUrls is None) and (urlHashs is None):
            return {}
        if shortUrls is None:
            urlarg = ''
        else:
            if not isinstance(shortUrls, list):
                raise ArgTypeError('shortUrls', self._typeStr(shortUrls), 'list')
            urlarg = self._multiArgs('shortUrl', shortUrls)
        if urlHashs is None:
            hasharg = ''
        else:
            if not isinstance(urlHashs, list):
                raise ArgTypeError('urlHashs', self._typeStr(urlHashs), 'list')
            hasharg = self._multiArgs('hash', urlHashs)
        url = '%s/clicks?login=%s&apiKey=%s%s%s' % (self.baseURL, self.login, self.key, urlarg, hasharg)
        resp = json.load(self.opener.open(url))
        self._checkResp(resp)
        data = resp['data']['clicks']
        if len(data) == 1:
            data = data[0]
        return data

    def referrers(self, shortUrl=None, urlHash=None):
        """
        Get referring sites and number of clicks per referrer for a given short URL or hash.

        @param shortUrl: URL to get referrers for
        @type shortUrl: str
        @param urlHash: URL hash to get referrers for
        @type urlHash: str

        @return: referrers and clicks for the URL
        @rtype: dict
        """
        if (shortUrl is None) and (urlHash is None):
            return {}
        if (shortUrl is not None) and (urlHash is not None):
            raise ApiError("You can submit only one URL or hash, not both.")
        if shortUrl is not None:
            url = "%s/referrers?login=%s&apiKey=%s&shortUrl=%s" % (self.baseURL, self.login, self.key, shortUrl)
        if urlHash is not None:
            url = "%s/referrers?login=%s&apiKey=%s&hash=%s" % (self.baseURL, self.login, self.key, urlHash)
        resp = json.load(self.opener.open(url))
        self._checkResp(resp)
        return resp['data']

    def countries(self, shortUrl=None, urlHash=None):
        """
        Get a list of countries from which clicks have originated for a given URL or hash.

        @param shortUrl: URL to get countries for
        @type shortUrl: str
        @param urlHash: URL hash to get countries for
        @type urlHash: str

        @return: countries informations for the URL or hash
        @rtype: dict
        """
        if (shortUrl is None) and (urlHash is None):
            return {}
        if (shortUrl is not None) and (urlHash is not None):
            raise ApiError("You can submit only one URL or hash, not both.")
        if shortUrl is not None:
            url = "%s/countries?login=%s&apiKey=%s&shortUrl=%s" % (self.baseURL, self.login, self.key, shortUrl)
        if urlHash is not None:
            url = "%s/countries?login=%s&apiKey=%s&hash=%s" % (self.baseURL, self.login, self.key, urlHash)
        resp = json.load(self.opener.open(url))
        self._checkResp(resp)
        return resp['data']

    def clicks_by_minute(self, shortUrls=None, urlHashs=None):
        """
        Get time series clicks per minute for the last hour (most recent to least recent) about short URLs/hashs.

        @param shortUrls: zero or more URLs to get clicks statistics for
        @type shortUrls: list
        @param urlHashs: zero or more URL hashs to get clicks statistics for
        @type urlHashs: list

        @return: clicks statistics about short URLs
        @rtype: dict
        """
        if (shortUrls is None) and (urlHashs is None):
            return {}
        if shortUrls is None:
            urlarg = ''
        else:
            if not isinstance(shortUrls, list):
                raise ArgTypeError('shortUrls', self._typeStr(shortUrls), 'list')
            urlarg = self._multiArgs('shortUrl', shortUrls)
        if urlHashs is None:
            hasharg = ''
        else:
            if not isinstance(urlHashs, list):
                raise ArgTypeError('urlHashs', self._typeStr(urlHashs), 'list')
            hasharg = self._multiArgs('hash', urlHashs)
        url = "%s/clicks_by_minute?login=%s&apiKey=%s%s%s" % (self.baseURL, self.login, self.key, urlarg, hasharg)
        resp = json.load(self.opener.open(url))
        self._checkResp(resp)
        data = resp['data']['clicks_by_minute']
        if len(data) == 1:
            data = data[0]
        return data

    def bitly_pro_domain(self, domain):
        """
        Check whether a given short domain is assigned for bitly Pro.

        @param domain: domain to check
        @type domain: str

        @return: True if the domain is assigned for bitly Pro
        @rtype: bool
        """
        url = "%s/bitly_pro_domain?login=%s&apiKey=%s&domain=%s" % (self.baseURL, self.login, self.key, domain)
        resp = json.load(self.opener.open(url))
        self._checkResp(resp)
        return True if (resp['data']['bitly_pro_domain'] == 1) else False

    def lookup(self, longUrls=None):
        """
        Find short URLs corresponding to given long URLs.

        @param longUrls: zero or more long URLs to find
        @type longUrls: list

        @return: informations about found short URLs
        @rtype: dict
        """
        if longUrls is None:
            return {}
        if not isinstance(longUrls, list):
            raise ArgTypeError('longUrls', self._typeStr(longUrls), 'list')
        urlarg = self._multiArgs('url', longUrls)
        url = "%s/lookup?login=%s&apiKey=%s%s" % (self.baseURL, self.login, self.key, urlarg)
        resp = json.load(self.opener.open(url))
        self._checkResp(resp)
        return resp['data']['lookup']

    def authenticate(self, login, password):
        """
        Lookup a bit.ly API key given an account username and password.
        Access to this function is restricted and must be requested by
        email at api@bit.ly.

        @param login: account username
        @type login: str
        @param password: account password
        @type password: str

        @return: informations about requested account
        @rtype: dict
        """
        url = "%s/authenticate" % self.baseURL
        data = urlencode({
            'login': self.login,
            'apiKey': self.key,
            'x_login': login,
            'x_password': password,
        })
        resp = json.load(self.opener.open(url, data))
        self._checkResp(resp)
        return resp['data']['authenticate']

    def info(self, shortUrls=None, urlHashs=None):
        """
        Get informations about short URLs/hashs (creator, page title, ...).

        @param shortUrls: zero or more short URLs to query
        @type shortUrls: list
        @param urlHashs: zero or more short URL hashs to query
        @type urlHashs: list

        @return: informations about queried URLs/hashs
        @rtype: dict
        """
        if (shortUrls is None) and (urlHashs is None):
            return {}
        if shortUrls is None:
            urlarg = ''
        else:
            if not isinstance(shortUrls, list):
                raise ArgTypeError('shortUrls', self._typeStr(shortUrls), 'list')
            urlarg = self._multiArgs('shortUrl', shortUrls)
        if urlHashs is None:
            hasharg = ''
        else:
            if not isinstance(urlHashs, list):
                raise ArgTypeError('urlHashs', self._typeStr(urlHashs), 'list')
            hasharg = self._multiArgs('hash', urlHashs)
        url = "%s/info?login=%s&apiKey=%s%s%s" % (self.baseURL, self.login, self.key, urlarg, hasharg)
        resp = json.load(self.opener.open(url))
        self._checkResp(resp)
        data = resp['data']['info']
        if len(data) == 1:
            data = data[0]
        return data
