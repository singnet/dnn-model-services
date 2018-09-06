import base64
import jsonrpcclient
from service import registry

if __name__ == "__main__":

    try:
        endpoint = input(
            "Endpoint (localhost:{}): ".format(
                registry["object_detection_service"]["jsonrpc"]
            )
        )
        if endpoint == "":
            endpoint = "localhost:{}".format(
                registry["object_detection_service"]["jsonrpc"]
            )

        rpc_method = "detect"

        model = input("Model (YOLOv3): ")
        if model == "":
            model = "YOLOv3"

        confidence = input("Confidence (0.7): ")
        if confidence == "":
            confidence = "0.7"

        img_path = input("Image (Path or Link): ")

        ret = jsonrpcclient.request(
            "http://{}".format(endpoint),
            rpc_method,
            model=model,
            confidence=confidence,
            img_path=img_path,
        )
        delta_time = ret["result"]["delta_time"]
        img_base64 = ret["result"]["img_base64"]
        print("Delta time: " + str(delta_time))
        # Storing the image into output.jpg
        imgdata = base64.b64decode(img_base64)
        with open("output.jpg", "wb") as f:
            f.write(imgdata)
        print("Done!")

    except Exception as e:
        print(e)
