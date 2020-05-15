#!/bin/bash

DIR="./Resources/Models/DeOldify/models"
if [ ! -d "$DIR" ]; then
    mkdir -p ${DIR}
fi

cd ${DIR} || true

MODELNAME="ColorizeArtistic_gen.pth"
WATERMARK="watermark.png"

FILE="${MODELNAME}"
if [ -f "${FILE}" ]
then
	echo "${FILE} found, skipping.."
else
	wget --no-check-certificate https://bh.singularitynet.io:7000/PreTrainedDNNModels/Image/deoldify-colorizer/${FILE}
fi

FILE="${WATERMARK}"
if [ -f "${FILE}" ]
then
	echo "${FILE} found, skipping.."
else
	wget --no-check-certificate https://bh.singularitynet.io:7000/PreTrainedDNNModels/Image/deoldify-colorizer/${FILE}
fi
