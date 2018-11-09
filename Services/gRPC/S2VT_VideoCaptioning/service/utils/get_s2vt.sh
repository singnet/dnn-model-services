#!/usr/bin/env sh
# This script downloads the trained S2VT VGG (RGB) model,
# associated vocabulary, and frame features for the validation set.

echo "Downloading Model and Data [~400MB] ..."

wget --no-check-certificate https://www.dropbox.com/s/wn6k2oqurxzt6e2/s2s_vgg_pstream_allvocab_fac2_iter_16000.caffemodel
wget --no-check-certificate https://www.dropbox.com/s/v1lrc6leknzgn3x/yt_coco_mvad_mpiimd_vocabulary.txt
wget --no-check-certificate https://raw.githubusercontent.com/vsubhashini/caffe/recurrent/examples/s2vt/s2vt.words_to_preds.deploy.prototxt
wget --no-check-certificate http://www.robots.ox.ac.uk/~vgg/software/very_deep/caffe/VGG_ILSVRC_16_layers.caffemodel
wget --no-check-certificate https://gist.githubusercontent.com/ksimonyan/211839e770f7b538e2d8/raw/ded9363bd93ec0c770134f4e387d8aaaaa2407ce/VGG_ILSVRC_16_layers_deploy.prototxt

echo "Organizing..."

DIR="./data"
if [ ! -d "$DIR" ]; then
    mkdir $DIR
fi
mv s2s_vgg_pstream_allvocab_fac2_iter_16000.caffemodel $DIR"/s2vt_vgg_rgb.caffemodel"
mv yt_coco_mvad_mpiimd_vocabulary.txt $DIR"/"
mv s2vt.words_to_preds.deploy.prototxt $DIR"/"
mv VGG_ILSVRC_16_layers.caffemodel $DIR"/"
mv VGG_ILSVRC_16_layers_deploy.prototxt $DIR"/"
echo "Done."