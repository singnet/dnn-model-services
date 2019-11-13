#!/usr/bin/env sh
# This script downloads the Real-Time-Voice-Cloning pre trained model,

DIR="./services/real-time-voice-cloning/rtvc"

cd ${DIR} || true

echo "Downloading model [~366MB] ..."

MODEL_FILENAME="pretrained.zip"

FILE="${MODEL_FILENAME}"
if [ -f "${FILE}" ]
then
	echo "${FILE} found, skipping.."
else
	wget --no-check-certificate http://54.203.198.53:7000/PreTrainedDNNModels/Voice/real-time-voice-cloning/${MODEL_FILENAME}
fi

unzip -o "${MODEL_FILENAME}"
