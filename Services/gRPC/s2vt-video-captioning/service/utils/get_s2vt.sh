#!/usr/bin/env sh
# This script downloads the trained S2VT VGG (RGB) model,
# associated vocabulary, and frame features for the validation set.

DIR="./data"
if [ ! -d "$DIR" ]; then
    mkdir -p ${DIR}
fi

cd ${DIR}

echo "Downloading Model and Data [~400MB] ..."

file="s2vt_vgg_rgb.caffemodel"
if [ -f "$file" ]
then
	echo "$file found, skipping.."
else
	wget --no-check-certificate https://www.dropbox.com/s/wn6k2oqurxzt6e2/s2s_vgg_pstream_allvocab_fac2_iter_16000.caffemodel
	mv s2s_vgg_pstream_allvocab_fac2_iter_16000.caffemodel "s2vt_vgg_rgb.caffemodel"
fi

file="yt_coco_mvad_mpiimd_vocabulary.txt"
if [ -f "$file" ]
then
	echo "$file found, skipping.."
else
	wget --no-check-certificate https://www.dropbox.com/s/v1lrc6leknzgn3x/yt_coco_mvad_mpiimd_vocabulary.txt
fi

file="s2vt.words_to_preds.deploy.prototxt"
if [ -f "$file" ]
then
	echo "$file found, skipping.."
else
	wget --no-check-certificate https://raw.githubusercontent.com/vsubhashini/caffe/recurrent/examples/s2vt/s2vt.words_to_preds.deploy.prototxt
fi

file="VGG_ILSVRC_16_layers.caffemodel"
if [ -f "$file" ]
then
	echo "$file found, skipping.."
else
	wget --no-check-certificate http://www.robots.ox.ac.uk/~vgg/software/very_deep/caffe/VGG_ILSVRC_16_layers.caffemodel
fi

file="VGG_ILSVRC_16_layers_deploy.prototxt"
if [ -f "$file" ]
then
	echo "$file found, skipping.."
else
    wget --no-check-certificate https://gist.githubusercontent.com/ksimonyan/211839e770f7b538e2d8/raw/ded9363bd93ec0c770134f4e387d8aaaaa2407ce/VGG_ILSVRC_16_layers_deploy.prototxt
fi