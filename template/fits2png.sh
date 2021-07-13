#!/bin/sh
files="$1*.fits"
for f in $files
do
	filename="$f.png"
	echo $filename
	ds9 "$f" -zoom to fit -zscale -saveimage png $filename -quit
done