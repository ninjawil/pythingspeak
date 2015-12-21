#------------------------------------------------------------------------------
#
# Interfaces to thingspeak
#
# The MIT License (MIT)
#
# Copyright (c) 2015 William De Freitas
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#
#-------------------------------------------------------------------------------

#!usr/bin/env python

#===============================================================================
# IMPORT MODULES
#===============================================================================
# Standard Library
import ast
import logging

# Third party modules
import requests
import requests.packages.urllib3

# Application modules


#!!! DISABLE WARNINGS ON PYTHON <2.7.9 !!!
requests.packages.urllib3.disable_warnings()


#===============================================================================
# CLASS DEFINITION AND FUNCTIONS
#===============================================================================
class TSAccount:

    '''Sets up a thingspeak account'''

    #---------------------------------------------------------------------------
    # PARENT CONSTRUCTOR
    #---------------------------------------------------------------------------
    def __init__(self, account_host_addr, account_api_key):

        self.host_addr = account_host_addr
        self.api_key = account_api_key
        self.logger = logging.getLogger('root')


    #---------------------------------------------------------------------------
    # GET REQUEST
    #---------------------------------------------------------------------------
    def http_request_get(self, query, parameters):

        if 'api_key' not in parameters:
            parameters['api_key'] = self.api_key
        
        self.logger.debug('HTTP request:')
        self.logger.debug('Query: {q}'.format(q= query))
        self.logger.debug('Parameters: {p}'.format(p= parameters))

        r = requests.get(query, parameters)

        r = r.text
        r = r.replace('null', '"NaN"')
        r = r.replace('true', 'True')
        r = r.replace('false', 'False')

        self.logger.debug(r)

        return ast.literal_eval(r)

    
    #---------------------------------------------------------------------------
    # LIST MY CHANNELS
    #---------------------------------------------------------------------------
    def list_my_channels(self):
        
        '''Valid parameters:
            api_key (string) - Your Account API Key (this is different from a
            Channel API Key, and can be found in your Account settings).
            (required)'''
  
        cmd = self.host_addr + 'channels.json'
            
        return self.http_request_get(cmd, {})
     

