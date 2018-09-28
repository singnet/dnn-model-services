from __future__ import print_function
import glob
import os
import numpy as np
from PIL import Image

# Some of the flowers data is stored as .mat files
from scipy.io import loadmat

import tarfile
import time
import traceback

import cntk.io.transforms as xforms

from urllib.request import urlretrieve

import zipfile
import requests

# Import CNTK and helpers
import cntk
import cv2

from registry import (
    flowers_map_names,
    dogs_map_names,
    imagenet_map_names,
    coco_map_names,
)

isFast = True
# cntk.device.try_set_default_device(C.device.gpu(0))


# By default, we store data in the Examples/Image directory under CNTK
# If you're running this _outside_ of CNTK, consider changing this
data_root = os.path.join(".", "Resources", "Examples", "Image")
data_sets_path = os.path.join(data_root, "DataSets")
output_path = os.path.join(".", "Resources", "Models")


def ensure_exists(path):
    if not os.path.exists(path):
        os.makedirs(path)


def write_to_file(file_path, img_paths, img_labels):
    with open(file_path, "w+") as f:
        for i in range(0, len(img_paths)):
            f.write("%s\t%s\n" % (os.path.abspath(img_paths[i]), img_labels[i]))


def download_unless_exists(url, filename, max_retries=3):
    """Download the file unless it already exists, with retry. Throws if all retries fail."""
    if os.path.exists(filename):
        print("Reusing locally cached: ", filename)
    else:
        print("Starting download of {} to {}".format(url, filename))
        retry_cnt = 0
        while True:
            try:
                urlretrieve(url, filename)
                print("Download completed.")
                return
            except Exception as e:
                print("Error: " + str(e))
                retry_cnt += 1
                if retry_cnt == max_retries:
                    print("Exceeded maximum retry count, aborting.")
                    raise
                print("Failed to download, retrying.")
                time.sleep(np.random.randint(1, 10))


def download_model(model_root=output_path, model_filename="ResNet_18_ImageNet_CNTK.model"):
    ensure_exists(model_root)
    model_uri = "https://www.cntk.ai/Models/CNTK_Pretrained/{}".format(model_filename)
    if "VGG" in model_filename:
        model_uri = "https://www.cntk.ai/Models/Caffe_Converted/{}".format(model_filename)
    if "yolo" in model_filename:
        model_uri = "https://raw.githubusercontent.com/arunponnusamy/object-detection-opencv/master/yolov3.cfg"
        model_local = os.path.join(model_root, "yolov3.cfg")
        download_unless_exists(model_uri, model_local)
        model_uri = "https://pjreddie.com/media/files/{}".format(model_filename)
    model_local = os.path.join(model_root, model_filename)
    download_unless_exists(model_uri, model_local)

    return model_local


def download_flowers_dataset(dataset_root=os.path.join(data_sets_path, "Flowers")):
    ensure_exists(dataset_root)
    flowers_uris = [
        "http://www.robots.ox.ac.uk/~vgg/data/flowers/102/102flowers.tgz",
        "http://www.robots.ox.ac.uk/~vgg/data/flowers/102/imagelabels.mat",
        "http://www.robots.ox.ac.uk/~vgg/data/flowers/102/setid.mat",
    ]
    flowers_files = [
        os.path.join(dataset_root, "102flowers.tgz"),
        os.path.join(dataset_root, "imagelabels.mat"),
        os.path.join(dataset_root, "setid.mat"),
    ]
    for uri, file in zip(flowers_uris, flowers_files):
        download_unless_exists(uri, file)
    tar_dir = os.path.join(dataset_root, "extracted")
    if not os.path.exists(tar_dir):
        print("Extracting {} to {}".format(flowers_files[0], tar_dir))
        os.makedirs(tar_dir)
        tarfile.open(flowers_files[0]).extractall(path=tar_dir)
    else:
        print("{} already extracted to {}, using existing version".format(flowers_files[0], tar_dir))

    flowers_data = {
        "data_folder": dataset_root,
        "training_map": os.path.join(dataset_root, "6k_img_map.txt"),
        "testing_map": os.path.join(dataset_root, "1k_img_map.txt"),
        "validation_map": os.path.join(dataset_root, "val_map.txt"),
        "full_map": os.path.join(dataset_root, "full_map.txt"),
    }

    if not os.path.exists(flowers_data["training_map"]):
        print("Writing map files ...")
        # get image paths and 0-based image labels
        image_paths = np.array(sorted(glob.glob(os.path.join(tar_dir, "jpg", "*.jpg"))))
        image_labels = loadmat(flowers_files[1])["labels"][0]
        image_labels -= 1

        # read set information from .mat file
        setid = loadmat(flowers_files[2])
        idx_train = setid["trnid"][0] - 1
        idx_test = setid["tstid"][0] - 1
        idx_val = setid["valid"][0] - 1

        # Confusingly the training set contains 1k images and the test set contains 6k images
        # We swap them, because we want to train on more data
        write_to_file(flowers_data["training_map"], image_paths[idx_train], image_labels[idx_train])
        write_to_file(flowers_data["testing_map"], image_paths[idx_test], image_labels[idx_test])
        write_to_file(flowers_data["validation_map"], image_paths[idx_val], image_labels[idx_val])
        write_to_file(flowers_data["full_map"], image_paths, image_labels)
        print("Map files written, dataset download and unpack completed.")
    else:
        print("Using cached map files.")

    return flowers_data


