. locations.sh

if [[ ! -d "$JAVADIR" ]]; then
	mkdir -p "$JAVADIR"
	tar zxvf "$BUILDDIR/$JAVAFILE" --directory "$JAVADIR"
fi

if [[ ! -d "$SDKDIR" ]]; then
	unzip -d "$SDKDIR" "$BUILDDIR/$SDKFILE"
fi

if [[ ! -d "$CORDOVADIR" ]]; then
	unzip -d "$CORDOVADIR" "$BUILDDIR/$CORDOVAFILE"
fi

if [[ ! -d "$ANDROIDCORDOVADIR" ]]; then
	unzip -d "$ANDROIDCORDOVADIR" "$UNPACKEDCORDOVADIR/$ANDROIDCORDOVAFILE"
fi