#===============================================================================
class TSChannel(TSAccount):
    
    '''Set up thingspeak channel:
        + Account host address (required)
        + api_key= Write api key
        + file= File to store api key default = thingspeak.txt
        + ch_id= Channel id

        Functions return a dictionary with responses.'''

    
    #---------------------------------------------------------------------------
    # CHILD CONSTRUCTOR
    #---------------------------------------------------------------------------    
    def __init__(self, acc_host_addr, **args):
        
        self.logger = logging.getLogger('root')

        if acc_host_addr[-1:] is not '/':
            acc_host_addr += '/'
            
        self.host_addr = acc_host_addr

        if 'api_key' in args:
            self.api_key = args['api_key']
            if 'file' in args:
                self.write_write_api_key_file(args['file'])
        elif 'file' in args:
            self.api_key = self.read_write_api_key(args['file'])        
        else:
            logger.error('ERROR: no api key or api file passed!')
        
        if 'ch_id' in args:
            self.channel_id = args['ch_id']


    #---------------------------------------------------------------------------
    # WRITE API KEY TO FILE
    #---------------------------------------------------------------------------
    def write_write_api_key_file(self, filename):
        with open(filename, 'w') as f:
                f.write(self.api_key)

    
    #---------------------------------------------------------------------------
    # LOAD THINGSPEAK API KEY
    #---------------------------------------------------------------------------
    def read_write_api_key(self, filename):
    
        error_to_catch = getattr(__builtins__,'FileNotFoundError', IOError)
        
        try:
            with open(filename, 'r') as f:
                key = f.read()
            return key
                
        except error_to_catch:
            logger.error('ERROR: No thingspeak write api key file found.')     


    #---------------------------------------------------------------------------
    # UPDATE THINGSPEAK CHANNEL
    #---------------------------------------------------------------------------
    def update_channel(self, parameters={}):
        
        '''Valid parameters:
            api_key (string) - Write API Key for this specific Channel
               (required). The Write API Key can optionally be sent via a
               THINGSPEAKAPIKEY HTTP header.
            field1 (string) - Field 1 data (optional)
            field2 (string) - Field 2 data (optional)
            field3 (string) - Field 3 data (optional)
            field4 (string) - Field 4 data (optional)
            field5 (string) - Field 5 data (optional)
            field6 (string) - Field 6 data (optional)
            field7 (string) - Field 7 data (optional)
            field8 (string) - Field 8 data (optional)
            lat (decimal) - Latitude in degrees (optional)
            long (decimal) - Longitude in degrees (optional)
            elevation (integer) - Elevation in meters (optional)
            status (string) - Status update message (optional)
            twitter (string) - Twitter username linked to ThingTweet (optional)
            tweet (string) - Twitter status update; see updating ThingTweet
                for more info (optional)
            created_at (datetime) - Date when this feed entry was created,
                in ISO 8601 format, for example: 2014-12-31 23:59:59 . Time
                zones can be specified via the timezone parameter (optional)'''

        cmd = '{host}update'.format(host= self.host_addr)
        
        if 'api_key' not in parameters:
            parameters['api_key'] = self.api_key
            
        return requests.post(cmd, parameters)


    #---------------------------------------------------------------------------
    # GET CHANNEL FEED
    #---------------------------------------------------------------------------
    def get_channel_feed(self, parameters={}):
        
        '''Valid parameters:
            api_key (string) Read API Key for this specific Channel 
               (optional--no key required for public channels)
            results (integer) Number of entries to retrieve, 8000 max,
                default of 100 (optional)
            days (integer) Number of 24-hour periods before now to
                include in feed (optional)
            start (datetime) Start date in format YYYY-MM-DD%20HH:NN:SS
                (optional)
            end (datetime) End date in format YYYY-MM-DD%20HH:NN:SS (optional)
            timezone (string) Timezone identifier for this request (optional)
            offset (integer) Timezone offset that results should be displayed
                in. Please use the timezone parameter for greater accuracy.
                (optional)
            status (true/false) Include status updates in feed by setting
                "status=true" (optional)
            metadata (true/false) Include Channel's metadata by setting
                "metadata=true" (optional)
            location (true/false) Include latitude, longitude, 
                and elevation in feed by setting "location=true" (optional)
            min (decimal) Minimum value to include in response (optional)
            max (decimal) Maximum value to include in response (optional)
            round (integer) Round to this many decimal places (optional)
            timescale (integer or string) Get first value in this many minutes, 
                valid values: 10, 15, 20, 30, 60, 240, 720, 1440, "daily"
                optional)
            sum (integer or string) Get sum of this many minutes, 
                valid values: 10, 15, 20, 30, 60, 240, 720, 1440, "daily"
                optional)
            average (integer or string) Get average of this many minutes, 
                valid values: 10, 15, 20, 30, 60, 240, 720, 1440, "daily"
                (optional)
            median (integer or string) Get median of this many minutes, 
                valid values: 10, 15, 20, 30, 60, 240, 720, 1440, "daily"
                optional)
            callback (string) Function name to be used for JSONP cross-domain
                requests (optional)'''
            
        cmd = '{host}channels/{ch_id}/feeds.json'.format(
                host= self.host_addr,
                ch_id= str(self.channel_id))
     
        return self.http_request_get(cmd, parameters)


    #---------------------------------------------------------------------------
    # GET A CHANNEL FIELD FEED
    #---------------------------------------------------------------------------
    def get_a_channel_field_feed(self, field_id= '', parameters={}):
        
        '''Valid parameters:
            api_key (string) Read API Key for this specific Channel 
               (optional--no key required for public channels)
            results (integer) Number of entries to retrieve, 8000 max,
                default of 100 (optional)
            days (integer) Number of 24-hour periods before now to
                include in feed (optional)
            start (datetime) Start date in format YYYY-MM-DD%20HH:NN:SS
                (optional)
            end (datetime) End date in format YYYY-MM-DD%20HH:NN:SS (optional)
            timezone (string) Timezone identifier for this request (optional)
            offset (integer) Timezone offset that results should be displayed
                in. Please use the timezone parameter for greater accuracy.
                (optional)
            status (true/false) Include status updates in feed by setting
                "status=true" (optional)
            metadata (true/false) Include Channel's metadata by setting
                "metadata=true" (optional)
            location (true/false) Include latitude, longitude, 
                and elevation in feed by setting "location=true" (optional)
            min (decimal) Minimum value to include in response (optional)
            max (decimal) Maximum value to include in response (optional)
            round (integer) Round to this many decimal places (optional)
            timescale (integer or string) Get first value in this many minutes, 
                valid values: 10, 15, 20, 30, 60, 240, 720, 1440, "daily"
                optional)
            sum (integer or string) Get sum of this many minutes, 
                valid values: 10, 15, 20, 30, 60, 240, 720, 1440, "daily"
                optional)
            average (integer or string) Get average of this many minutes, 
                valid values: 10, 15, 20, 30, 60, 240, 720, 1440, "daily"
                (optional)
            median (integer or string) Get median of this many minutes, 
                valid values: 10, 15, 20, 30, 60, 240, 720, 1440, "daily"
                optional)
            callback (string) Function name to be used for JSONP cross-domain
                requests (optional)'''
            
        if field_id:
            field_id = '/{f_id}'.format(f_id= field_id)

        cmd = '{host}channels/{ch_id}/fields{f_id}.json'.format(
                host= self.host_addr,
                ch_id= str(self.channel_id),
                f_id= field_id)
     
        return self.http_request_get(cmd, parameters)


    #---------------------------------------------------------------------------
    # GET LAST FEED
    #---------------------------------------------------------------------------
    def get_last_entry_in_channel_feed(self, field_id= '', parameters={}):
        
        '''Valid parameters:
            api_key (string) Read API Key for this specific Channel 
                (optional--no key required for public channels)
            timezone (string) Timezone identifier for this request (optional)
            offset (integer) Timezone offset that results should be displayed
                in. Please use the timezone parameter for greater accuracy.
                optional)
            status (true/false) Include status updates in feed by
                setting "status=true" (optional)
            location (true/false) Include latitude, longitude, 
                and elevation in feed by setting "location=true" (optional)
            callback (string) Function name to be used for JSONP cross-domain
                requests (optional)
            prepend (string) Text to add before the API response (optional)
            append (string) Text to add after the API response (optional)'''

        if field_id:
            field_id = '/{f_id}'.format(f_id= field_id)

        cmd = '{host}channels/{ch_id}/feeds{f_id}/last.json'.format(
                host= self.host_addr, 
                ch_id= str(self.channel_id),
                f_id= field_id)

        return self.http_request_get(cmd, parameters)


    #---------------------------------------------------------------------------
    # GET STATUS UPDATE
    #---------------------------------------------------------------------------
    def get_status_update(self, parameters={}):
        
        '''Valid parameters:
            api_key (string) Read API Key for this specific Channel (optional
                --no key required for public channels)
            timezone (string) Timezone identifier for this request (optional)
            offset (integer) Timezone offset that results should be displayed
                in. Please use the timezone parameter for greater accuracy.
                optional)
            callback (string) Function name to be used for JSONP cross-domain
                requests (optional)'''
  
        cmd = '{host}channels/{ch_id}/status.json'.format(
                host= self.host_addr,
                ch_id= str(self.channel_id))
            
        return self.http_request_get(cmd, parameters)


    #---------------------------------------------------------------------------
    # GET SPECIFIC ENTRY IN A CHANNEL
    #---------------------------------------------------------------------------
    def get_specific_entry(self, entry_id, parameters={}):
        
        '''entry_id to return
           Valid parameters:
            api_key (string) Read API Key for this specific Channel (optional
                --no key required for public channels)
            timezone (string) Timezone identifier for this request (optional)
            offset (integer) Timezone offset that results should be displayed
                in. Please use the timezone parameter for greater accuracy.
                (optional)
            status (true/false) Include status updates in feed by setting
                "status=true" (optional)
            location (true/false) Include latitude, longitude, and elevation
                in feed by setting "location=true" (optional)
            callback (string) Function name to be used for JSONP cross-domain
                requests (optional)'''
  
        cmd = '{host}channels/{ch_id}/feeds/{entry}.json'.format(
                host= self.host_addr,
                ch_id= str(self.channel_id),
                entry= str(entry_id))
            
        return self.http_request_get(cmd, parameters)
