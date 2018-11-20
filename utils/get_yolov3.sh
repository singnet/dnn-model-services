#!/usr/bin/env sh
# This script downloads the YOLOv3 model and config file

DIR="./Resources/Models"
if [ ! -d "$DIR" ]; then
    mkdir -p ${DIR}
fi

cd ${DIR}

echo "Downloading YOLOv3 files [~240MB] ..."

file="yolov3.weights"
if [ -f "$file" ]
then
	echo "$file found, skipping.."
else
	wget --no-check-certificate https://pjreddie.com/media/files/yolov3.weights
fi

file="yolov3.cfg"
if [ -f "$file" ]
then
	echo "$file found, skipping.."
else
	wget --no-check-certificate https://raw.githubusercontent.com/pjreddie/darknet/master/cfg/yolov3.cfg
fi