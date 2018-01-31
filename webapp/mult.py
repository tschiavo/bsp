from multiprocessing import Process
from multiprocessing import Pool

from random import randint
import time
import os

import lib.init as init
import data.user_data as user_data

def log_result(result):
    print str(result)

def f(count, x):
    init.init()
    #s = randint(1, 5)
    #time.sleep(s)
    #return (__name__, os.getppid(), os.getpid(), "id: "+str(count), "sleep: "+str(s), x)
    try:
        return (count, user_data.do_get_u_id_from_sn("mary"))
    except e:
        print str(e)

if __name__ == '__main__':
    pool = Pool(processes = 50)              # start 4 worker processes
    count = 0
    for x in range(1,100):
        count = count + 1
        print str("count: "+str(count))
        result = pool.apply_async(f, (count, 10),  callback = log_result)
        #print str(result.get(timeout=20))
    pool.close()
    pool.join()

    init.init()
