from __future__ import print_function
import glob
import os
import numpy as np
from PIL import Image

# Some of the flowers data is stored as .mat files
from scipy.io import loadmat

import tarfile
import time

import cntk.io.transforms as xforms

# Loat the right urlretrieve based on python version
try:
    from urllib.request import urlretrieve
except ImportError:
    from urllib import urlretrieve

import zipfile
import requests

# Import CNTK and helpers
import cntk as C

from registry import flowers_map_names, dogs_map_names, cars_map_names

isFast = True
# C.device.try_set_default_device(C.device.gpu(0))


# By default, we store data in the Examples/Image directory under CNTK
# If you're running this _outside_ of CNTK, consider changing this
data_root = os.path.join(".", "Resources", "Examples", "Image")
datasets_path = os.path.join(data_root, "DataSets")
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
                retry_cnt += 1
                if retry_cnt == max_retries:
                    print("Exceeded maximum retry count, aborting.")
                    raise
                print("Failed to download, retrying.")
                time.sleep(np.random.randint(1, 10))


def download_model(
    model_root=os.path.join(data_root, "PretrainedModels"),
    model_filename="ResNet_18_ImageNet_CNTK.model",
):
    ensure_exists(model_root)
    resnet_model_uri = "https://www.cntk.ai/Models/CNTK_Pretrained/{}".format(
        model_filename
    )
    if "VGG" in model_filename:
        resnet_model_uri = "https://www.cntk.ai/Models/Caffe_Converted/{}".format(
            model_filename
        )
    resnet_model_local = os.path.join(model_root, model_filename)
    download_unless_exists(resnet_model_uri, resnet_model_local)
    return resnet_model_local


def download_flowers_dataset(dataset_root=os.path.join(datasets_path, "Flowers")):
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
        print(
            "{} already extracted to {}, using existing version".format(
                flowers_files[0], tar_dir
            )
        )

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
        write_to_file(
            flowers_data["training_map"],
            image_paths[idx_train],
            image_labels[idx_train],
        )
        write_to_file(
            flowers_data["testing_map"], image_paths[idx_test], image_labels[idx_test]
        )
        write_to_file(
            flowers_data["validation_map"], image_paths[idx_val], image_labels[idx_val]
        )

        write_to_file(flowers_data["full_map"], image_paths, image_labels)

        print("Map files written, dataset download and unpack completed.")
    else:
        print("Using cached map files.")

    return flowers_data


def download_animals_dataset(dataset_root=os.path.join(datasets_path, "Animals")):
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


def setup_flowers(num_epochs):
    set_model = {
        "model_file": os.path.join(
            output_path, "flowers_{}_{}.model".format(opt_model, num_epochs)
        ),
        "results_file": os.path.join(
            output_path, "flowers_{}_Predic.txt".format(opt_model, num_epochs)
        ),
        "num_classes": 102,
    }

    print("Downloading flowers and animals data-set...")
    set_data = download_flowers_dataset()
    # animals_data = download_animals_dataset()
    print("All flowers data now available!")

    return set_data, set_model, flowers_map_names


