# For service integration
import logging
import grpc
import json
import service.serviceUtils
import service.service_spec.scene_recognition_pb2_grpc as grpc_bt_grpc
from service.service_spec.scene_recognition_pb2 import SceneRecognitionResult
import concurrent.futures as futures
import sys
import os
from urllib.error import HTTPError
from service.scene_recognition import SceneRecognitionModel

logging.basicConfig(
    level=10, format="%(asctime)s - [%(levelname)8s] - %(name)s - %(message)s"
)
log = logging.getLogger("scene_recognition_service")


class SceneRecognitionServicer(grpc_bt_grpc.SceneRecognitionServicer):
    """Scene recognition servicer class to be added to the gRPC stub.
    Derived from protobuf (auto-generated) class."""

    def __init__(self):
        log.debug("SceneRecognitionServicer created!")

        self.result = SceneRecognitionResult()

        self.input_dir = "./service/temp/input"
        self.output_dir = "./service/temp/output"
        service.serviceUtils.initialize_diretories([self.input_dir, self.output_dir])

        self.sr_model = SceneRecognitionModel()

        self.prediction_list = ["io", "categories", "attributes", "cam"]

    def treat_inputs(self, request, arguments, created_images):
        """Treats gRPC inputs and assembles lua command. Specifically, checks if required field have been specified,
        if the values and types are correct and, for each input/input_type adds the argument to the lua command."""

        file_index_str = ""
        image_path = ""
        predict = []

        for field, values in arguments.items():
            # var_type = values[0]
            # required = values[1] Not being used now but required for future automation steps
            default = values[2]

            # Tries to retrieve argument from gRPC request
            try:
                arg_value = eval("request.{}".format(field))
            except Exception as e:  # AttributeError if trying to access a field that hasn't been specified.
                log.error(e)
                return False

            log.debug("Received request.{} = {}".format(field, arg_value))

            # Deals with each field (or field type) separately. This is very specific to the lua command required.
            if field == "input_image":
                assert (request.input_image != ""), "Input image field should not be empty."
                try:
                    image_path, file_index_str = \
                        service.serviceUtils.treat_image_input(arg_value, self.input_dir, "{}".format(field))
                    log.debug("Field: {}. Image path: {}".format(field, image_path))
                    created_images.append(image_path)
                except Exception as e:
                    log.error(e)
                    raise
            elif field == "predict":
                predict = [word.strip() for word in request.predict.lower().split(',')]
                if predict == [""]:
                    predict = default
                else:
                    for word in predict:
                        assert word in self.prediction_list
            else:
                log.error("Error. Required request field not found.")
                return False

        return image_path, predict, file_index_str

    def recognize_scene(self, request, context):
        """Wraps the scene recognition model to make sure inputs and outputs match the service requirements."""

        # Store the names of the images to delete them afterwards
        created_images = []

        # Python command call arguments. Key = argument name, value = tuple(type, required?, default_value)
        arguments = {"input_image": ("image", True, None),
                     "predict": ("string", True, self.prediction_list)}

        # Treat inputs
        try:
            image_path, predict, file_index_str = self.treat_inputs(request, arguments, created_images)
        except HTTPError as e:
            error_message = "Error downloading the input image \n" + e.read()
            log.error(error_message)
            self.result.data = error_message
            return self.result
        except Exception as e:
            log.error(e)
            self.result.data = e
            return self.result

        # Get cam (color activation mappings) file path
        input_filename = os.path.split(created_images[0])[1]
        log.debug("Input file name: {}".format(input_filename))
        output_image_path = self.output_dir + '/' + input_filename
        log.debug("Output image path (cam_path): {}".format(output_image_path))
        created_images.append(output_image_path)

        result_dict = self.sr_model.recognize(image_path, predict, output_image_path)

        # Prepare gRPC output message
        self.result = SceneRecognitionResult()
        log.debug("Got result.")
        self.result.data = json.dumps(result_dict)
        log.debug("Output generated. Service successfully completed.")

        for image in created_images:
            service.serviceUtils.clear_file(image)

        return self.result


def serve(max_workers=5, port=7777):
    """The gRPC serve function.

    Params:
    max_workers: pool of threads to execute calls asynchronously
    port: gRPC server port

    Add all your classes to the server here.
    (from generated .py files by protobuf compiler)"""

    server = grpc.server(futures.ThreadPoolExecutor(max_workers=max_workers))
    grpc_bt_grpc.add_SceneRecognitionServicer_to_server(
        SceneRecognitionServicer(), server)
    server.add_insecure_port('[::]:{}'.format(port))
    return server


if __name__ == '__main__':
    """Runs the gRPC server to communicate with the Snet Daemon."""
    parser = service.serviceUtils.common_parser(__file__)
    args = parser.parse_args(sys.argv[1:])
    service.serviceUtils.main_loop(serve, args)
