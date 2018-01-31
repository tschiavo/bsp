SRCDIR=~/beeaware/
ANDROIDSRCDIR=$SRCDIR/locationapp/android

BUILDDIR=$SRCDIR/phone/beeawareandroid

JAVADIR=$BUILDDIR/java
JAVAPATH=http://download.oracle.com/otn-pub/java/jdk/7u51-b13/
JAVAFILE=jdk-7u51-linux-x64.tar.gz
JAVA_BIN=$JAVADIR/jdk1.7.0_51/bin

SDKDIR=$BUILDDIR/sdk
SDKPATH=http://dl.google.com/android/adt
SDKFILE=adt-bundle-linux-x86_64-20130729.zip

ANDROIDSDKDIR=$SDKDIR/adt-bundle-linux-x86_64-20130729/sdk
ANDROID_TOOLS_BIN=$ANDROIDSDKDIR/tools/
ANDROID_PLATFORM_TOOLS_BIN=$ANDROIDSDKDIR/platform-tools/

CORDOVADIR=$BUILDDIR/cordova
CORDOVAPATH=http://archive.apache.org/dist/cordova
CORDOVAFILE=cordova-3.3.0-src.zip

UNPACKEDCORDOVADIR=$CORDOVADIR/cordova-3.3.0

ANDROIDCORDOVADIR=$UNPACKEDCORDOVADIR/cordova-android
ANDROIDCORDOVAFILE=cordova-android.zip
UNPACKEDANDROIDCORDOVADIR=$UNPACKEDCORDOVADIR/cordova-android/cordova-android

CORDOVAPROJDIR=$BUILDDIR/proj
ANDROIDCORDOVAPROJDIR=$CORDOVAPROJDIR/android/
