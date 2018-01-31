newuser=$(cat /dev/urandom| tr -dc 'a-z'|head -c 8)
curl -d "username=${newuser}&pass=12345" http://beeaware.yerr.org:8202/create
