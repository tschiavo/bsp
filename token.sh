function urlencode() {
    python -c "import sys, urllib as ul; print ul.quote_plus(sys.argv[1])" "$1"
}

FLICKRURL="https://www.flickr.com/services/oauth/request_token"
MYRANDOM=$RANDOM$RANDOM$RANDOM$RANDOM
NONCE=$(($MYRANDOM%100000000))
NONCE=$(echo $NONCE | sed -e 's/-//')
TIMESTAMP=$(date +%s)
CONSUMER_KEY="db220b2d7f59f951501aebead773c28c"
CONSUMER_SECRET="c0c5ca3412291a49"
SIGN_METH="HMAC-SHA1"
VER="1.0"
CALLBACK="http://beeaware.spriggle.net"
ENCODEDCALLBACK=$(urlencode $CALLBACK)

BASEURL=$FLICKRURL

PARAMSTR=$PARAMSTR"oauth_callback="$ENCODEDCALLBACK
PARAMSTR=$PARAMSTR"&oauth_consumer_key="$CONSUMER_KEY
PARAMSTR=$PARAMSTR"&oauth_nonce="$NONCE
PARAMSTR=$PARAMSTR"&oauth_signature_method="$SIGN_METH
PARAMSTR=$PARAMSTR"&oauth_timestamp="$TIMESTAMP
PARAMSTR=$PARAMSTR"&oauth_version="$VER

SIGNATUREBASESTR="GET&"$(urlencode $BASEURL)"&"$(urlencode $PARAMSTR)

echo ------SIGNATUREBASESTR------
echo $SIGNATUREBASESTR
echo ----------------------------

SIGNING_KEY=$CONSUMER_SECRET"&"