def setup_dogs(num_epochs):
    dataset_root = os.path.join(datasets_path, "Dogs")

    set_data = {
        "data_folder": dataset_root,
        "training_map": os.path.join(dataset_root, "dogs_train.txt"),
        "testing_map": os.path.join(dataset_root, "dogs_test.txt"),
        "validation_map": os.path.join(dataset_root, "dogs_valid.txt"),
        "full_map": os.path.join(dataset_root, "dogs_train.txt"),
    }

    set_model = {
        "model_file": os.path.join(
            output_path, "dogs_{}_{}.model".format(opt_model, num_epochs)
        ),
        "results_file": os.path.join(
            output_path, "dogs_{}_{}_Predic.txt".format(opt_model, num_epochs)
        ),
        "num_classes": 133,
    }
    # Get the images if they dont exist
    zip_dir = os.path.join(dataset_root)
    download_unless_exists(
        "https://s3-us-west-1.amazonaws.com/udacity-aind/dog-project/dogImages.zip",
        zip_dir + "/dogImages.zip",
    )

    if not os.path.exists(zip_dir):
        print("Extracting {} to {}".format("dogImages.zip", zip_dir))
        os.makedirs(zip_dir)
        zip_ref = zipfile.ZipFile("dogImages.zip", "r")
        zip_ref.extractall(zip_dir)
        zip_ref.close()
    else:
        print(
            "{} already extracted to {}, using existing version".format(
                "dogImages.zip", zip_dir
            )
        )

    # Creating the .maps files
    allfiles = glob.glob(
        os.getcwd() + "/Resources/Examples/Image/DataSets/Dogs/dogImages/train/*/*"
    )
    with open(set_data["full_map"], "w+") as my_f:
        for file in allfiles:
            num_breed = file.split("/")[-2]
            num_breed = int(num_breed.split(".")[0]) - 1
            my_f.write(file + "\t" + str(num_breed) + "\n")
    allfiles = glob.glob(
        os.getcwd() + "/Resources/Examples/Image/DataSets/Dogs/dogImages/test/*/*"
    )
    with open(set_data["testing_map"], "w+") as my_f:
        for file in allfiles:
            num_breed = file.split("/")[-2]
            num_breed = int(num_breed.split(".")[0]) - 1
            my_f.write(file + "\t" + str(num_breed) + "\n")
    allfiles = glob.glob(
        os.getcwd() + "/Resources/Examples/Image/DataSets/Dogs/dogImages/valid/*/*"
    )
    with open(set_data["validation_map"], "w+") as my_f:
        for file in allfiles:
            num_breed = file.split("/")[-2]
            num_breed = int(num_breed.split(".")[0]) - 1
            my_f.write(file + "\t" + str(num_breed) + "\n")

    return set_data, set_model, dogs_map_names


# Creates a minibatch source for training or testing
def create_mb_source(map_file, image_dims, num_classes, randomize=True):
    transforms = [
        xforms.scale(
            width=image_dims[2],
            height=image_dims[1],
            channels=image_dims[0],
            interpolations="linear",
        )
    ]
    return C.io.MinibatchSource(
        C.io.ImageDeserializer(
            map_file,
            C.io.StreamDefs(
                features=C.io.StreamDef(field="image", transforms=transforms),
                labels=C.io.StreamDef(field="label", shape=num_classes),
            ),
        ),
        randomize=randomize,
    )


# Creates the network model for transfer learning
def create_model(
    model_details,
    num_classes,
    input_features,
    new_prediction_node_name="prediction",
    freeze=False,
):
    # Load the pretrained classification net and find nodes
    base_model = C.load_model(model_details["model_file"])
    feature_node = C.logging.find_by_name(
        base_model, model_details["feature_node_name"]
    )

    if model_details["inception"]:
        node_outputs = C.logging.get_node_outputs(base_model)
        last_node = node_outputs[5]
        feature_node = C.logging.find_all_with_name(base_model, "")[-5]
    if model_details["vgg"]:
        last_node = C.logging.find_by_name(base_model, "prob")
        feature_node = C.logging.find_by_name(base_model, "data")
    else:
        last_node = C.logging.find_by_name(
            base_model, model_details["last_hidden_node_name"]
        )

    # Clone the desired layers with fixed weights
    cloned_layers = C.combine([last_node.owner]).clone(
        C.CloneMethod.freeze if freeze else C.CloneMethod.clone,
        {feature_node: C.placeholder(name="features")},
    )

    # Add new dense layer for class prediction
    feat_norm = input_features - C.Constant(114)
    cloned_out = cloned_layers(feat_norm)
    z = C.layers.Dense(num_classes, activation=None, name=new_prediction_node_name)(
        cloned_out
    )

    return z