def download_animals_dataset(dataset_root=os.path.join(data_sets_path, "Animals")):
    ensure_exists(dataset_root)
    animals_uri = "https://www.cntk.ai/DataSets/Animals/Animals.zip"
    animals_file = os.path.join(dataset_root, "Animals.zip")
    download_unless_exists(animals_uri, animals_file)
    if not os.path.exists(os.path.join(dataset_root, "Test")):
        with zipfile.ZipFile(animals_file) as animals_zip:
            print("Extracting {} to {}".format(animals_file, dataset_root))
            animals_zip.extractall(path=os.path.join(dataset_root, ".."))
            print("Extraction completed.")
    else:
        print("Reusing previously extracted Animals data.")

    return {
        "training_folder": os.path.join(dataset_root, "Train"),
        "testing_folder": os.path.join(dataset_root, "Test"),
    }


def setup_imagenet(opt_model):
    if opt_model != "":
        if "VGG" in opt_model:
            model_filename = opt_model + "_ImageNet_Caffe.model"
        else:
            model_filename = opt_model + "_ImageNet_CNTK.model"
    else:
        opt_model = "ResNet18"
        model_filename = opt_model + "_ImageNet_CNTK.model"

    model_details = setup_base_model(opt_model, model_filename)

    set_model = {
        "model_file": model_details["model_file"],
        "results_file": os.path.join(
            output_path, "ImageNet_{}_Predic.txt".format(opt_model)
        ),
        "num_classes": 1000,
    }

    return set_model, model_details, imagenet_map_names


def setup_detect(opt_model):
    if opt_model != "":
        if "VGG" in opt_model:
            model_filename = opt_model + "_ImageNet_Caffe.model"
        elif "yolo" in opt_model:
            model_filename = opt_model + ".weights"
        else:
            model_filename = opt_model + "_ImageNet_CNTK.model"
    else:
        opt_model = "yolov3"
        model_filename = opt_model + ".weights"

    model_details = setup_base_model(opt_model, model_filename)

    classes = [v for k, v in coco_map_names.items()]
    colors = np.random.uniform(0, 255, size=(len(classes), 3))

    set_model = {
        "model_file": model_details["model_file"],
        "model_cfg": os.path.join(output_path, "{}.cfg".format(opt_model)),
        "results_file": os.path.join(
            output_path, "Detect_{}_Predic.txt".format(opt_model)
        ),
        "num_classes": 80,
        "classes": classes,
        "colors": colors,
    }

    return set_model, model_details, coco_map_names


def setup_flowers(num_epochs, opt_model, training=False):
    if training:
        print("Downloading flowers and animals data-set...")
        set_data = download_flowers_dataset()
        # animals_data = download_animals_dataset()
        print("All flowers data now available!")

    set_model = {
        "model_file": os.path.join(output_path, "flowers_{}_{}.model".format(opt_model, num_epochs)),
        "results_file": os.path.join(output_path, "flowers_{}_Predic.txt".format(opt_model, num_epochs)),
        "num_classes": 102,
    }

    if opt_model != "":
        if "VGG" in opt_model:
            model_filename = opt_model + "_ImageNet_Caffe.model"
        else:
            model_filename = opt_model + "_ImageNet_CNTK.model"
    else:
        opt_model = "ResNet18"
        model_filename = opt_model + "_ImageNet_CNTK.model"

    model_details = setup_base_model(opt_model, model_filename)

    return set_data, set_model, model_details, flowers_map_names


