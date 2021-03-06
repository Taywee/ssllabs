#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright © 2016 Taylor C. Richberger <taywee@gmx.com>
# This code is released under the license described in the LICENSE file

from __future__ import division, absolute_import, print_function, unicode_literals

from six.moves.urllib.parse import urlsplit, urlunsplit, urlencode
import six

import requests

from ssllabs import errors
from ssllabs.host import Host
from ssllabs.info import Info
from ssllabs.statuscodes import StatusCodes

class Client(object):
    '''The main entry point of this module, used to run analysis and get data'''

    def __init__(self, entrypoint='https://api.ssllabs.com/api/v2'):
        '''initializes the client object.

        :param str entrypoint: The entrypoint URL for the API; usually shouldn't be changed
        '''
        self.entrypoint = entrypoint
        self.__host = None

    @property
    def entrypoint(self):
        '''Returns the entrypoint URL.

        Because the URL is disassembled on setting and reassembled on getting,
        the URL may not match the exact string as set, but will semantically
        match as the same URL (for instance, an empty query string and fragment
        are identical to absent ones).

        :returns: the entrypoint as set with the entrypoint property or __init__
        :rtype: str
        '''
        return urlunsplit((self.__scheme, self.__netloc, self.__path, '', ''))

    @entrypoint.setter
    def entrypoint(self, value):
        '''Sets the entrypoint URL.

        Because this calls urlsplit, an invalid URL will raise whatever
        exceptions it would when fed directly into urlsplit.

        :param str value: The URL to set
        '''
        parts = urlsplit(value)
        self.__scheme = parts.scheme
        self.__netloc = parts.netloc
        self.__path = parts.path.rstrip('/')

    def info(self):
        '''Calls the info API endpoint.
        
        :returns: the info data
        :rtype: ssllabs.info.Info
        '''
        path = '/'.join((self.__path, 'info'))
        url = urlunsplit((self.__scheme, self.__netloc, path, '', ''))
        request = requests.get(url)
        request.raise_for_status()
        return Info(request.json())

    def statusCodes(self):
        '''Calls the getStatusCodes API endpoint.
        
        :returns: the StatusCodes data
        :rtype: ssllabs.statuscodes.StatusCodes
        '''
        path = '/'.join((self.__path, 'getStatusCodes'))
        url = urlunsplit((self.__scheme, self.__netloc, path, '', ''))
        request = requests.get(url)
        request.raise_for_status()
        return StatusCodes(request.json())

    def analyze(self, host, publish=False, ignoreMismatch=False):
        '''A generator that iteratively calls analyze on a host until it is done or errored.
        
        Does not return the host structure, but sets it to the object for
        recalling with the :meth:`host` property.  When you run this, you must
        iterate it to completion before trying to access the host property.
        You can do this with a loop like::

            for data in client.analyze("https://example.com"):
                time.sleep(10)

        It is done this way to enable the user to construct their own
        asynchronous setups if they wish, without enforcing a specific
        framework or language version.  For instance, a proper async coroutine
        for python 3.5 could be constructed to do this something like this::
            
            from ssllabs.client import Client
            import asyncio

            async def analyze(hostname):
                client = Client()
                for data in client.analyze(hostname):
                    await asyncio.sleep(10)
                return client.host

        This will let you check multiple endpoints at once, or run the analysis
        while doing other work.

        The data yielded is the same form as the data put into the host
        property, but is expected to be incomplete; in particular, there will
        be no EndpointDetails.  You can use this data to possibly provide an
        ETA and progress bar, however.  It is quite fancy.

        :raises ssllabs.errors.ResponseError: subclass if an error was encountered with a known code
        :raises requests.HTTPError: if an error was encountered that isn't a known code, the raw error is returned
        :param str host: The host to test
        :param bool publish: Whether to publish the results on the Qualys SSL Labs site
        :param bool ignoreMismatch: Proceed with assessments even when the server certificate doesn't match the assessment hostname
        '''
        path = '/'.join((self.__path, 'analyze'))

        # Start the run
        query = {'host': host, 'all': 'done'}
        if publish:
            query['publish'] = 'on'

        if ignoreMismatch:
            query['ignoreMismatch'] = 'on'

        startnewquery = {'startNew': 'on'}
        startnewquery.update(query)

        try:
            url = urlunsplit((self.__scheme, self.__netloc, path, urlencode(startnewquery), ''))
            request = requests.get(url)
            request.raise_for_status()
            data = request.json()

            url = urlunsplit((self.__scheme, self.__netloc, path, urlencode(query), ''))
            while data['status'] in {'IN_PROGRESS', 'DNS'}:
                yield Host(data)
                request = requests.get(url)
                request.raise_for_status()
                data = request.json()
            self.__host = Host(data)
        except requests.HTTPError as e:
            if e.response.status_code in errors.codes:
                raise errors.codes[e.response.status_code](e.response.reason)
            else:
                raise e

    @property
    def host(self):
        '''Gets the host data.

        :raises ssllabs.errors.NoHostError: if a full call to analyze hasn't been completed
        :returns: The host object
        :rtype: ssllabs.host.Host
        '''

        if self.__host is None:
            raise errors.NoHostError('analyze must be run to completion before the host property may be accessed')
        return self.__host
