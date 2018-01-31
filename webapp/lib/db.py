# Copyright 2013 The Moore Collective, LLC, All Rights Reserved
import psycopg2
import psycopg2.extras
import psycopg2.pool
import threading

_LOCK = threading.Lock()

_CONN_STR = ''
_POOL = None

def setconnstr(connstr):
    global _CONN_STR
    global _POOL
    _CONN_STR = connstr
    _POOL = psycopg2.pool.ThreadedConnectionPool(5, 10, _CONN_STR)

def conntodb():
    global _CONN_NUM
    global _POOL
    curconn = _POOL.getconn()
    return curconn

def sendtodbraw(statement, params = None, cursor_name = None):
    global _POOL
    ret = None
    #print "sendtodbraw: start"
    conn = conntodb()
    if not conn.closed:
        try:
            cur = None
            if cursor_name is not None:
                cur = conn.cursor(cursor_name, 
                    cursor_factory=psycopg2.extras.DictCursor)
            else:
                cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
            cur.execute(statement, params)
            if cursor_name == None: conn.commit()
            #print "sendtodbraw: end w/success"
            ret = cur
        except Exception, exc:
            print exc
            conn.close()

    #print "sendtodbraw: end w/none"
    _POOL.putconn(conn)
    return ret 

def sendtodb(statement, params = None):
    return sendtodbraw(statement, params)

def sendtodbssc(cursor_name, statement, params = None):
    return sendtodbraw(statement, params, cursor_name)
