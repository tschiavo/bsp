. locations.sh

PATH=$PATH:$JAVA_BIN:$ANDROID_TOOLS_BIN:$ANDROID_PLATFORM_TOOLS_BIN
JAVA_HOME=$JAVA_BIN/../ 
STATIC_WEB_DIR=../../../webapp/static/

# Overlay the source, do the build, and put the .apk in a web dir.
./deployfiles.sh "$ANDROIDSRCDIR" "$ANDROIDCORDOVAPROJDIR" && \
	JAVA_HOME=$JAVA_BIN/../ $ANDROIDCORDOVAPROJDIR/cordova/build && \
	cp -v $ANDROIDCORDOVAPROJDIR/bin/BeeawareBeacon-debug.apk $STATIC_WEB_DIR 
