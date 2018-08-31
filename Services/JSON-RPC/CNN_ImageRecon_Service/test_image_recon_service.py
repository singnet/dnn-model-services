import jsonrpcclient
from service import registry

if __name__ == "__main__":

    try:
        endpoint = input(
            "Endpoint (localhost:{}): ".format(
                registry["image_recon_service"]["jsonrpc"]
            )
        )
        if endpoint == "":
            endpoint = "localhost:{}".format(registry["image_recon_service"]["jsonrpc"])

        rpc_method = input("Method (flowers|dogs|cars): ")

        model = input("Model (ResNet18): ")
        if model == "":
            model = "ResNet18"

        img_path = input("Image (Path or Link): ")

        ret = jsonrpcclient.request(
            "http://{}".format(endpoint), rpc_method, model=model, img_path=img_path
        )
        delta_time = ret["result"]["delta_time"]
        top5 = ret["result"]["top_5"]
        print("Delta time: " + str(delta_time))
        for (k, v) in sorted(top5.items()):
            print("{0} - {1}".format(k, v))

    except Exception as e:
        print(e)
