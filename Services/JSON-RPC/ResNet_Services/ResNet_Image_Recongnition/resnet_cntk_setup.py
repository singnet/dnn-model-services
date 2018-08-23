from __future__ import print_function
import glob
import os
import numpy as np
from PIL import Image
# Some of the flowers data is stored as .mat files
from scipy.io import loadmat

import sys
import tarfile
import time
# import matplotlib.image as mpimg
import matplotlib.pyplot as plt

import cntk.io.transforms as xforms

# Loat the right urlretrieve based on python version
try:
    from urllib.request import urlretrieve
except ImportError:
    from urllib import urlretrieve

import zipfile

# Import CNTK and helpers
import cntk as C

from services import flowers_map_names, dogs_map_names, cars_map_names

isFast = True
# C.device.try_set_default_device(C.device.gpu(0))


# Check for an environment variable defined in CNTK's test infrastructure
def is_test(): return 'CNTK_EXTERNAL_TESTDATA_SOURCE_DIRECTORY' in os.environ


# Select the right target device when this notebook is being tested
# Currently supported only for GPU
# Setup data environment for pre-built data sources for testing
if is_test():
    if 'TEST_DEVICE' in os.environ:
        if os.environ['TEST_DEVICE'] == 'cpu':
            raise ValueError('This notebook is currently not support on CPU')
        else:
            C.device.try_set_default_device(C.device.gpu(0))
    sys.path.append(os.path.join(
        *"./Tests/EndToEndTests/CNTKv2Python/Examples".split("/")))
    import prepare_test_data as T
    T.prepare_resnet_v1_model()
    T.prepare_flower_data()
    T.prepare_animals_data()

# By default, we store data in the Examples/Image directory under CNTK
# If you're running this _outside_ of CNTK, consider changing this
data_root = os.path.join('.', 'Examples', 'Image')

datasets_path = os.path.join(data_root, 'DataSets')
output_path = os.path.join('.', 'Models')


def ensure_exists(path):
    if not os.path.exists(path):
        os.makedirs(path)


def write_to_file(file_path, img_paths, img_labels):
    with open(file_path, 'w+') as f:
        for i in range(0, len(img_paths)):
            f.write('%s\t%s\n' %
                    (os.path.abspath(img_paths[i]), img_labels[i]))


def download_unless_exists(url, filename, max_retries=3):
    '''Download the file unless it already exists, with retry. Throws if all retries fail.'''
    if os.path.exists(filename):
        print('Reusing locally cached: ', filename)
    else:
        print('Starting download of {} to {}'.format(url, filename))
        retry_cnt = 0
        while True:
            try:
                urlretrieve(url, filename)
                print('Download completed.')
                return
            except Exception as e:
                retry_cnt += 1
                if retry_cnt == max_retries:
                    print('Exceeded maximum retry count, aborting.')
                    raise
                print('Failed to download, retrying.')
                time.sleep(np.random.randint(1, 10))


def download_model(model_root=os.path.join(data_root, 'PretrainedModels'), model_filename='ResNet_18_ImageNet_CNTK.model'):
    ensure_exists(model_root)
    resnet_model_uri = 'https://www.cntk.ai/Models/CNTK_Pretrained/{}'.format(
        model_filename)
    resnet_model_local = os.path.join(model_root, model_filename)
    download_unless_exists(resnet_model_uri, resnet_model_local)
    return resnet_model_local


