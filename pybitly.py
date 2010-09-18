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
Module to interact with the bit.ly API.
All the functions provided by the API are implemented (except 0Auth functions).
"""

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


class ArgTypeError(Exception):
    """
    An argument does not have the expected type.
    """
    def __init__(self, arg, given, expected):
        self.value = "Argument '%s' has type '%s', expected '%s'." % (arg, given, expected)

    def __str__(self):
        return repr(self.value)


class Api(object):
    """
    Interact with the bit.ly API.

    constructor:
        @param login (str): API login
        @param key (str): API key
    """
    baseURL = "http://api.bit.ly/v3"

    def __init__(self, login, key):
        self.login = login
        self.key = key
        self.opener = build_opener()

    def _checkResp(self, data):
        """
        Check query status and raise an ApiError if not OK.
        @param data (dict): query response
        """
        if data['status_code'] != 200:
            message = "Error %d: %s." % (data['status_code'], data['status_txt'])
            raise ApiError(message)

    def _multiArgs(self, argname, args):
        """
        Format URL arguments for queries allowing multiple ones.
        @param argname (str): argument name
        @param args (list): arguments to format
        @return str: formatted arguments
        """
        if len(args) == 0:
            return ''
        arglist = []
        for arg in args:
            arglist.append('%s=%s' % (argname, arg))
        arglist = '&'+'&'.join(arglist)
        return arglist

    def shorten(self, url, domain="bit.ly"):
        """
        Shorten a given URL.
        @param url (str): url to shorten
        @param domain (str): domain to use for the short URL ('bit.ly' or 'j.mp')
        @return dict: informations about shortened URL
        """
        if (domain not in ("bit.ly", "j.mp")) and (not self.bitly_pro_domain(domain)):
            raise ApiError("Unknown domain: %s (allowed: 'bit.ly', 'j.mp' and bitly Pro domains)" % domain)
        url = "%s/shorten?login=%s&apiKey=%s&longUrl=%s&domain=%s" % (self.baseURL, self.login, self.key, url, domain)
        resp = json.load(self.opener.open(url))
        self._checkResp(resp)
        return resp['data']

    def expand(self, shortUrl=None, urlHash=None):
        """
        Expand short URLs/hashs.
        @param shortUrl (list): zero or more short URLs to expand
        @param urlHash (list): zero or more URL hashs to expand
        @return dict: informations about expanded URLs
        """
        if (shortUrl is None) and (urlHash is None):
            return {}
        if shortUrl is None:
            urlarg = ''
        else:
            if type(shortUrl) is not list:
                raise ArgTypeError('shortUrl', str(type(shortUrl)).split("'")[1], 'list')
            urlarg = self._multiArgs('shortUrl', shortUrl)
        if urlHash is None:
            hasharg = ''
        else:
            if type(urlHash) is not list:
                raise ArgTypeError('urlHash', str(type(urlHash)).split("'")[1], 'list')
            hasharg = self._multiArgs('hash', urlHash)
        url = "%s/expand?login=%s&apiKey=%s%s%s" % (self.baseURL, self.login, self.key, urlarg, hasharg)
        resp = json.load(self.opener.open(url))
        self._checkResp(resp)
        return resp['data']['expand']

    def validate(self, login, key):
        """
        Validate a bit.ly API account.
        @param login (str): login for the account to check
        @param key (str): key for the account to check
        @return bool: True if the account is valid
        """
        url = "%s/validate?login=%s&apiKey=%s&x_login=%s&x_apiKey=%s" % (self.baseURL, self.login, self.key, login, key)
        resp = json.load(self.opener.open(url))
        self._checkResp(resp)
        return True if (resp['data']['valid'] == 1) else False

    def clicks(self, shortUrl=None, urlHash=None):
        """
        Get statistics about short URLs/hashs.
        @param shortUrl (list): zero or more short URLs to expand
        @param urlHash (list): zero or more URL hashs to expand
        @return dict: statistics about short URLs
        """
        if (shortUrl is None) and (urlHash is None):
            return {}
        if shortUrl is None:
            urlarg = ''
        else:
            urlarg = self._multiArgs('shortUrl', shortUrl)
        if urlHash is None:
            hasharg = ''
        else:
            if type(urlHash) is not list:
                raise ArgTypeError('urlHash', str(type(urlHash)).split("'")[1], 'list')
            hasharg = self._multiArgs('hash', urlHash)
        url = '%s/clicks?login=%s&apiKey=%s%s%s' % (self.baseURL, self.login, self.key, urlarg, hasharg)
        resp = json.load(self.opener.open(url))
        self._checkResp(resp)
        return resp['data']['clicks']

    def referrers(self, shortUrl=None, urlHash=None):
        """
        Get referring sites and number of clicks per referrer for a given short URL or hash.
        @param shortUrl (str or None): URL to get referrers for
        @param urlHash (str): URL hash to get referrers for
        @return dict: referrers and clicks for the URL
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
        @param shortUrl (str or None): URL to get countries for
        @param urlHash (str or None): URL hash to get countries for
        @return dict: countries informations for the URL or hash
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

    def clicks_by_minute(self, shortUrl=None, urlHash=None):
        """
        Get time series clicks per minute for the last hour (most recent to least recent) about short URLs/hashs.
        @param shortUrl (list): zero or more URLs to get clicks statistics for
        @param urlHash (list): zero or more URL hashs to get clicks statistics for
        @return dict: clicks statistics about short URLs
        """
        if (shortUrl is None) and (urlHash is None):
            return {}
        if shortUrl is None:
            urlarg = ''
        else:
            if type(shortUrl) is not list:
                raise ArgTypeError('shortUrl', str(type(shortUrl)).split("'")[1], 'list')
            urlarg = self._multiArgs('shortUrl', shortUrl)
        if urlHash is None:
            hasharg = ''
        else:
            if type(urlHash) is not list:
                raise ArgTypeError('urlHash', str(type(urlHash)).split("'")[1], 'list')
            hasharg = self._multiArgs('hash', urlHash)
        url = "%s/clicks_by_minute?login=%s&apiKey=%s%s%s" % (self.baseURL, self.login, self.key, urlarg, hasharg)
        resp = json.load(self.opener.open(url))
        self._checkResp(resp)
        return resp['data']['clicks_by_minute']

    def bitly_pro_domain(self, domain):
        """
        Check whether a given short domain is assigned for bitly Pro.
        @param domain (str): domain to check
        @return bool: True if the domain is assigned for bitly Pro
        """
        url = "%s/bitly_pro_domain?login=%s&apiKey=%s&domain=%s" % (self.baseURL, self.login, self.key, domain)
        resp = json.load(self.opener.open(url))
        self._checkResp(resp)
        return True if (resp['data']['bitly_pro_domain'] == 1) else False

    def lookup(self, longUrl=None):
        """
        Find short URLs corresponding to given long URLs.
        @param longUrl (list): zero or more long URLs to find
        @return dict: informations about found short URLs
        """
        if longUrl is None:
            return {}
        if type(longUrl) is not list:
            raise ArgTypeError('longUrl', str(type(longUrl)).split("'")[1], 'list')
        urlarg = self._multiArgs('url', longUrl)
        url = "%s/lookup?login=%s&apiKey=%s%s" % (self.baseURL, self.login, self.key, urlarg)
        resp = json.load(self.opener.open(url))
        self._checkResp(resp)
        return resp['data']['lookup']

    def authenticate(self, login, password):
        """
        Lookup a bit.ly API key given an account username and password.
        Access to this function is restricted and must be requested
        by email at api@bit.ly.
        @param login (str): account username
        @param password (str): account password
        @return dict: informations about requested account
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

    def info(self, shortUrl=None, urlHash=None):
        """
        Get informations about short URLs/hashs (creator, page title, ...).
        @param shortUrl (list): zero or more short URLs to query
        @param urlHash (list): zero or more short URL hashs to query
        @return dict: informations about queried URLs/hashs
        """
        if (shortUrl is None) and (urlHash is None):
            return {}
        if shortUrl is None:
            urlarg = ''
        else:
            if type(shortUrl) is not list:
                raise ArgTypeError('shortUrl', str(type(shortUrl)).split("'")[1], 'list')
            urlarg = self._multiArgs('shortUrl', shortUrl)
        if urlHash is None:
            hasharg = ''
        else:
            if type(urlHash) is not list:
                raise ArgTypeError('urlHash', str(type(urlHash)).split("'")[1], 'list')
            hasharg = self._multiArgs('hash', urlHash)
        url = "%s/info?login=%s&apiKey=%s%s%s" % (self.baseURL, self.login, self.key, urlarg, hasharg)
        resp = json.load(self.opener.open(url))
        self._checkResp(resp)
        return resp['data']['info']
