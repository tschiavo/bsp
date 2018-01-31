. locations.sh

if [[ ! -e "$BUILDDIR/$JAVAFILE" ]]; then
	wget --no-check-certificate --no-cookies \
		--header "Cookie: oraclelicense=accept-securebackup-cookie" \
		-O "$BUILDDIR/$JAVAFILE" "$JAVAPATH/$JAVAFILE" 
fi

if [[ ! -e "$BUILDDIR/$SDKFILE" ]]; then
	wget -O "$BUILDDIR/$SDKFILE" "$SDKPATH/$SDKFILE" 
fi

if [[ ! -e "$BUILDDIR/$CORDOVAFILE" ]]; then
	wget -O "$BUILDDIR/$CORDOVAFILE" "$CORDOVAPATH/$CORDOVAFILE"
fi