def download_flowers_dataset(dataset_root=os.path.join(datasets_path, 'Flowers')):
    ensure_exists(dataset_root)
    flowers_uris = [
        'http://www.robots.ox.ac.uk/~vgg/data/flowers/102/102flowers.tgz',
        'http://www.robots.ox.ac.uk/~vgg/data/flowers/102/imagelabels.mat',
        'http://www.robots.ox.ac.uk/~vgg/data/flowers/102/setid.mat'
    ]
    flowers_files = [
        os.path.join(dataset_root, '102flowers.tgz'),
        os.path.join(dataset_root, 'imagelabels.mat'),
        os.path.join(dataset_root, 'setid.mat')
    ]
    for uri, file in zip(flowers_uris, flowers_files):
        download_unless_exists(uri, file)
    tar_dir = os.path.join(dataset_root, 'extracted')
    if not os.path.exists(tar_dir):
        print('Extracting {} to {}'.format(flowers_files[0], tar_dir))
        os.makedirs(tar_dir)
        tarfile.open(flowers_files[0]).extractall(path=tar_dir)
    else:
        print('{} already extracted to {}, using existing version'.format(
            flowers_files[0], tar_dir))

    flowers_data = {
        'data_folder': dataset_root,
        'training_map': os.path.join(dataset_root, '6k_img_map.txt'),
        'testing_map': os.path.join(dataset_root, '1k_img_map.txt'),
        'validation_map': os.path.join(dataset_root, 'val_map.txt'),
        'full_map': os.path.join(dataset_root, 'full_map.txt')
    }

    if not os.path.exists(flowers_data['training_map']):
        print('Writing map files ...')
        # get image paths and 0-based image labels
        image_paths = np.array(
            sorted(glob.glob(os.path.join(tar_dir, 'jpg', '*.jpg'))))
        image_labels = loadmat(flowers_files[1])['labels'][0]
        image_labels -= 1

        # read set information from .mat file
        setid = loadmat(flowers_files[2])
        idx_train = setid['trnid'][0] - 1
        idx_test = setid['tstid'][0] - 1
        idx_val = setid['valid'][0] - 1

        # Confusingly the training set contains 1k images and the test set contains 6k images
        # We swap them, because we want to train on more data
        write_to_file(flowers_data['training_map'],
                      image_paths[idx_train], image_labels[idx_train])
        write_to_file(flowers_data['testing_map'],
                      image_paths[idx_test], image_labels[idx_test])
        write_to_file(flowers_data['validation_map'],
                      image_paths[idx_val], image_labels[idx_val])

        write_to_file(flowers_data['full_map'], image_paths, image_labels)

        print('Map files written, dataset download and unpack completed.')
    else:
        print('Using cached map files.')

    return flowers_data


def download_animals_dataset(dataset_root=os.path.join(datasets_path, 'Animals')):
    ensure_exists(dataset_root)
    animals_uri = 'https://www.cntk.ai/DataSets/Animals/Animals.zip'
    animals_file = os.path.join(dataset_root, 'Animals.zip')
    download_unless_exists(animals_uri, animals_file)
    if not os.path.exists(os.path.join(dataset_root, 'Test')):
        with zipfile.ZipFile(animals_file) as animals_zip:
            print('Extracting {} to {}'.format(animals_file, dataset_root))
            animals_zip.extractall(path=os.path.join(dataset_root, '..'))
            print('Extraction completed.')
    else:
        print('Reusing previously extracted Animals data.')

    return {
        'training_folder': os.path.join(dataset_root, 'Train'),
        'testing_folder': os.path.join(dataset_root, 'Test')
    }


print('Downloading flowers and animals data-set, this might take a while...')
flowers_data = download_flowers_dataset()
animals_data = download_animals_dataset()
print('All data now available to the notebook!')

model_filename = 'ResNet18_ImageNet_CNTK.model'
opt = input(
    '\n====> Model filename (Enter="ResNet18"): ')
if opt != '':
    model_filename = opt + '_ImageNet_CNTK.model'

print('Downloading pre-trained model. Note: this might take a while...')
base_model_file = download_model(model_filename=model_filename)
print('Downloading pre-trained model complete!')

# define base model location and characteristics
base_model = {
    'model_file': base_model_file,
    'feature_node_name': 'features',
    'last_hidden_node_name': 'z.x',
    # Channel Depth x Height x Width
    'image_dims': (3, 224, 224)
}

# Print out all layers in the model
print('Loading {} and printing all layers:'.format(base_model['model_file']))
node_outputs = C.logging.get_node_outputs(
    C.load_model(base_model['model_file']))
for l in node_outputs:
    print("  {0} {1}".format(l.name, l.shape))


def plot_images(images, subplot_shape):
    plt.style.use('ggplot')
    fig, axes = plt.subplots(*subplot_shape)
    for image, ax in zip(images, axes.flatten()):
        ax.imshow(image.reshape(28, 28), vmin=0, vmax=1.0, cmap='gray')
        ax.axis('off')
    plt.show()


flowers_image_dir = os.path.join(
    flowers_data['data_folder'], 'extracted', 'jpg')


# for image in ['06734']:
#     img = mpimg.imread(os.path.join(
#         flowers_image_dir, 'image_{}.jpg'.format(image)))
#     imgplot = plt.imshow(img)
#     plt.show()

ensure_exists(output_path)
np.random.seed(123)