def setup_dogs(num_epochs, opt_model, training=False):
    dataset_root = os.path.join(data_sets_path, "Dogs")

    set_data = {
        "data_folder": dataset_root,
        "training_map": os.path.join(dataset_root, "dogs_train.txt"),
        "testing_map": os.path.join(dataset_root, "dogs_test.txt"),
        "validation_map": os.path.join(dataset_root, "dogs_valid.txt"),
        "full_map": os.path.join(dataset_root, "dogs_train.txt"),
    }

    set_model = {
        "model_file": os.path.join(output_path, "dogs_{}_{}.model".format(opt_model, num_epochs)),
        "results_file": os.path.join(output_path, "dogs_{}_{}_Predic.txt".format(opt_model, num_epochs)),
        "num_classes": 133,
    }
    # Get the images if they dont exist
    zip_dir = os.path.join(dataset_root)
    ensure_exists(zip_dir)
    if training:
        download_unless_exists("https://s3-us-west-1.amazonaws.com/udacity-aind/dog-project/dogImages.zip",
                               zip_dir + "/dogImages.zip")

    if not os.path.exists(zip_dir):
        print("Extracting {} to {}".format("dogImages.zip", zip_dir))
        os.makedirs(zip_dir)
        zip_ref = zipfile.ZipFile("dogImages.zip", "r")
        zip_ref.extractall(zip_dir)
        zip_ref.close()
    else:
        print("{} already extracted to {}, using existing version".format("dogImages.zip", zip_dir))

    # Creating the .maps files
    allfiles = glob.glob(os.getcwd() + "/Resources/Examples/Image/DataSets/Dogs/dogImages/train/*/*")
    with open(set_data["full_map"], "w+") as my_f:
        for file in allfiles:
            num_breed = file.split("/")[-2]
            num_breed = int(num_breed.split(".")[0]) - 1
            my_f.write(file + "\t" + str(num_breed) + "\n")
    allfiles = glob.glob(os.getcwd() + "/Resources/Examples/Image/DataSets/Dogs/dogImages/test/*/*")
    with open(set_data["testing_map"], "w+") as my_f:
        for file in allfiles:
            num_breed = file.split("/")[-2]
            num_breed = int(num_breed.split(".")[0]) - 1
            my_f.write(file + "\t" + str(num_breed) + "\n")
    allfiles = glob.glob(os.getcwd() + "/Resources/Examples/Image/DataSets/Dogs/dogImages/valid/*/*")
    with open(set_data["validation_map"], "w+") as my_f:
        for file in allfiles:
            num_breed = file.split("/")[-2]
            num_breed = int(num_breed.split(".")[0]) - 1
            my_f.write(file + "\t" + str(num_breed) + "\n")

    if opt_model != "":
        if "VGG" in opt_model:
            model_filename = opt_model + "_ImageNet_Caffe.model"
        else:
            model_filename = opt_model + "_ImageNet_CNTK.model"
    else:
        opt_model = "ResNet18"
        model_filename = opt_model + "_ImageNet_CNTK.model"

    model_details = setup_base_model(opt_model, model_filename)

    return set_data, set_model, model_details, dogs_map_names


# Creates a mini_batch source for training or testing
def create_mb_source(map_file, image_dims, num_classes, randomize=True):
    transforms = [
        xforms.scale(
            width=image_dims[2],
            height=image_dims[1],
            channels=image_dims[0],
            interpolations="linear",
        )
    ]

    return cntk.io.MinibatchSource(
        cntk.io.ImageDeserializer(
            map_file,
            cntk.io.StreamDefs(
                features=cntk.io.StreamDef(field="image", transforms=transforms),
                labels=cntk.io.StreamDef(field="label", shape=num_classes),
            ),
        ),
        randomize=randomize,
    )


