import logging
import os
import urllib.request
from urllib.parse import urlparse
import base64
import io
from PIL import Image
import time
import re
import argparse
from service import registry

logging.basicConfig(
    level=10, format="%(asctime)s - [%(levelname)8s] - %(name)s - %(message)s")
log = logging.getLogger(os.path.basename(__file__))


def common_parser(script_name):
    parser = argparse.ArgumentParser(prog=script_name)
    service_name = os.path.splitext(os.path.basename(script_name))[0]
    parser.add_argument("--grpc-port",
                        help="port to bind gRPC service to",
                        default=registry[service_name]["grpc"],
                        type=int,
                        required=False)
    return parser


def main_loop(grpc_handler, args):
    """From gRPC docs:
    Because start() does not block you may need to sleep-loop if there is nothing
    else for your code to do while serving."""
    server = grpc_handler(port=args.grpc_port)
    server.start()
    try:
        while True:
            time.sleep(0.1)
    except KeyboardInterrupt:
        server.stop(0)


def download(url, filename):
    """Downloads a file given its url and saves to filename."""

    # Adds header to deal with images under https
    opener = urllib.request.build_opener()
    opener.addheaders = [('User-agent', 'Mozilla/5.0 (Windows NT x.y; Win64; x64; rv:9.0) Gecko/20100101 Firefox/10.0')]
    urllib.request.install_opener(opener)

    # Downloads the image
    try:
        urllib.request.urlretrieve(url, filename)
    except Exception:
        raise
    return


def jpg_to_base64(jpgimg, open_file=False):
    """Encodes a jpg file into base64. Can receive either the already open jpg PIL Image or its path as input."""

    if open_file:
        try:
            jpgimg = Image.open(jpgimg)
        except Exception as e:
            log.error(e)
            raise
    imgbuffer = io.BytesIO()
    try:
        jpgimg.save(imgbuffer, format='JPEG')
    except Exception as e:
        log.error(e)
        raise
    imgbytes = imgbuffer.getvalue()
    return base64.b64encode(imgbytes)


def base64_to_jpg(base64img, output_file_path=""):
    """Decodes from base64 to jpg. If output_file_path is defined, saves the decoded image."""

    decoded_jpg = base64.b64decode(base64img)
    jpg_bytes = io.BytesIO(decoded_jpg)
    image = Image.open(jpg_bytes)
    if output_file_path != "":
        # If image is PNG, convert to JPG
        if image.format == 'PNG':
            image = image.convert('RGB')
        image.save(output_file_path, format='JPEG')
    return decoded_jpg


def clear_path(path):
    """ Deletes all files in a path. """

    for file in os.listdir(path):
        file_path = os.path.join(path, file)
        try:
            if os.path.isfile(file_path):
                os.unlink(file_path)
        except Exception as e:
            print(e)
    return


def clear_file(file_path):
    """ Deletes a file given its path."""

    try:
        if os.path.isfile(file_path):
            os.unlink(file_path)
    except Exception as e:
        print(e)
    return


def initialize_diretories(directories_list, clear_directories=True):
    """ Creates directories (or clears them if necesary)."""

    for directory in directories_list:
        if not os.path.exists(directory):
            os.makedirs(directory)
        else:
            if clear_directories:
                clear_path(directory)


def get_file_index(save_dir, prefix):
    """ Gets number "x" of images of this type in the directory (so that the save path will be "prefix_x".
    Requires files named as follows: "*_xx.ext", e.g.: "contentimage_03.jpg", from which 03 would be extracted to return
    04 as the index of the next file to be saved. This number resets to 0 at 99."""

    file_index = 0
    regex = prefix + r'([0-9]{2})\.([a-z]{3})'
    files = [f for f in os.listdir(save_dir) if os.path.isfile(os.path.join(save_dir, f))]
    if files:
        for file_name in files:
            regmatch = re.match(regex, file_name)
            if regmatch is not None:
                int_index = int(regmatch.group(1))
                if int_index >= file_index:
                    file_index = int_index + 1
                    # Circular list (up to 99) for files of each type.
                    if file_index > 99:
                        file_index = 0
    file_index_str = str(file_index).zfill(2)
    return file_index_str


def png_to_jpg(png_path, delete_original=True):
    """Opens a png image, creates a jpg image of the same name and optionally deletes the original png image.
    Returns: path to the jpg image."""
    with Image.open(png_path) as png_img:
        jpg_img = png_img.convert('RGB')
        stripped_file_name = os.path.splitext(png_path)[0]
        jpg_path = stripped_file_name + ".jpg"
        jpg_img.save(jpg_path)
    if delete_original:
        clear_file(png_path)
    return jpg_path


def treat_image_input(input_argument, save_dir, image_type):
    """ Gets image save path, downloads links or saves local images to temporary folder, deals with base64 inputs."""

    # Gets index (numerical suffix) to save the image (so it multiple calls are allowed)
    file_index_str = get_file_index(save_dir, image_type + "_")

    # Assemble save path (still lacks extension)
    save_path = save_dir + '/' + image_type + "_" + file_index_str

    # If its a link, download
    if urlparse(input_argument).scheme in ('http', 'https'):
        log.debug("Treating image input as a url.")
        path = urlparse(input_argument).path
        file_ext = os.path.splitext(path)[1].lower()
        if file_ext not in ['.jpg', '.jpeg', '.png']:
            log.error('URL image extension not recognized. Should be .jpg, .jpeg or .png. '
                      'Got {}. Trying to treat image as .jpg.'.format(file_ext))
            save_path += ".jpg"
        else:
            save_path += file_ext
        log.debug("Downloading image under the path: {}".format(save_path))
        try:
            download(input_argument, save_path)
            if file_ext == ".png":
                save_path = png_to_jpg(save_path, True)
            Image.open(save_path)
        except Exception:
            clear_file(save_path)
            raise

    # If its a local file
    elif os.path.isfile(input_argument):
        log.debug("Treating image input as a path to a local file.")
        try:
            image = Image.open(input_argument)
        except Exception:
            log.exception('Could not open image in treat_image_input')
            raise

        # Gets file extension
        if image.format == 'PNG':
            file_ext = ".png"
        elif image.format == 'JPEG' or image.format == 'JPG':
            file_ext = '.jpg'
        else:
            log.error("Input file extension not recognized!")
            return False
        save_path += file_ext

        # Save image to temp file
        image.save(save_path)

    # If it's not a local file, try to decode from base64 to jpg and save
    else:
        # TODO : check if always decoding base64 to JPG works.
        log.debug("Treating image input as base64.")
        # Extracting header if present
        if input_argument[0:4] == "data":
            file_ext = '.' + input_argument.split('/')[1].split(';')[0].lower()
            input_argument = input_argument.split(',')[1]
        else:
            file_ext = '.jpg'
        save_path += file_ext
        base64_to_jpg(input_argument, save_path)

    return save_path, file_index_str
