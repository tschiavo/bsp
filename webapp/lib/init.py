# Copyright 2013 The Moore Collective, LLC, All Rights Reserved
import optparse

import lib.db
import lib.auth
import lib.ip

def init():
    parser = optparse.OptionParser()
    parser.add_option(
        '-l', '--listen', 
        help='listen on ip address',
        dest='ipaddr',
        default='0.0.0.0')
    parser.add_option(
        '-p', '--port', 
        help='listen on port',
        dest='port',
        default='9999')
    parser.add_option(
        '-c', '--connstr', 
        help='connection string',
        dest='connstr')
    parser.add_option(
        '-s', '--onesession', 
        help='allow only one session',
        dest='onesession', 
        action='store_true',
        default=False)
    parser.add_option(
        '-r', '--require-invite', 
        help='require invite token to create account',
        dest='require_invite', 
        action='store_true',
        default=False)
    parser.add_option(
        '-e', '--external-location',
        help='external location to refer users to inside notification emails',
        dest='external_location',
        default='')
    parser.add_option(
        '-t', 
        '--sessiontimeout', 
        help='session timeout time (min)', 
        dest='sessiontimeout',
        default='1000000')

    (opts, args) = parser.parse_args()

    if opts.connstr is None:
        parser.print_help()
        exit(-1)

    lib.auth.set_timeout( int(opts.sessiontimeout) )

    lib.auth.onesession = False if opts.onesession is None else True

    lib.auth.require_invite = opts.require_invite

    lib.db.setconnstr(opts.connstr)

    lib.ip.address = opts.ipaddr
    lib.ip.port = opts.port
    lib.ip.external_location = opts.external_location

    return opts
