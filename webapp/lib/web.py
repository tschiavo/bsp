import datetime
import pytz
import time
import copy

import html
import json

import data.system_data as sys_data

def get_map_info(lat, lon):

    revlookupurl = html.urlencode(
        'http://nominatim.openstreetmap.org/reverse', {
            'format' : 'json',
                'lat' : lat, 'lon' : lon,
                    'zoom' : '18', 'addressdetails' : '1'}
    )

    revlookupstr = html.geturl(revlookupurl)

    resp = json.loads(revlookupstr)

    placeinfo = {}
    if resp is not None:
        resp = resp['address']
        #print str(resp)
        bestaddress = 'address is unknown'
        if 'road' in resp: 
            bestaddress = resp['road']

        if 'city' in resp: 
            bestaddress += ', ' + resp['city']
        elif 'county' in resp:
            bestaddress += ', ' + resp['county']

        if 'state' in resp: 
            bestaddress += ', ' + resp['state']
        elif 'county' in resp: 
            bestaddress += ', ' + resp['county']
        elif 'country' in resp: 
            bestaddress += ', ' + resp['country']
    
    return bestaddress


def get_map_link(lat, lon, descr):
    mapurl = html.urlencode('http://maps.google.com/maps',
        {'q':str(lat) + ',' + str(lon)})
    maplink = html.hyperlink(mapurl, descr)
    return maplink


def get_weather_info(loc):

    lat=loc['latitude']
    lon=loc['longitude']
    utctime=loc['utctime']
    loctime=loc['loctime']

    last_call = None
    last_call = sys_data.do_get_latest_service_call('wunderground')

    last_time = None
    if last_call is not None: last_time = last_call['call_timestamp']

    #print 'last time', str(last_time)

    #put a throttle on the calls to avoid getting blacklisted
    elapsed_time = None
    if last_time is not None: 
        elapsed_time = datetime.datetime.utcnow() - last_time

    #print 'elapsed time', str(elapsed_time)

    if  last_time is None or elapsed_time > datetime.timedelta(seconds=6):    

        #print 'calling wunderground'
        print 'using timestamp', str(loctime)

        yyyymmdd = datetime.datetime.strftime(loctime, '%Y%m%d')
            
        key = 'caa2beefd7998a94'
        url = \
            'http://api.wunderground.com/api/' + \
                key + '/history_' + yyyymmdd + \
                    '/q/' + str(lat) + ',' + str(lon) + '.json'

        #print url

        histjson = html.geturl(url)

        #must do this to prevent getting blacklisted by wunderground
        sys_data.do_log_service_call('wunderground')

        #print 'weather string', str(histjson)

        if histjson is not None:

            histdict = json.loads(histjson)

            if 'history' in histdict:
                hist = histdict['history']

                if 'observations' in hist:
                    obslist = hist['observations']

                    def flattime(obs):
                        return \
                            obs['year'] + obs['mon'] + obs['mday'] + \
                                obs['hour'] + obs['min']

                    fmt = '%Y%m%d%H%M'
                    def parsedate(obs):
                        return datetime.datetime.strptime(flattime(obs), fmt)

                    #find the nearest observation, stop when obs >= loctime
                    nearest_time = None
                    nearest_obs = None
                    for obs in obslist:
                        #print 'observation', str(obs)
                        obs_utctime = parsedate(obs['utcdate'])
                        obs_utctime = pytz.timezone('UTC').localize(obs_utctime)
                        #print 'obs_utctime', str(obs_utctime)
                        nearest_obs = copy.deepcopy(obs)

                        if obs_utctime > utctime:
                            break

                    if nearest_obs is None:
                        print 'wunderground history issue; no history'
                        print 'url', url
                        #print histjson
                        return None

                    return nearest_obs['tempi'] + ' F and ' + \
                            nearest_obs['conds']

    else:
        print 'it is too soon to call wunderground again:', str(elapsed_time)

    return None

if __name__ == '__main__':
    #curtime = datetime.datetime.utcnow()
    curtime = datetime.datetime.strptime('201404041329', '%Y%m%d%H%M')
    print str(get_weather_info(40.7409345957, -73.9909135938, curtime))
    print str(get_map_info(40.7409345957, -73.9909135938))
