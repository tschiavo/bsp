# Copyright 2013 The Moore Collective, LLC, All Rights Reserved

from datetime import datetime, timedelta
import sys

import psycopg2

import urls
import lib.html as html
import lib.db as db
import pages.common as comn
import pages.location_atom as loc_atom
import data.location_data as location_data

def render_get_location(isin, usr, usrid, view, time, length, display):
    if not isin:
        yield comn.sp('You are not logged in.', isin, usr)
    else:
        if display is not None:
            for seg in comn.yp(get_location_gen(
                usrid, view, time, length, display),
                isin, usr): 
                    yield (seg)
        else:
            for seg in get_location_gen(
                usrid, view, time, length, display):
                yield (seg)

def get_location_gen(usrid, view, time, length, display):
    displaydefined = display is not None
    accuracythresh = '500'
    epoch = datetime.utcfromtimestamp(0)
    now = datetime.utcnow()
    nowdelta = now - epoch
    onedayms = 1000*60*60*24
    deltanum = onedayms
    if length and length.isdigit(): deltanum = long(length)
    rangedelta = timedelta(milliseconds=deltanum)
    yesterdaydelta = nowdelta - rangedelta
    seconds = yesterdaydelta.seconds
    seconds += yesterdaydelta.days * 24 * 60 * 60
    millis = seconds * 1000
    time = str(millis) if time is None else time

    begtimestr = ''
    endtimestr = ''
    timephrase = ''
    timenum = 0 if time is None or time == 'all' else long(time)
    view = view if view else view

    if not time is None and time.isdigit():
        delta = timedelta(milliseconds=timenum)

        begtimestr = str(delta + epoch)
        endtimestr = str(delta + epoch + rangedelta)

        timephrase = \
            '''and (time > '%(b)s' and time < '%(e)s')''' % \
                { 'b':begtimestr, 'e':endtimestr }

    selectphrase = 'loc.sess_id, latitude, longitude, altitude, accuracy, time'
    orderphrase = 'order by time asc'

    query = \
        ''' select ''' + \
        selectphrase + \
        '''
        from location as loc
        join _user_session as us on us.sess_id = loc.sess_id
        join _user as u on u.u_id = us.u_id
        where u.u_id = %(usrid)s and accuracy < ''' + \
            accuracythresh + ' ' + \
            timephrase + ' ' + \
            orderphrase

    filterquery = \
    '''with filter as (''' + query + ''')
    select distinct on (latitude, longitude)
    latitude, longitude from filter'''

    cur = db.sendtodb(
        filterquery if view == 'latlon' else query, { 'usrid' : usrid })

    if displaydefined:

        yield \
            html.hyperlink(urls.PLACES__URL, 'My Places') + ' | ' + \
            html.br() + html.br()

        if time != None:
            lastframe = \
                html.urlencode(urls.LOCATION__URL,
                {
                    loc_atom.DISPLAY : '',
                    loc_atom.TIME : str(timenum - deltanum),
                    loc_atom.LEN : length,
                    loc_atom.EXPORT : view 
                })

            nextframe = \
                html.urlencode(urls.LOCATION__URL,
                {
                    loc_atom.DISPLAY : '',
                    loc_atom.TIME : str(timenum + deltanum),
                    loc_atom.LEN : length,
                    loc_atom.EXPORT : view 
                })

            yield \
                '[' + html.hyperlink(lastframe, '<<<') +  '] ' + \
                begtimestr + ' - ' + endtimestr + \
                ' [' + html.hyperlink(nextframe , '>>>') + ']' + html.br()

        viewframe = \
            html.urlencode(urls.LOCATION__URL, 
            {
                loc_atom.TIME : time,
                loc_atom.LEN : length,
                loc_atom.DISPLAY : ''
            })

        viewcsvframe = \
            html.urlencode(urls.LOCATION__URL, 
            {
                loc_atom.EXPORT : 'csv',
                loc_atom.TIME : time,
                loc_atom.LEN : length,
                loc_atom.DISPLAY : ''
            })

        viewlatlonframe = \
            html.urlencode(urls.LOCATION__URL, 
            {
                loc_atom.EXPORT : 'latlon',
                loc_atom.TIME : time,
                loc_atom.LEN : length,
                loc_atom.DISPLAY : ''
            })

        downloadcsvframe = \
            html.urlencode(urls.LOCATION__URL, 
            {
                loc_atom.EXPORT : 'csv',
                loc_atom.TIME : time,
                loc_atom.LEN : length,
            })

        downloadlatlonframe = \
            html.urlencode(urls.LOCATION__URL, 
            {
                loc_atom.EXPORT : 'latlon',
                loc_atom.TIME : time,
                loc_atom.LEN : length,
            })

        downloadcsvall = \
            html.urlencode(urls.LOCATION__URL, 
            {
                loc_atom.EXPORT : 'csv',
                loc_atom.TIME : 'all'
            })

        links = [
            html.hyperlink(viewframe, 'view frame'),
            html.hyperlink(viewlatlonframe, 'view frame latlon'),
            html.hyperlink(viewcsvframe, 'view frame csv'),
            html.hyperlink(downloadcsvframe, 'download frame csv'),
            html.hyperlink(downloadlatlonframe, 'download frame latlon'),
            html.hyperlink(downloadcsvall, 'download all csv')
        ]

        yield " | ".join(links) + html.br() + html.br()

        if view == 'csv' or view == 'latlon':
            timepair = \
                { loc_atom.TIME : str(timenum) } if timenum else {}
            lenpair = \
                { loc_atom.LEN : deltanum } if length else {}

            exporturl = html.urlencode(urls.LOCATION__URL, 
                dict(
                    timepair.items() + 
                    lenpair.items() + 
                    { loc_atom.EXPORT : view }.items()
                )
            )

            if displaydefined:
                yield '<pre>'

    if view == 'csv':
        yield 'sess,time,lat,lon,alt,acc\n'

    for row in cur:
        if view == 'csv':
            time = str(row['time'])
            sess = str(row['sess_id'])
            lat = str(row['latitude'])
            lon = str(row['longitude'])
            alt = str(row['altitude'])
            acc = str(row['accuracy'])
            yield sess + ',' + time + ',' + lat + ',' + lon + ',' + alt + \
                ',' + acc + '\n'
        elif view == 'latlon':
            lat = str(row['latitude'])
            lon = str(row['longitude'])
            yield lat + ',' + lon + '\n'
        else:
            time = str(row['time'])
            sess = str(row['sess_id'])
            lat = str(row['latitude'])
            lon = str(row['longitude'])
            alt = str(row['altitude'])
            acc = str(row['accuracy'])

            maplink = html.hyperlink(
                html.urlencode('http://maps.google.com/maps', { 
                    'q' : lat + ',' + lon
            }), 'map')

            revlookuplink = html.hyperlink(html.urlencode(
                'http://nominatim.openstreetmap.org/reverse', {
                'format' : 'json', 
                'lat' : lat, 
                'lon' : lon, 
                'zoom' : '18', 
                'addressdetails' : '1'
            }), 'lookup')

            markurl = html.urlencode(urls.PLACES__URL, {
                loc_atom.ORIGIN : urls.LOCATION__URL,
                loc_atom.LATITUDE : lat,
                loc_atom.LONGITUDE : lon
            })

            markform = \
                html.markup('form', {
                    'action' : markurl,
                    'method' : 'post',
                    'style' : 'display:inline'},
                    comn.submitbutton('Mark'))

            yield \
                time + ': ' + \
                lat + ', ' + lon + \
                ' [' + maplink + '] | ' + \
                '[' + revlookuplink + '] ' + \
                html.br()

    if displaydefined and (view == 'csv' or view == 'latlon'):
        yield '</pre>'

def render_post_location_from_json(isin, usr, u_id, json, sendersess):
    if not isin:
        return comn.sp('You are not logged in.', isin, usr)
    else:
        #print json
        for j in json["locations"]:
            curr = render_post_location(
                isin, 
                usr,
                u_id,
                j["time"],
                j["lat"],
                j["lon"],
                j["alt"],
                j["acc"],
                sendersess)
            #print str(j)
            if curr != "ok":
                return "error"
        return "ok"

def render_post_location(isin, usr, u_id, time, lat, lon, alt, acc, sess_id):
    if not isin:
        print 'location:render_post_location:you are not logged in, user: ' + \
            str(usr)
    else:
        #print "trace:location:render_post_location", str(usr), str(sess_id)
        try:
            location_data.do_add_location(
                time, lat, lon, alt, acc, sess_id, u_id, usr)
            #print "ok"
            return "ok"
        except:
            #print "error"
            print "Unexpected error:", sys.exc_info()[0]
            return "error"
