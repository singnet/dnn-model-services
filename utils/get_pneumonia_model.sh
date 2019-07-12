#!/usr/bin/env sh
# This script downloads the VGG19 Pneumonia model

DIR="./Resources/Models"
if [ ! -d "$DIR" ]; then
    mkdir -p ${DIR}
fi

cd ${DIR}

echo "Downloading VGG19 Pneumonia Model files [~180MB] ..."

file="PneumoniaModel.h5"
if [ -f "$file" ]
then
	echo "$file found, skipping.."
else
	wget --no-check-certificate https://snet-models.s3.amazonaws.com/bh/PneumoniaDiagnosis/PneumoniaModel.h5
fi
