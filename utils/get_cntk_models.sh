#!/usr/bin/env sh
# This script downloads the CNTK pre trained ResNet152 models on flowers and dogs datasets,

DIR="./Resources/Models"
if [ ! -d "$DIR" ]; then
    mkdir -p ${DIR}
fi

cd ${DIR}

echo "Downloading CNTK ResNet152 models [~450MB] ..."

DOGS_RESNET152="dogs_ResNet152_20.model"
FLOWERS_RESNET152="flowers_ResNet152_20.model"

file="$DOGS_RESNET152"
if [ -f "$file" ]
then
	echo "$file found, skipping.."
else
	wget --no-check-certificate http://54.203.198.53:7000/PreTrainedDNNModels/Image/cntk-image-recon/${DOGS_RESNET152}
fi

file="$FLOWERS_RESNET152"
if [ -f "$file" ]
then
	echo "$file found, skipping.."
else
	wget --no-check-certificate http://54.203.198.53:7000/PreTrainedDNNModels/Image/cntk-image-recon/${FLOWERS_RESNET152}
fi