# Trains a transfer learning model
def train_model(
    model_details, num_classes, train_map_file, learning_params, max_images=-1
):
    num_epochs = learning_params["max_epochs"]
    epoch_size = sum(1 for line in open(train_map_file))
    if max_images > 0:
        epoch_size = min(epoch_size, max_images)
    minibatch_size = learning_params["mb_size"]

    # Create the minibatch source and input variables
    minibatch_source = create_mb_source(
        train_map_file, model_details["image_dims"], num_classes
    )
    image_input = C.input_variable(model_details["image_dims"])
    label_input = C.input_variable(num_classes)

    # Define mapping from reader streams to network inputs
    input_map = {
        image_input: minibatch_source["features"],
        label_input: minibatch_source["labels"],
    }

    # Instantiate the transfer learning model and loss function
    tl_model = create_model(
        model_details,
        num_classes,
        image_input,
        freeze=learning_params["freeze_weights"],
    )
    ce = C.cross_entropy_with_softmax(tl_model, label_input)
    pe = C.classification_error(tl_model, label_input)

    # Instantiate the trainer object
    lr_schedule = C.learning_parameter_schedule(learning_params["lr_per_mb"])
    mm_schedule = C.momentum_schedule(learning_params["momentum_per_mb"])
    learner = C.momentum_sgd(
        tl_model.parameters,
        lr_schedule,
        mm_schedule,
        l2_regularization_weight=learning_params["l2_reg_weight"],
    )
    trainer = C.Trainer(tl_model, (ce, pe), learner)

    # Get minibatches of images and perform model training
    print(
        "Training transfer learning model for {0} epochs (epoch_size = {1}).".format(
            num_epochs, epoch_size
        )
    )
    C.logging.log_number_of_parameters(tl_model)
    progress_printer = C.logging.ProgressPrinter(tag="Training", num_epochs=num_epochs)

    for epoch in range(num_epochs):  # loop over epochs
        sample_count = 0
        while sample_count < epoch_size:  # loop over minibatches in the epoch
            data = minibatch_source.next_minibatch(
                min(minibatch_size, epoch_size - sample_count), input_map=input_map
            )

            # update model with it
            trainer.train_minibatch(data)

            # count samples processed so far
            sample_count += trainer.previous_minibatch_sample_count
            progress_printer.update_with_trainer(trainer, with_metric=True)

            if sample_count % (100 * minibatch_size) == 0:
                print("Processed {0} samples".format(sample_count))

        progress_printer.epoch_summary(with_metric=True)

    return tl_model


# Evaluates a single image using the re-trained model
def eval_single_image(loaded_model, image_path, image_dims):
    # load and format image (resize, RGB -> BGR, CHW -> HWC)
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
        sm = C.softmax(output[0])
        return sm.eval()
    except FileNotFoundError:
        print("Could not open (skipping file): ", image_path)
        return ["None"]


# Evaluates an image set using the provided model
def eval_test_images(
    loaded_model, output_file, test_map_file, image_dims, max_images=-1, column_offset=0
):
    num_images = sum(1 for line in open(test_map_file))
    if max_images > 0:
        num_images = min(num_images, max_images)
    if isFast:
        # We will run through fewer images for test run
        num_images = min(num_images, 300)

    print(
        "Evaluating model output node '{0}' for {1} images.".format(
            "prediction", num_images
        )
    )

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
                    print(
                        "Processed {0} samples ({1:.2%} correct)".format(
                            pred_count, (float(correct_count) / pred_count)
                        )
                    )
                if pred_count >= num_images:
                    break
    print("{0} of {1} prediction were correct".format(correct_count, pred_count))
    return correct_count, pred_count, (float(correct_count) / pred_count)


