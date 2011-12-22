#!/bin/bash

inglob=$1
outdir=$2

echo "Convert images from glob $inglob to $outdir/*.png"
for img in $inglob; do 
  echo "Converting image: $img";
  convert $img $outdir/`basename $img .tiff`.png; 
done
