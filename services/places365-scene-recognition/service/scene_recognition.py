# PlacesCNN to predict the scene category, attribute, and class activation map in a single pass
# by Bolei Zhou, sep 2, 2017
# Turned into a SingularityNET service by Ramon Durães, dec 11, 2018

import torch
from torch.autograd import Variable as V
from torchvision import transforms as trn
from torch.nn import functional as F
import os
import numpy as np
from scipy.misc import imresize as imresize
import cv2
from PIL import Image
import logging
import service
from service.serviceUtils import jpg_to_base64
from service import wideresnet as wideresnet

logging.basicConfig(
    level=10, format="%(asctime)s - [%(levelname)8s] - %(name)s - %(message)s"
)
log = logging.getLogger("places365_scene_recognition_service")

models_root = os.path.join("..", "..", "utils", "Resources", "Models")


class SceneRecognitionModel:

    def __init__(self):
        # load the labels
        self.classes, self.labels_io, self.labels_attribute, self.w_attribute = self.load_labels()

        # load the model
        self.features_blobs = []
        self.model = self.load_model()

        # load the transformer
        self.tf = self.return_tf()  # image transformer

        # get the softmax weights
        self.params = list(self.model.parameters())

        weight_softmax = self.params[-2].data.numpy()
        weight_softmax[weight_softmax < 0] = 0
        self.weight_softmax = weight_softmax

    @staticmethod
    def load_labels():
        """Loads labels related to scene categories, indoor/outdoor places and scene attributes."""

        # prepare all the labels
        # scene category relevant
        file_name_category = os.path.join(models_root, 'categories_places365.txt')
        if not os.access(file_name_category, os.W_OK):
            log.error("Categories file not found under its path ({}). Please run the model downloading script provided."
                      .format(file_name_category))
            exit(1)
        classes = list()
        with open(file_name_category) as class_file:
            for line in class_file:
                classes.append(line.strip().split(' ')[0][3:])
        classes = tuple(classes)

        # indoor and outdoor relevant
        file_name_io = os.path.join(models_root, 'IO_places365.txt')
        if not os.access(file_name_io, os.W_OK):
            log.error("IO file not found under its path ({}). Please run the model downloading script provided."
                      .format(file_name_io))
            exit(1)
        with open(file_name_io) as f:
            lines = f.readlines()
            labels_io = []
            for line in lines:
                items = line.rstrip().split()
                labels_io.append(int(items[-1]) - 1)  # 0 is indoor, 1 is outdoor
        labels_io = np.array(labels_io)

        # scene attribute relevant
        file_name_attribute = os.path.join(models_root, 'labels_sunattribute.txt')
        if not os.access(file_name_attribute, os.W_OK):
            log.error("Attributes file not found under its path ({}). Please run the model downloading script provided."
                      .format(file_name_attribute))
            exit(1)
        with open(file_name_attribute) as f:
            lines = f.readlines()
            labels_attribute = [item.rstrip() for item in lines]
        file_name_w = os.path.join(models_root, 'W_sceneattribute_wideresnet18.npy')
        if not os.access(file_name_w, os.W_OK):
            log.error("Attributes file not found under its path ({}). Please run the model downloading script provided."
                      .format(file_name_w))
            exit(1)
        w_attribute = np.load(file_name_w)

        return classes, labels_io, labels_attribute, w_attribute

    def hook_feature(self, module, input, output):
        self.features_blobs.append(np.squeeze(output.data.cpu().numpy()))

    @staticmethod
    def return_cam(feature_conv, weight_softmax, class_idx):
        """ Returns Class Activation Mappings (heatmaps that highlight the most relevant areas of the image for the
        prediction). """
        # generate the class activation maps upsample to 256x256
        size_upsample = (256, 256)
        nc, h, w = feature_conv.shape
        output_cam = []
        # for idx in class_idx:
        cam = weight_softmax[class_idx].dot(feature_conv.reshape((nc, h * w)))
        cam = cam.reshape(h, w)
        cam = cam - np.min(cam)
        cam_img = cam / np.max(cam)
        cam_img = np.uint8(255 * cam_img)
        output_cam.append(imresize(cam_img, size_upsample))
        return output_cam

    @staticmethod
    def return_tf():
        # load the image transformer
        tf = trn.Compose([
            trn.Resize((224, 224)),
            trn.ToTensor(),
            trn.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
        ])
        return tf

    def load_model(self):
        """ Loads CNN model. """
        # this model has a last conv feature map as 14x14
        model_file = 'wideresnet18_places365.pth.tar'
        model_path = os.path.join(models_root, model_file)
        if not os.access(model_path, os.W_OK):
            log.error("Model file not found under its path ({}). Please run the model downloading script provided.".
                      format(model_path))
            exit(1)

        model = wideresnet.resnet18(num_classes=365)
        checkpoint = torch.load(model_path, map_location=lambda storage, loc: storage)
        state_dict = {str.replace(k, 'module.', ''): v for k, v in checkpoint['state_dict'].items()}
        model.load_state_dict(state_dict)
        model.eval()

        # hook the feature extractor
        features_names = ['layer4', 'avgpool']  # this is the last conv layer of the resnet
        for name in features_names:
            model._modules.get(name).register_forward_hook(self.hook_feature)
        return model

    def recognize(self, input_image_path, predict, cam_path):
        """ Performs scene recognition: predicts scene attributes, category, indoor/outdoor and class activation
        mappings. """
        log.debug("Input image path : {}".format(input_image_path))
        result = {}

        # load the test image
        img = Image.open(input_image_path)
        input_img = V(self.tf(img).unsqueeze(0))

        # forward pass
        logit = self.model.forward(input_img)
        h_x = F.softmax(logit, 1).data.squeeze()
        probs, idx = h_x.sort(0, True)
        probs = probs.numpy()
        idx = idx.numpy()

        log.debug('RESULT ON ' + input_image_path)

        # Output the IO prediction
        if "io" in predict:
            io_image = np.mean(self.labels_io[idx[:10]])  # vote for the indoor or outdoor
            if io_image < 0.5:
                result["io"] = "indoor"
                log.debug('--TYPE OF ENVIRONMENT: indoor')
            else:
                result["io"] = "outdoor"
                log.debug('--TYPE OF ENVIRONMENT: outdoor')

        # Output the prediction of scene category
        if "categories" in predict:
            result["categories"] = ""
            log.debug('--SCENE CATEGORIES:')
            for i in range(0, 5):
                category = ' {:.3f} -> {},'.format(probs[i], self.classes[idx[i]])
                result["categories"] += category
                log.debug(category)

        # output the scene attributes
        if "attributes" in predict:
            responses_attribute = self.w_attribute.dot(self.features_blobs[1])
            idx_a = np.argsort(responses_attribute)
            log.debug('--SCENE ATTRIBUTES:')
            attributes = ', '.join([self.labels_attribute[idx_a[i]] for i in range(-1, -10, -1)])
            result["attributes"] = attributes
            log.debug(attributes)

        # generate class activation mapping
        if "cam" in predict:
            cams = self.return_cam(self.features_blobs[0], self.weight_softmax, [idx[0]])
            img = cv2.imread(input_image_path)
            height, width, _ = img.shape
            heatmap = cv2.applyColorMap(cv2.resize(cams[0], (width, height)), cv2.COLORMAP_JET)
            cam_result = heatmap * 0.4 + img * 0.5
            cv2.imwrite(cam_path, cam_result)
            log.debug('Class activation mapping is saved at {}'.format(cam_path))
            result["cam"] = service.serviceUtils.jpg_to_base64(cam_path, open_file=True).decode("utf-8")
        return result