# Creates the network model for transfer learning
def create_model(model_details, num_classes, input_features, new_prediction_node_name="prediction", freeze=False):
    # Load the pre-trained classification net and find nodes
    base_model = cntk.load_model(model_details["model_file"])
    feature_node = cntk.logging.find_by_name(base_model, model_details["feature_node_name"])

    last_node = cntk.logging.find_by_name(base_model, model_details["last_hidden_node_name"])
    if model_details["inception"]:
        node_outputs = cntk.logging.get_node_outputs(base_model)
        last_node = node_outputs[5]
        feature_node = cntk.logging.find_all_with_name(base_model, "")[-5]
    if model_details["vgg"]:
        last_node = cntk.logging.find_by_name(base_model, "prob")
        feature_node = cntk.logging.find_by_name(base_model, "data")

    # Clone the desired layers with fixed weights
    cloned_layers = cntk.combine([last_node.owner]).clone(
        cntk.CloneMethod.freeze if freeze else cntk.CloneMethod.clone,
        {feature_node: cntk.placeholder(name="features")},
    )

    # Add new dense layer for class prediction
    feat_norm = input_features - cntk.Constant(114)
    cloned_out = cloned_layers(feat_norm)
    z = cntk.layers.Dense(num_classes, activation=None, name=new_prediction_node_name)(cloned_out)

    return z


# Trains a transfer learning model
def train_model(model_details, num_classes, train_map_file, learning_params, max_images=-1):
    num_epochs = learning_params["max_epochs"]
    epoch_size = sum(1 for _ in open(train_map_file))
    if max_images > 0:
        epoch_size = min(epoch_size, max_images)
    mini_batch_size = learning_params["mb_size"]

    # Create the minibatch source and input variables
    mini_batch_source = create_mb_source(train_map_file, model_details["image_dims"], num_classes)
    image_input = cntk.input_variable(model_details["image_dims"])
    label_input = cntk.input_variable(num_classes)

    # Define mapping from reader streams to network inputs
    input_map = {
        image_input: mini_batch_source["features"],
        label_input: mini_batch_source["labels"],
    }

    # Instantiate the transfer learning model and loss function
    tl_model = create_model(
        model_details,
        num_classes,
        image_input,
        freeze=learning_params["freeze_weights"],
    )
    ce = cntk.cross_entropy_with_softmax(tl_model, label_input)
    pe = cntk.classification_error(tl_model, label_input)

    # Instantiate the trainer object
    lr_schedule = cntk.learning_parameter_schedule(learning_params["lr_per_mb"])
    mm_schedule = cntk.momentum_schedule(learning_params["momentum_per_mb"])
    learner = cntk.momentum_sgd(
        tl_model.parameters,
        lr_schedule,
        mm_schedule,
        l2_regularization_weight=learning_params["l2_reg_weight"],
    )
    trainer = cntk.Trainer(tl_model, (ce, pe), [learner])

    # Get mini_batches of images and perform model training
    print("Training transfer learning model for {0} epochs (epoch_size = {1}).".format(num_epochs, epoch_size))
    cntk.logging.log_number_of_parameters(tl_model)
    progress_printer = cntk.logging.ProgressPrinter(tag="Training", num_epochs=num_epochs)

    # Loop over epochs
    for epoch in range(num_epochs):
        sample_count = 0
        # Loop over mini_batches in the epoch
        while sample_count < epoch_size:
            data = mini_batch_source.next_minibatch(min(mini_batch_size, epoch_size - sample_count),
                                                    input_map=input_map)

            # Update model with it
            trainer.train_minibatch(data)

            # Count samples processed so far
            sample_count += trainer.previous_minibatch_sample_count
            progress_printer.update_with_trainer(trainer, with_metric=True)

            if sample_count % (100 * mini_batch_size) == 0:
                print("Processed {0} samples".format(sample_count))

        progress_printer.epoch_summary(with_metric=True)

    return tl_model


# Evaluates a single image using the re-trained model
def eval_single_image(loaded_model, image_path, image_dims):
    # Load and format image (resize, RGB -> BGR, CHW -> HWC)
    try:
        img = Image.open(image_path)

        if image_path.endswith("png"):
            temp = Image.new("RGB", img.size, (255, 255, 255))
            temp.paste(img, img)
            img = temp
        resized = img.resize((image_dims[2], image_dims[1]), Image.ANTIALIAS)
        bgr_image = np.asarray(resized, dtype=np.float32)[..., [2, 1, 0]]
        hwc_format = np.ascontiguousarray(np.rollaxis(bgr_image, 2))

        # compute model output
        arguments = {loaded_model.arguments[0]: [hwc_format]}
        output = loaded_model.eval(arguments)

        # return softmax probabilities
        sm = cntk.softmax(output[0])

        return sm.eval()

    except FileNotFoundError:
        print("Could not open (skipping file): ", image_path)

        return ["None"]


