#!/bin/bash
scripts=/home/acm/Scripts
model=$1
scene=$2
gpu=$3
img=$4
bRange=$5

echo Model: $1/$2 img_type $img
echo ChangeType: $5

echo Building model on gpu $1
python $scripts/build.py -s $model -x $scene -g $gpu -i $img -p 3 -v .01
python $scripts/build.py -s $model -x $scene -g $gpu -i $img -p 2 -v .01 -r

echo Rendering change images
python $scripts/render_changes.py -s $model -x $scene -g $gpu -i $img 

echo Rendering blob images
python $scripts/render_blobImgs.py -s $model -x $scene -g $gpu -i $img -r $bRange
python $scripts/render_blobImgs.py -s $model -x $scene -g $gpu -i $img -r $bRange -k 