# Creates a minibatch source for training or testing
def create_mb_source(map_file, image_dims, num_classes, randomize=True):
    transforms = [xforms.scale(width=image_dims[2], height=image_dims[1],
                               channels=image_dims[0], interpolations='linear')]
    return C.io.MinibatchSource(C.io.ImageDeserializer(map_file, C.io.StreamDefs(
        features=C.io.StreamDef(field='image', transforms=transforms),
        labels=C.io.StreamDef(field='label', shape=num_classes))),
        randomize=randomize)


# Creates the network model for transfer learning
def create_model(model_details, num_classes, input_features, new_prediction_node_name='prediction', freeze=False):
    # Load the pretrained classification net and find nodes
    base_model = C.load_model(model_details['model_file'])
    feature_node = C.logging.find_by_name(
        base_model, model_details['feature_node_name'])
    last_node = C.logging.find_by_name(
        base_model, model_details['last_hidden_node_name'])

    # Clone the desired layers with fixed weights
    cloned_layers = C.combine([last_node.owner]).clone(
        C.CloneMethod.freeze if freeze else C.CloneMethod.clone,
        {feature_node: C.placeholder(name='features')})

    # Add new dense layer for class prediction
    feat_norm = input_features - C.Constant(114)
    cloned_out = cloned_layers(feat_norm)
    z = C.layers.Dense(num_classes, activation=None,
                       name=new_prediction_node_name)(cloned_out)

    return z

# Trains a transfer learning model


def train_model_dogs(model_details, num_classes, train_map_file,
                     learning_params, max_images=-1):
    num_epochs = learning_params['max_epochs']
    epoch_size = sum(1 for line in open(train_map_file))
    if max_images > 0:
        epoch_size = min(epoch_size, max_images)
    minibatch_size = learning_params['mb_size']

    # Create the minibatch source and input variables
    minibatch_source = create_mb_source(
        train_map_file, model_details['image_dims'], num_classes)
    image_input = C.input_variable(model_details['image_dims'])
    label_input = C.input_variable(num_classes)

    # Define mapping from reader streams to network inputs
    input_map = {
        image_input: minibatch_source['features'],
        label_input: minibatch_source['labels']
    }

    # Instantiate the transfer learning model and loss function
    tl_model = create_model(model_details,
                            num_classes,
                            image_input,
                            freeze=learning_params['freeze_weights'])
    ce = C.cross_entropy_with_softmax(tl_model, label_input)
    pe = C.classification_error(tl_model, label_input)

    # Instantiate the trainer object
    lr_schedule = C.learning_parameter_schedule(learning_params['lr_per_mb'])
    mm_schedule = C.momentum_schedule(learning_params['momentum_per_mb'])
    learner = C.momentum_sgd(tl_model.parameters, lr_schedule, mm_schedule,
                             l2_regularization_weight=learning_params['l2_reg_weight'])
    trainer = C.Trainer(tl_model, (ce, pe), learner)

    # Get minibatches of images and perform model training
    print("Training transfer learning model for {0} epochs (epoch_size = {1}).".format(
        num_epochs, epoch_size))
    C.logging.log_number_of_parameters(tl_model)
    progress_printer = C.logging.ProgressPrinter(
        tag='Training', num_epochs=num_epochs)
    for epoch in range(num_epochs):       # loop over epochs
        sample_count = 0
        while sample_count < epoch_size:  # loop over minibatches in the epoch
            data = minibatch_source.next_minibatch(
                min(minibatch_size, epoch_size - sample_count),
                input_map=input_map)
            # update model with it
            trainer.train_minibatch(data)
            # count samples processed so far
            sample_count += trainer.previous_minibatch_sample_count
            progress_printer.update_with_trainer(
                trainer, with_metric=True)  # log progress
            if sample_count % (100 * minibatch_size) == 0:
                print("Processed {0} samples".format(sample_count))

        progress_printer.epoch_summary(with_metric=True)

    return tl_model


