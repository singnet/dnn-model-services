#!/usr/bin/env sh
# This script downloads the CNTK pre trained ResNet152 models on flowers and dogs datasets,

echo "Downloading CNTK ResNet152 models [~450MB] ..."

DOGS_RESNET152="dogs_ResNet152_20.model"
FLOWERS_RESNET152="flowers_ResNet152_20.model"
wget --no-check-certificate http://54.203.198.53:7000/PreTrainedDNNModels/Image/CNTK_ImageRecon/${DOGS_RESNET152}
wget --no-check-certificate http://54.203.198.53:7000/PreTrainedDNNModels/Image/CNTK_ImageRecon/${FLOWERS_RESNET152}

DIR="./Resources/Models"
if [ ! -d "$DIR" ]; then
    mkdir -p ${DIR}
fi

mv ${DOGS_RESNET152} ${DIR}"/"
mv ${FLOWERS_RESNET152} ${DIR}"/"