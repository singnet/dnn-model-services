#!/usr/bin/python

import matplotlib.pyplot as plt
import numpy as np
import os
import sys
import argparse

# sys.path.append('../../python/')
import caffe


class FeatureExtractor():
    def __init__(self, weights_path, image_net_proto, device_id=-1):
        if device_id >= 0:
            caffe.set_mode_gpu()
            caffe.set_device(device_id)
        else:
            caffe.set_mode_cpu()
        # Setup image processing net.
        phase = caffe.TEST
        self.image_net = caffe.Net(image_net_proto, weights_path, phase)
        image_data_shape = self.image_net.blobs['data'].data.shape
        self.transformer = caffe.io.Transformer({'data': image_data_shape})
        channel_mean = np.zeros(image_data_shape[1:])
        channel_mean_values = [104, 117, 123]
        assert channel_mean.shape[0] == len(channel_mean_values)
        for channel_index, mean_val in enumerate(channel_mean_values):
            channel_mean[channel_index, ...] = mean_val
        self.transformer.set_mean('data', channel_mean)
        self.transformer.set_channel_swap('data', (2, 1, 0))  # BGR
        self.transformer.set_transpose('data', (2, 0, 1))

    def set_image_batch_size(self, batch_size):
        self.image_net.blobs['data'].reshape(batch_size,
                                             *self.image_net.blobs['data'].data.shape[1:])

    def preprocess_image(self, image):
        if type(image) in (str, unicode):
            image = plt.imread(image)
        crop_edge_ratio = (256. - 224.) / 256. / 2
        ch = int(image.shape[0] * crop_edge_ratio + 0.5)
        cw = int(image.shape[1] * crop_edge_ratio + 0.5)
        cropped_image = image[ch:-ch, cw:-cw]
        if len(cropped_image.shape) == 2:
            cropped_image = np.tile(cropped_image[:, :, np.newaxis], (1, 1, 3))
        preprocessed_image = self.transformer.preprocess('data', cropped_image)
        print('Preprocessed image has shape %s, range (%f, %f)' % (
            preprocessed_image.shape,
            preprocessed_image.min(),
            preprocessed_image.max()))
        return preprocessed_image

    def image_to_feature(self, image, output_name='fc7'):
        net = self.image_net
        if net.blobs['data'].data.shape[0] > 1:
            batch = np.zeros_like(net.blobs['data'].data)
            batch[0] = image
        else:
            batch = image.reshape(net.blobs['data'].data.shape)
        net.forward(data=batch)
        feature = net.blobs[output_name].data[0].copy()
        return feature

    def compute_features(self, image_list, output_name='fc7'):
        batch = np.zeros_like(self.image_net.blobs['data'].data)
        batch_shape = batch.shape
        batch_size = batch_shape[0]
        features_shape = (len(image_list),) + self.image_net.blobs[output_name].data.shape[1:]
        features = np.zeros(features_shape)
        for batch_start_index in range(0, len(image_list), batch_size):
            batch_list = image_list[batch_start_index:(batch_start_index + batch_size)]
            for batch_index, image_path in enumerate(batch_list):
                batch[batch_index:(batch_index + 1)] = self.preprocess_image(image_path)
            current_batch_size = min(batch_size, len(image_list) - batch_start_index)
            print('Computing features for images %d-%d of %d' % (
                batch_start_index,
                batch_start_index + current_batch_size - 1,
                len(image_list)))
            self.image_net.forward(data=batch)
            features[batch_start_index:(batch_start_index + current_batch_size)] = \
                self.image_net.blobs[output_name].data[:current_batch_size]
        return features


def write_features_to_file(image_list, features, batch_size, output_file):
    vid_pool = 0
    with open(output_file, 'w') as opfd:
        for i, image_path in enumerate(image_list):
            image_feature = features[i].tolist()
            text_features = ','.join(map(str, image_feature))
            if not i % batch_size:
                vid_pool += 1
            opfd.write('%s_%s,%s\n' % (str(vid_pool), i, text_features))


def compute_single_image_feature(feature_extractor, image_path, batch_size, out_file):
    assert os.path.exists(image_path)
    preprocessed_image = feature_extractor.preprocess_image(image_path)
    feature = feature_extractor.image_to_feature(preprocessed_image)
    write_features_to_file([image_path], [feature], batch_size, out_file)


def compute_image_list_features_from_path(feature_extractor, images_file_path, batch_size, out_file):
    assert os.path.exists(images_file_path)
    with open(images_file_path, 'r') as infd:
        image_list = infd.read().splitlines()
    features = feature_extractor.compute_features(image_list)
    write_features_to_file(image_list, features, batch_size, out_file)


def compute_image_list_features(feature_extractor, image_list, batch_size, out_file):
    features = feature_extractor.compute_features(image_list)
    write_features_to_file(image_list, features, batch_size, out_file)


# For external use.
# Extracts features from a frame list (img_list) and save them into output_file.
def extractor(model_file, net_file, img_list, output_file, batch_size):
    try:
        feature_extractor = FeatureExtractor(model_file, net_file, 0)
        feature_extractor.set_image_batch_size(batch_size)
        compute_image_list_features(feature_extractor, img_list, batch_size, output_file)
        return True
    except Exception as e:
        print(e)
        return False


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-l", "--imagelist", type=str, help='list of images (one per line)')
    parser.add_argument("-o", "--output", type=str, help='output features file')
    parser.add_argument("-b", "--batchsize", type=int, help='size of batch')
    parser.add_argument("-n", "--net", type=int, help='size of batch')
    args = parser.parse_args()

    BASE_DIR = ''
    IMAGE_LIST_FILE = args.imagelist if args.imagelist else 'images_paths_list.txt'
    # IMAGE_PATH = '../images/cat.jpg'
    OUTPUT_FILE = args.output if args.output else 'output_features.csv'
    BATCH_SIZE = args.batchsize if args.batchsize else 10

    # NOTE: Download these files from the Caffe Model Zoo.
    net_layer = args.net if args.net else 16
    IMAGE_NET_FILE = './utils/data/vgg_orig_16layer.deploy.prototxt'
    MODEL_FILE = BASE_DIR + './utils/data/VGG_ILSVRC_16_layers.caffemodel'
    if net_layer == 19:
        IMAGE_NET_FILE = './utils/data/vgg_orig_19layer.deploy.prototxt'
        MODEL_FILE = BASE_DIR + './utils/data/VGG_ILSVRC_19_layers.caffemodel'
    elif net_layer == 1:
        IMAGE_NET_FILE = './utils/data/vgg16_low_noise.prototxt'
        MODEL_FILE = BASE_DIR + './utils/data/VGG16_SOD_finetune.caffemodel'
    elif net_layer == 152:
        IMAGE_NET_FILE = './utils/data/ResNet-152-deploy.prototxt'
        MODEL_FILE = BASE_DIR + './utils/data/ResNet-152-model.caffemodel'

    DEVICE_ID = 0
    feature_extractor = FeatureExtractor(MODEL_FILE, IMAGE_NET_FILE, DEVICE_ID)
    feature_extractor.set_image_batch_size(BATCH_SIZE)

    # compute features for a list of images in a file
    compute_image_list_features_from_path(feature_extractor, IMAGE_LIST_FILE, BATCH_SIZE, OUTPUT_FILE)
    # compute features for a single image
    # feature_extractor.set_image_batch_size(1)
    # compute_single_image_feature(feature_extractor, IMAGE_PATH, OUTPUT_FILE)


if __name__ == "__main__":
    main()