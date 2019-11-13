#!/usr/bin/env sh
# This script downloads the VGG19 Pneumonia model

DIR="./Resources/Models"
if [ ! -d "$DIR" ]; then
    mkdir -p ${DIR}
fi

cd ${DIR} || true

echo "Downloading VGG19 Pneumonia Model files [~180MB] ..."

FILE="PneumoniaModel.h5"
if [ -f "${FILE}" ]
then
	echo "${FILE} found, skipping.."
else
	wget --no-check-certificate https://snet-models.s3.amazonaws.com/bh/PneumoniaDiagnosis/PneumoniaModel.h5
fi
