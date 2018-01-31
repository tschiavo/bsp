cookiesfile=thecookies
url=http://beeaware.yerr.org:8202/send
#buddy
#userguid=52e9d0f0-049b-47c1-8151-13025ea78e9d
#tony
userguid=e004f289-15fa-4342-849b-9367bf9515b7
contextnum=$(shuf -i 0-3 -n 1)
polaritynum=$(shuf -i 0-1 -n 1)
energynum=$(shuf -i 0-18 -n 1)
poststr=sender\=me\&receiver\=${userguid}\&context\=${contextnum}\&polarity\=${polaritynum}\&energy\=${energynum}\&note\=hello
curl -b ${cookiesfile} -c ${cookiesfile} -d "${poststr}" ${url}
