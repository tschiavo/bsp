cookiesfile=thecookies
logouturl=http://beeaware.yerr.org:8202/logout
loginurl=http://beeaware.yerr.org:8202/login
cookiestr=username\=${1}\&pass\=${2}
curl -b ${cookiesfile} -c ${cookiesfile} -G ${logouturl}
curl -b ${cookiesfile} -c ${cookiesfile} -d "${cookiestr}" ${loginurl}
