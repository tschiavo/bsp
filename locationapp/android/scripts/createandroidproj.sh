. locations.sh

PATH=$PATH:$ANDROID_TOOLS_BIN:$ANDROID_PLATFORM_TOOLS_BIN
PATH=$PATH:$JAVA_BIN

if [[ ! -d "$ANDROIDSDKDIR/platforms/android-19" ]]; then
	echo "y" | android update sdk --force --no-ui --filter android-19
fi

#if [[ ! -e "$ANDROIDSDKDIR/platform-tools/aapt" ]]; then
#	ln -s $ANDROIDSDKDIR/build-tools/android-4.3/aapt \
#		$ANDROIDSDKDIR/platform-tools/aapt
#fi

#if [[ ! -d "$ANDROIDCORDOVAPROJDIR" ]]; then

    #mkdir -p "$ANDROIDCORDOVAPROJDIR/assets"

    ABSANDROIDCORDOVAPROJDIR=$(readlink -m "$ANDROIDCORDOVAPROJDIR")

	JAVA_HOME=$JAVA_BIN/../ \
		"$UNPACKEDANDROIDCORDOVADIR/bin/create" \
		"$ABSANDROIDCORDOVAPROJDIR" \
		"org.yerr.beeaware.beacon" \
		"BeeawareBeacon"
#fi