# Evaluates an image set using the provided model
def eval_test_images(loaded_model, output_file, test_map_file, image_dims, max_images=-1, column_offset=0):
    num_images = sum(1 for _ in open(test_map_file))
    if max_images > 0:
        num_images = min(num_images, max_images)
    if isFast:
        # We will run through fewer images for test run
        num_images = min(num_images, 300)

    print("Evaluating model output node '{0}' for {1} images.".format("prediction", num_images))

    pred_count = 0
    correct_count = 0
    np.seterr(over="raise")
    with open(output_file, "wb") as results_file:
        with open(test_map_file, "r") as input_file:
            for line in input_file:
                tokens = line.rstrip().split("\t")
                img_file = tokens[0 + column_offset]
                probs = eval_single_image(loaded_model, img_file, image_dims)

                if probs[0] == "None":
                    print("Eval not possible: ", img_file)
                    continue

                pred_count += 1
                true_label = int(tokens[1 + column_offset])
                predicted_label = np.argmax(probs)
                if predicted_label == true_label:
                    correct_count += 1

                np.savetxt(results_file, probs[np.newaxis], fmt="%.3f")
                if pred_count % 100 == 0:
                    print("Processed {0} samples ({1:.2%} correct)".format(pred_count,
                                                                           (float(correct_count) / pred_count)))
                if pred_count >= num_images:
                    break

    print("{0} of {1} prediction were correct".format(correct_count, pred_count))

    if pred_count == 0:
        pred_count = 1

    return correct_count, pred_count, (float(correct_count) / pred_count)


def eval_single_image_imagenet(opt_model, loaded_model, image_path, image_dims):
    img = Image.open(image_path)

    if image_path.endswith("png"):
        temp = Image.new("RGB", img.size, (255, 255, 255))
        temp.paste(img, img)
        img = temp
    resized = img.resize((image_dims[2], image_dims[1]), Image.ANTIALIAS)
    bgr_image = np.asarray(resized, dtype=np.float32)[..., [2, 1, 0]]
    hwc_format = np.ascontiguousarray(np.rollaxis(bgr_image, 2))

    if "VGG" in opt_model:
        arguments = {loaded_model.arguments[0]: [hwc_format]}
        output = loaded_model.eval(arguments)
        sm = cntk.softmax(output[0])

        return sm.eval()

    elif "InceptionV3" in opt_model:
        z = cntk.as_composite(loaded_model[0].owner)
        output = z.eval({z.arguments[0]: [hwc_format]})

    else:
        z = cntk.as_composite(loaded_model[3].owner)
        output = z.eval({z.arguments[0]: [hwc_format]})

    predictions = np.squeeze(output)

    return predictions


def detect_objects(trained_model, set_model, min_conf, img_path):
    def get_output_layers(net):
        layer_names = net.getLayerNames()
        output_layers = [layer_names[output_node[0] - 1] for output_node in net.getUnconnectedOutLayers()]

        return output_layers

    def draw_rectangle(img, classes, colors, cls_id, conf, left, top, right, bottom):
        label = "%.2f" % conf
        if classes:
            assert cls_id < len(classes)
            label = "%s:%s" % (classes[cls_id], label)

        cv2.rectangle(img, (left, top), (right, bottom), colors[cls_id], 2)
        y_offset = top - 15 if top - 15 > 15 else top + 15
        cv2.putText(img, label, (left, y_offset), cv2.FONT_HERSHEY_SIMPLEX, 0.5, colors[cls_id], 2)

    image = cv2.imread(img_path)
    w_image = image.shape[1]
    h_image = image.shape[0]
    scale = 0.00392

    blob = cv2.dnn.blobFromImage(image, scale, (416, 416), (0, 0, 0), True, crop=False)

    trained_model.setInput(blob)

    outs = trained_model.forward(get_output_layers(trained_model))

    class_ids = []
    confidences = []
    boxes = []
    conf_threshold = 0.1
    nms_threshold = 0.4

    for out in outs:
        for detection in out:
            scores = detection[5:]
            class_id = np.argmax(scores)
            confidence = scores[class_id]
            if confidence >= float(min_conf):
                center_x = int(detection[0] * w_image)
                center_y = int(detection[1] * h_image)
                w = int(detection[2] * w_image)
                h = int(detection[3] * h_image)
                x = center_x - w / 2
                y = center_y - h / 2
                class_ids.append(class_id)
                confidences.append(float(confidence))
                boxes.append([x, y, w, h])

    indices = cv2.dnn.NMSBoxes(boxes, confidences, conf_threshold, nms_threshold)

    for i in indices:
        i = i[0]
        box = boxes[i]
        x = box[0]
        y = box[1]
        w = box[2]
        h = box[3]
        draw_rectangle(
            image,
            set_model["classes"],
            set_model["colors"],
            class_ids[i],
            confidences[i],
            round(x),
            round(y),
            round(x + w),
            round(y + h),
        )

    # Check if a display is available
    try:
        if os.environ["DISPLAY"]:
            if w_image > 416 or h_image > 416:
                image = cv2.resize(image, (416, 416))
            cv2.imshow("object detection", image)
            cv2.waitKey()

            cv2.imwrite("object-detection.jpg", image)
            cv2.destroyAllWindows()
        else:
            print("Command line version...")

    except Exception as e:
        print(e)
        print("Command line version...")

    return {"boxes": [(conf, c) for conf, c in zip(confidences, class_ids)]}