def force_train(base_model, set_model, set_data, max_training_epochs):
    # Print out all layers in the model
    print("Loading {} and printing all layers:".format(base_model["model_file"]))
    node_outputs = C.logging.get_node_outputs(C.load_model(base_model["model_file"]))
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
    trained_model = train_model(
        base_model, set_model["num_classes"], set_data["full_map"], learning_params
    )
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


ensure_exists(output_path)
np.random.seed(123)


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


opt_setup = ""
while opt_setup != "q":
    opt_setup = input("==> Setup CNTK CNN: (1=Test/2=Train/q=Quit)? ")
    if opt_setup == "1":
        opt_test = ""
        while opt_test != "q":
            try:
                opt_test = str(input("==> Set;Model;Epochs;Image (r=Return): ")).split(
                    ";"
                )

                opt_set, opt_model, opt_epochs, img_path = ["", "", "", ""]
                if len(opt_test) == 4:
                    opt_set, opt_model, opt_epochs, img_path = opt_test
                elif opt_test == ["r"]:
                    break
                else:
                    print("Please, provide 4 fields!")
                    continue

                print()
                max_training_epochs = 10
                if opt_epochs.isdigit():
                    max_training_epochs = int(opt_epochs)

                map_names = set_data = set_model = {}
                if opt_set == "flowers":
                    set_data, set_model, map_names = setup_flowers(max_training_epochs)
                elif opt_set == "dogs":
                    set_data, set_model, map_names = setup_dogs(max_training_epochs)
                else:
                    print("Invalid Set!")
                    continue

                if opt_model != "":
                    if "VGG" in opt_model:
                        model_filename = opt_model + "_ImageNet_Caffe.model"
                    else:
                        model_filename = opt_model + "_ImageNet_CNTK.model"
                else:
                    opt_model = "ResNet18"
                    model_filename = opt_model + "_ImageNet_CNTK.model"

                model_details = setup_base_model(opt_model, model_filename)

                if os.path.exists(set_model["model_file"]):
                    print("Loading existing model from %s" % set_model["model_file"])
                    trained_model = C.load_model(set_model["model_file"])
                else:
                    print("{} Exists?".format(set_model["model_file"]))
                    continue

                if "http://" in img_path or "https://" in img_path:
                    r = requests.get(img_path, allow_redirects=True)
                    with open("temp_img.jpg", "wb") as my_f:
                        my_f.write(r.content)
                        img_path = "temp_img.jpg"

                start_time = time.time()
                print("============================\nTest Results: ")
                probs = eval_single_image(
                    trained_model, img_path, model_details["image_dims"]
                )
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
                print("Error! " + str(e))
                break
    elif opt_setup == "2":
        opt_train = ""
        while opt_train != "r":
            opt_train = str(input("==> Set;Model;Epochs (r=Return): ")).split(";")

            opt_set, opt_model, opt_epochs = ["", "", ""]
            if len(opt_train) == 3:
                opt_set, opt_model, opt_epochs = opt_train
            elif opt_train == ["r"]:
                break
            else:
                print("Please, provide 3 fields!")
                continue

            print()
            max_training_epochs = 10
            if opt_epochs.isdigit():
                max_training_epochs = int(opt_epochs)

            map_names = set_data = set_model = {}
            if opt_set == "flowers":
                set_data, set_model, map_names = setup_flowers(max_training_epochs)
            elif opt_set == "dogs":
                set_data, set_model, map_names = setup_dogs(max_training_epochs)
            else:
                print("Invalid Set!")
                continue

            if opt_model != "":
                if "VGG" in opt_model:
                    model_filename = opt_model + "_ImageNet_Caffe.model"
                else:
                    model_filename = opt_model + "_ImageNet_CNTK.model"
            else:
                opt_model = "ResNet18"
                model_filename = opt_model + "_ImageNet_CNTK.model"

            model_details = setup_base_model(opt_model, model_filename)

            force_train(model_details, set_model, set_data, max_training_epochs)

    else:
        print("Exit!")
        break
