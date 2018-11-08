#!/usr/bin/env sh
# This script downloads the YOLOv3 model and config file,

echo "Downloading YOLOv3 files [~240MB] ..."

wget --no-check-certificate https://pjreddie.com/media/files/yolov3.weights
wget --no-check-certificate https://github.com/pjreddie/darknet/blob/master/cfg/yolov3.cfg

DIR="./Resources/Models"
if [ ! -d "$DIR" ]; then
    mkdir -p ${DIR}
fi

mv yolov3.weights ${DIR}"/"
mv yolov3.cfg ${DIR}"/"