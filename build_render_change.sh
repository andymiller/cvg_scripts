#!/bin/bash

model=$1
scene=$2
gpu=$3
img=$4
changeType=$5

echo Model: $1/$2 img_type $img
echo ChangeType: $5

echo Building model on gpu $1
python /home/acm/cvg_scripts/build.py -s $model -x $scene -g $gpu -i $img -p 3
python /home/acm/cvg_scripts/build.py -s $model -x $scene -g $gpu -i $img -p 1 -r

echo Rendering change images
python /home/acm/cvg_scripts/render_changes.py -s $model -x $scene -g $gpu -i $img 

echo Rendering blob images
python /home/acm/cvg_scripts/render_blobImgs.py -s $model -x $scene -g $gpu 
python /home/acm/cvg_scripts/render_blobImgs.py -s $model -x $scene -g $gpu -k