# Trains a transfer learning model
def train_model_flowers(model_details, num_classes, train_map_file,
                        learning_params, max_images=-1):
    num_epochs = learning_params['max_epochs']
    epoch_size = sum(1 for line in open(train_map_file))
    if max_images > 0:
        epoch_size = min(epoch_size, max_images)
    minibatch_size = learning_params['mb_size']

    # Create the minibatch source and input variables
    minibatch_source = create_mb_source(
        train_map_file, model_details['image_dims'], num_classes)
    image_input = C.input_variable(model_details['image_dims'])
    label_input = C.input_variable(num_classes)

    # Define mapping from reader streams to network inputs
    input_map = {
        image_input: minibatch_source['features'],
        label_input: minibatch_source['labels']
    }

    # Instantiate the transfer learning model and loss function
    tl_model = create_model(model_details,
                            num_classes,
                            image_input,
                            freeze=learning_params['freeze_weights'])
    ce = C.cross_entropy_with_softmax(tl_model, label_input)
    pe = C.classification_error(tl_model, label_input)

    # Instantiate the trainer object
    lr_schedule = C.learning_parameter_schedule(learning_params['lr_per_mb'])
    mm_schedule = C.momentum_schedule(learning_params['momentum_per_mb'])
    learner = C.momentum_sgd(tl_model.parameters, lr_schedule, mm_schedule,
                             l2_regularization_weight=learning_params['l2_reg_weight'])
    trainer = C.Trainer(tl_model, (ce, pe), learner)

    # Get minibatches of images and perform model training
    print("Training transfer learning model for {0} epochs (epoch_size = {1}).".format(
        num_epochs, epoch_size))
    C.logging.log_number_of_parameters(tl_model)
    progress_printer = C.logging.ProgressPrinter(
        tag='Training', num_epochs=num_epochs)
    for epoch in range(num_epochs):       # loop over epochs
        sample_count = 0
        while sample_count < epoch_size:  # loop over minibatches in the epoch
            data = minibatch_source.next_minibatch(
                min(minibatch_size, epoch_size - sample_count), input_map=input_map)
            # update model with it
            trainer.train_minibatch(data)
            # count samples processed so far
            sample_count += trainer.previous_minibatch_sample_count
            progress_printer.update_with_trainer(
                trainer, with_metric=True)  # log progress
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
        return ['None']


# Evaluates an image set using the provided model
def eval_test_images(loaded_model, output_file, test_map_file, image_dims, max_images=-1, column_offset=0):
    num_images = sum(1 for line in open(test_map_file))
    if max_images > 0:
        num_images = min(num_images, max_images)
    if isFast:
        # We will run through fewer images for test run
        num_images = min(num_images, 300)

    print("Evaluating model output node '{0}' for {1} images.".format(
        'prediction', num_images))

    pred_count = 0
    correct_count = 0
    np.seterr(over='raise')
    with open(output_file, 'wb') as results_file:
        with open(test_map_file, "r") as input_file:
            for line in input_file:
                tokens = line.rstrip().split('\t')
                img_file = tokens[0 + column_offset]
                probs = eval_single_image(loaded_model, img_file, image_dims)

                if probs[0] == 'None':
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
    print("{0} of {1} prediction were correct".format(
        correct_count, pred_count))
    return correct_count, pred_count, (float(correct_count) / pred_count)


force_retraining = True
opt = input("\n====> Force Retraining (default=y/n)? ")
if opt == 'n':
    force_retraining = False

max_training_epochs = 5 if isFast else 20
if force_retraining:
    opt = input("====> Number of Epochs: ")
    if opt.isdigit():
        max_training_epochs = int(opt)
print('\n\n')

learning_params = {
    'max_epochs': max_training_epochs,
    'mb_size': 50,
    'lr_per_mb': [0.2]*10 + [0.1],
    'momentum_per_mb': 0.9,
    'l2_reg_weight': 0.0005,
    'freeze_weights': True
}

map_names = {}

opt = input("====> Type (1=flowers|2=dogs|3=cars): ")

