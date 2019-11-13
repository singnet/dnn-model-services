#!/usr/bin/env sh
# This script downloads the PLACES365 model and lists of categories and attributes necessary

DIR="./Resources/Models"
if [ ! -d "${DIR}" ]; then
    mkdir -p ${DIR}
fi

cd ${DIR} || true

echo "Downloading Places365 model and text files [~ 45 Mb] ..."

FILE="wideresnet18_places365.pth.tar"
if [ -f "${FILE}" ]
then
	echo "${FILE} found, skipping.."
else
	wget --no-check-certificate http://places2.csail.mit.edu/models_places365/wideresnet18_places365.pth.tar
fi

FILE="categories_places365.txt"
if [ -f "${FILE}" ]
then
	echo "${FILE} found, skipping.."
else
	wget --no-check-certificate https://raw.githubusercontent.com/csailvision/places365/master/categories_places365.txt
fi

FILE="IO_places365.txt"
if [ -f "${FILE}" ]
then
	echo "${FILE} found, skipping.."
else
	wget --no-check-certificate https://raw.githubusercontent.com/csailvision/places365/master/IO_places365.txt
fi

FILE="labels_sunattribute.txt"
if [ -f "${FILE}" ]
then
	echo "${FILE} found, skipping.."
else
	wget --no-check-certificate https://raw.githubusercontent.com/csailvision/places365/master/labels_sunattribute.txt
fi

FILE="W_sceneattribute_wideresnet18.npy"
if [ -f "${FILE}" ]
then
	echo "${FILE} found, skipping.."
else
	wget --no-check-certificate http://places2.csail.mit.edu/models_places365/W_sceneattribute_wideresnet18.npy
fi