def force_training(base_model, set_model, set_data, max_training_epochs):
    # Print out all layers in the model
    print("Loading {} and printing all layers:".format(base_model["model_file"]))
    node_outputs = cntk.logging.get_node_outputs(cntk.load_model(base_model["model_file"]))
    for l in node_outputs:
        print("  {0} {1}".format(l.name, l.shape))

    learning_params = {
        "max_epochs": max_training_epochs,
        "mb_size": 50,
        "lr_per_mb": [0.2] * 10 + [0.1],
        "momentum_per_mb": 0.9,
        "l2_reg_weight": 0.0005,
        "freeze_weights": True,
    }

    print("Force Retraining or Model file NOT FOUND...")
    start_time = time.time()
    trained_model = train_model(base_model, set_model["num_classes"], set_data["full_map"], learning_params)
    trained_model.save(set_model["model_file"])
    print("Stored trained model at %s" % set_model["model_file"])

    # Evaluate the test set
    _, _, predict_accuracy = eval_test_images(
        trained_model,
        set_model["results_file"],
        set_data["testing_map"],
        base_model["image_dims"],
    )
    print("Done. Wrote output to %s" % set_model["results_file"])

    # Test: Accuracy on flower data
    print("Prediction accuracy: {0:.2%}".format(float(predict_accuracy)))

    delta_time = time.time() - start_time
    print("Delta Time: {0:.2f}".format(delta_time))


def setup_base_model(opt_model, model_filename):
    # define base model location and characteristics
    model_details = {
        "model_file": "",
        "feature_node_name": "features",
        "last_hidden_node_name": "z.x",
        "inception": "",
        "vgg": "",
        # Channel Depth x Height x Width
        "image_dims": (3, 224, 224),
    }

    print("Downloading pre-trained model...")
    model_details_file = download_model(model_filename=model_filename)
    print("Downloading pre-trained model complete!")

    model_details["model_file"] = model_details_file

    if opt_model == "AlexNet":
        model_details["image_dims"] = (3, 227, 227)
    elif opt_model == "InceptionV3":
        model_details["inception"] = 1
        model_details["image_dims"] = (3, 299, 299)
    elif "VGG" in opt_model:
        model_details["vgg"] = 1
        model_details["image_dims"] = (3, 224, 224)
    else:
        model_details["image_dims"] = (3, 224, 224)

    return model_details