if opt.isdigit():
    if opt == '1':
        map_names = flowers_map_names

        flowers_model = {
            'model_file': os.path.join(output_path, 'flowers_{}.model'.format(
                model_filename.split('_')[0])),
            'results_file': os.path.join(output_path, 'flowers_{}_Predictions.txt'.format(
                model_filename.split('_')[0])),
            'num_classes': 102
        }
        # Train only if no model exists yet or if force_retraining is set to True
        if os.path.exists(flowers_model['model_file']) and not force_retraining:
            print("Loading existing model from %s" %
                  flowers_model['model_file'])
            trained_model = C.load_model(flowers_model['model_file'])
        else:
            print("Force Retraining or Model file NOT FOUND...")
            start_time = time.time()
            trained_model = train_model_flowers(base_model,
                                                flowers_model['num_classes'],
                                                flowers_data['full_map'],
                                                learning_params)
            trained_model.save(flowers_model['model_file'])
            print("Stored trained model at %s" % flowers_model['model_file'])
            # Evaluate the test set
            _, _, predict_accuracy = eval_test_images(trained_model,
                                                      flowers_model['results_file'],
                                                      flowers_data['testing_map'],
                                                      base_model['image_dims'])
            print("Done. Wrote output to %s" % flowers_model['results_file'])

            # Test: Accuracy on flower data
            print("Prediction accuracy: {0:.2%}".format(
                float(predict_accuracy)))

            delta_time = time.time() - start_time
            print('Delta Time: {0:.2f}'.format(delta_time))

    elif opt == '2':
        map_names = dogs_map_names

        dataset_root = os.path.join(datasets_path, 'Dogs')

        dogs_data = {
            'data_folder': dataset_root,
            'train_map': os.path.join(dataset_root, 'dogs_train.txt'),
            'test_map': os.path.join(dataset_root, 'dogs_test.txt'),
            'valid_map': os.path.join(dataset_root, 'dogs_valid.txt'),
        }

        dogs_model = {
            'model_file': os.path.join(output_path, 'dogs_{}.model'.format(
                model_filename.split('_')[0])),
            'results_file': os.path.join(output_path, 'dogs_{}_Predictions.txt'.format(
                model_filename.split('_')[0])),
            'num_classes': 133
        }
        # Train only if no model exists yet or if force_retraining is set to True
        if os.path.exists(dogs_model['model_file']) and not force_retraining:
            print("Loading existing model from %s" %
                  dogs_model['model_file'])
            trained_model = C.load_model(dogs_model['model_file'])
        else:
            print("Force Retraining or Model file NOT FOUND...")
            start_time = time.time()
            # Get the images if they dont exist
            download_unless_exists(
                'https://s3-us-west-1.amazonaws.com/udacity-aind/dog-project/dogImages.zip',
                'dogImages.zip')
            zip_dir = os.path.join(dataset_root)
            if not os.path.exists(zip_dir):
                print('Extracting {} to {}'.format('dogImages.zip', zip_dir))
                os.makedirs(zip_dir)
                zip_ref = zipfile.ZipFile('dogImages.zip', 'r')
                zip_ref.extractall(zip_dir)
                zip_ref.close()
            else:
                print('{} already extracted to {}, using existing version'.format(
                    'dogImages.zip', zip_dir))

            # Creating the .maps files
            allfiles = glob.glob(
                os.getcwd() + "/Examples/Image/DataSets/Dogs/dogImages/train/*/*")
            with open(dogs_data['train_map'], 'w+') as my_f:
                for file in allfiles:
                    num_breed = file.split('/')[-2]
                    num_breed = int(num_breed.split('.')[0])-1
                    my_f.write(file + '\t' + str(num_breed) + '\n')
            allfiles = glob.glob(
                os.getcwd() + "/Examples/Image/DataSets/Dogs/dogImages/test/*/*")
            with open(dogs_data['test_map'], 'w+') as my_f:
                for file in allfiles:
                    num_breed = file.split('/')[-2]
                    num_breed = int(num_breed.split('.')[0])-1
                    my_f.write(file + '\t' + str(num_breed) + '\n')
            allfiles = glob.glob(
                os.getcwd() + "/Examples/Image/DataSets/Dogs/dogImages/valid/*/*")
            with open(dogs_data['valid_map'], 'w+') as my_f:
                for file in allfiles:
                    num_breed = file.split('/')[-2]
                    num_breed = int(num_breed.split('.')[0])-1
                    my_f.write(file + '\t' + str(num_breed) + '\n')

            # Train the model with the train map file
            trained_model = train_model_dogs(base_model,
                                             dogs_model['num_classes'],
                                             dogs_data['train_map'],
                                             learning_params)
            trained_model.save(dogs_model['model_file'])
            print("Stored trained model at %s" % dogs_model['model_file'])
            # Evaluate the test set
            _, _, predict_accuracy = eval_test_images(trained_model,
                                                      dogs_model['results_file'],
                                                      dogs_data['test_map'],
                                                      base_model['image_dims'])
            print("Done. Wrote output to %s" % dogs_model['results_file'])

            # Test: Accuracy on flower data
            print("Prediction accuracy: {0:.2%}".format(
                float(predict_accuracy)))

            delta_time = time.time() - start_time
            print('Delta Time: {0:.2f}'.format(delta_time))

    elif opt == '3':
        map_names = cars_map_names

        dataset_root = os.path.join(datasets_path, 'Cars')

        cars_data = {
            'data_folder': dataset_root,
            'train_map': os.path.join(dataset_root, 'cars_train.txt'),
            'test_map': os.path.join(dataset_root, 'cars_test.txt'),
            'valid_map': os.path.join(dataset_root, 'cars_valid.txt'),
        }

        cars_model = {
            'model_file': os.path.join(output_path, 'cars_{}.model'.format(
                model_filename.split('_')[0])),
            'results_file': os.path.join(output_path, 'cars_{}_Predictions.txt'.format(
                model_filename.split('_')[0])),
            'num_classes': 133
        }
        # Train only if no model exists yet or if force_retraining is set to True
        if os.path.exists(cars_model['model_file']) and not force_retraining:
            print("Loading existing model from %s" %
                  cars_model['model_file'])
            trained_model = C.load_model(cars_model['model_file'])
        else:
            print("Force Retraining or Model file NOT FOUND...")
            start_time = time.time()
            # Get the images if they dont exist
            download_unless_exists(
                'https://s3-us-west-1.amazonaws.com/udacity-aind/dog-project/carImages.zip',
                'carImages.zip')
            zip_dir = os.path.join(dataset_root)
            if not os.path.exists(zip_dir):
                print('Extracting {} to {}'.format(
                    'carImages.zip', zip_dir))
                os.makedirs(zip_dir)
                zip_ref = zipfile.ZipFile('carImages.zip', 'r')
                zip_ref.extractall(zip_dir)
                zip_ref.close()
            else:
                print('{} already extracted to {}, using existing version'.format(
                    'carImages.zip', zip_dir))

            # Creating the .maps files
            allfiles = glob.glob(
                os.getcwd() + "/Examples/Image/DataSets/Cars/train/*/*")
            with open(cars_data['train_map'], 'w+') as my_f:
                for file in allfiles:
                    num_breed = file.split('/')[-2]
                    num_breed = int(num_breed.split('.')[0])-1
                    my_f.write(file + '\t' + str(num_breed) + '\n')
            allfiles = glob.glob(
                os.getcwd() + "/Examples/Image/DataSets/Cars/test/*/*")
            with open(cars_data['test_map'], 'w+') as my_f:
                for file in allfiles:
                    num_breed = file.split('/')[-2]
                    num_breed = int(num_breed.split('.')[0])-1
                    my_f.write(file + '\t' + str(num_breed) + '\n')
            allfiles = glob.glob(
                os.getcwd() + "/Examples/Image/DataSets/Cars/valid/*/*")
            with open(cars_data['valid_map'], 'w+') as my_f:
                for file in allfiles:
                    num_breed = file.split('/')[-2]
                    num_breed = int(num_breed.split('.')[0])-1
                    my_f.write(file + '\t' + str(num_breed) + '\n')

            # Train the model with the train map file
            trained_model = train_model_dogs(base_model,
                                             cars_model['num_classes'],
                                             cars_data['train_map'],
                                             learning_params)
            trained_model.save(cars_model['model_file'])
            print("Stored trained model at %s" % cars_model['model_file'])
            # Evaluate the test set
            _, _, predict_accuracy = eval_test_images(trained_model,
                                                      cars_model['results_file'],
                                                      cars_data['test_map'],
                                                      base_model['image_dims'])
            print("Done. Wrote output to %s" % cars_model['results_file'])

            # Test: Accuracy on flower data
            print("Prediction accuracy: {0:.2%}".format(
                float(predict_accuracy)))

            delta_time = time.time() - start_time
            print('Delta Time: {0:.2f}'.format(delta_time))

    else:
        print('Invalid option!')
        exit(0)

else:
    print('Invalid option!')
    exit(0)

img_path = input("\n====> Image path (q=Quit): ")
while img_path != 'q':
    try:
        start_time = time.time()
        probs = eval_single_image(trained_model, img_path,
                                  base_model['image_dims'])
        p_array = probs.argsort()[-5:][::-1]
        for i, prob in enumerate(p_array):
            perc = probs[prob]*100
            print('{0}: {1:05.2f}'.format(map_names[prob], perc))
        predicted_label = np.argmax(probs)
        print('\nPredicted Label: ' + str(map_names[predicted_label]))
        delta_time = time.time() - start_time
        print('Delta Time: {0:.2f}'.format(delta_time))
        img_path = input("\n====> Image path (q=Quit): ")
    except Exception as e:
        print('Error! ' + str(e))
