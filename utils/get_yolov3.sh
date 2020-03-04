#!/usr/bin/env sh
# This script downloads the YOLOv3 model and config file

DIR="./Resources/Models"
if [ ! -d "$DIR" ]; then
    mkdir -p ${DIR}
fi

cd ${DIR} || true

echo "Downloading YOLOv3 files [~240MB] ..."

FILE="yolov3.weights"
if [ -f "${FILE}" ]
then
	echo "${FILE} found, skipping.."
else
	wget --no-check-certificate http://54.203.198.53:7000/PreTrainedDNNModels/Image/yolov3-object-detection/yolov3.weights
fi

FILE="yolov3.cfg"
if [ -f "${FILE}" ]
then
	echo "${FILE} found, skipping.."
else
	wget --no-check-certificate http://54.203.198.53:7000/PreTrainedDNNModels/Image/yolov3-object-detection/yolov3.cfg
fi