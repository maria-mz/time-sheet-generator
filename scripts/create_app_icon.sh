#!/bin/bash
# Create the .icns file for the app icon png.
# Adapted from https://stackoverflow.com/questions/12306223/how-to-manually-create-icns-files-using-iconutil

ICON_NAME="app-icon"
ICON="assets/icons/$ICON_NAME.png"

mkdir $ICON_NAME.iconset

sips -z 16 16     $ICON --out $ICON_NAME.iconset/icon_16x16.png
sips -z 32 32     $ICON --out $ICON_NAME.iconset/icon_16x16@2x.png
sips -z 32 32     $ICON --out $ICON_NAME.iconset/icon_32x32.png
sips -z 64 64     $ICON --out $ICON_NAME.iconset/icon_32x32@2x.png
sips -z 128 128   $ICON --out $ICON_NAME.iconset/icon_128x128.png
sips -z 256 256   $ICON --out $ICON_NAME.iconset/icon_128x128@2x.png
sips -z 256 256   $ICON --out $ICON_NAME.iconset/icon_256x256.png
sips -z 512 512   $ICON --out $ICON_NAME.iconset/icon_256x256@2x.png
sips -z 512 512   $ICON --out $ICON_NAME.iconset/icon_512x512.png
sips -z 512 512   $ICON --out $ICON_NAME.iconset/icon_512x512@2x.png

iconutil -c icns $ICON_NAME.iconset

rm -R $ICON_NAME.iconset

mv $ICON_NAME.icns assets/icons/