def main():
    ensure_exists(output_path)
    np.random.seed(123)

    opt_setup = ""
    while opt_setup != "q":
        opt_setup = input("==> Setup CNTK CNN: (1=Test/2=Train/q=Quit)? ")
        if opt_setup == "1":
            opt_test = ""
            while opt_test != "q":
                try:
                    opt_test = str(input("==> Method;Model;Epochs;Image (r=Return): ")).split(";")

                    if len(opt_test) == 4:
                        opt_method, opt_model, opt_epochs, img_path = opt_test
                    elif opt_test == ["r"]:
                        break
                    else:
                        print("Please, provide 4 fields!")
                        continue

                    max_training_epochs = 10
                    if opt_epochs.isdigit():
                        max_training_epochs = int(opt_epochs)

                    if opt_method == "ImageNet":
                        set_model, model_details, map_names = setup_imagenet(opt_model)
                    elif opt_method == "detect":
                        set_model, model_details, map_names = setup_detect(opt_model)
                    elif opt_method == "flowers":
                        set_data, set_model, model_details, map_names = setup_flowers(max_training_epochs, opt_model)
                    elif opt_method == "dogs":
                        set_data, set_model, model_details, map_names = setup_dogs(max_training_epochs, opt_model)
                    else:
                        print("Invalid Set!")
                        continue

                    if os.path.exists(set_model["model_file"]):
                        print("Loading existing model from %s" % set_model["model_file"])
                        if opt_method == "detect":
                            trained_model = cv2.dnn.readNet(set_model["model_file"], set_model["model_cfg"])
                        else:
                            trained_model = cntk.load_model(set_model["model_file"])
                    else:
                        print("{} Exists?".format(set_model["model_file"]))
                        continue

                    if "http://" in img_path or "https://" in img_path:
                        header = {
                            'User-Agent': 'Mozilla/5.0 (Windows NT x.y; Win64; x64; rv:9.0) Gecko/20100101 Firefox/10.0'
                        }
                        r = requests.get(img_path, headers=header, allow_redirects=True)
                        with open("temp_img.jpg", "wb") as my_f:
                            my_f.write(r.content)
                            img_path = "temp_img.jpg"

                    start_time = time.time()
                    print("============================\nTest Results: ")
                    if opt_method == "ImageNet":
                        probs = eval_single_image_imagenet(opt_model,
                                                           trained_model,
                                                           img_path,
                                                           model_details["image_dims"])
                        p_array = probs.argsort()[-5:][::-1]
                        if len(p_array) > 1:
                            for i, prob in enumerate(p_array):
                                print("{0:05.2f}: {1}".format(probs[prob], map_names[prob]))
                        predicted_label = np.argmax(probs)
                        print("\nPredicted Label: " + str(map_names[predicted_label]))
                        delta_time = time.time() - start_time
                        print("Delta Time: {0:.2f}\n".format(delta_time))
                        if img_path == "temp_img.jpg":
                            os.remove(img_path)
                        continue

                    elif opt_method == "detect":
                        confidence = "0.5"
                        ret = detect_objects(trained_model, set_model, confidence, img_path)
                        boxes = ret["boxes"]
                        for (conf, class_id) in boxes:
                            print("{0:05.2f}%: {1}".format(float(conf) * 100, map_names[class_id]))
                        delta_time = time.time() - start_time
                        print("Delta Time: {0:.2f}\n".format(delta_time))

                        if img_path == "temp_img.jpg":
                            os.remove(img_path)
                        continue

                    probs = eval_single_image(trained_model, img_path, model_details["image_dims"])
                    p_array = probs.argsort()[-5:][::-1]
                    for i, prob in enumerate(p_array):
                        perc = probs[prob] * 100
                        print("{0:05.2f}: {1}".format(perc, map_names[prob]))
                    predicted_label = np.argmax(probs)
                    print("\nPredicted Label: " + str(map_names[predicted_label]))
                    delta_time = time.time() - start_time
                    print("Delta Time: {0:.2f}\n".format(delta_time))

                    if img_path == "temp_img.jpg":
                        os.remove(img_path)

                except Exception as e:
                    traceback.print_exc()
                    print("Error: " + str(e))
                    break

        elif opt_setup == "2":
            opt_train = ""
            while opt_train != "r":
                try:
                    opt_train = str(input("==> Method;Model;Epochs (r=Return): ")).split(";")

                    if len(opt_train) == 3:
                        opt_method, opt_model, opt_epochs = opt_train
                    elif opt_train == ["r"]:
                        break
                    else:
                        print("Please, provide 3 fields!")
                        continue

                    print()
                    max_training_epochs = 10
                    if opt_epochs.isdigit():
                        max_training_epochs = int(opt_epochs)

                    if opt_method == "flowers":
                        set_data, set_model, model_details, map_names = setup_flowers(max_training_epochs,
                                                                                      opt_model,
                                                                                      True)
                    elif opt_method == "dogs":
                        set_data, set_model, model_details, map_names = setup_dogs(max_training_epochs,
                                                                                   opt_model,
                                                                                   True)
                    else:
                        print("Invalid Set!")
                        continue

                    force_training(model_details, set_model, set_data, max_training_epochs)

                except Exception as e:
                    traceback.print_exc()
                    print("Error: " + str(e))
                    break

        else:
            print("Exit!")
            break


if __name__ == "__main__":
    main()
