SRCDIR=$1
PROJDIR=$2

mkdir -p ~/.android/
cp -v $SRCDIR/debug.keystore ~/.android/

mkdir -p $PROJDIR
cp -v $SRCDIR/AndroidManifest.xml $PROJDIR

mkdir -p $PROJDIR/res
cp -rv $SRCDIR/res/drawable* $PROJDIR/res/

mkdir -p $PROJDIR/res/xml/
cp -v $SRCDIR/config.xml $PROJDIR/res/xml/

mkdir -p $PROJDIR/assets/www/
cp -v $SRCDIR/index.html $PROJDIR/assets/www/

DST=$PROJDIR/src/org/yerr/beeaware/beacon/
mkdir -p $DST
cp -v $SRCDIR/BeeawareBeacon.java $DST
cp -v $SRCDIR/GPSTracker.java $DST
cp -v $SRCDIR/LocationRecorder.java $DST
cp -v $SRCDIR/LocalStorage.java $DST
cp -v $SRCDIR/BackgroundService.java $DST
cp -v $SRCDIR/BackgroundServiceApi.aidl $DST
cp -v $SRCDIR/BootReceiver.java $DST
cp -v $SRCDIR/WebLog.java $DST
