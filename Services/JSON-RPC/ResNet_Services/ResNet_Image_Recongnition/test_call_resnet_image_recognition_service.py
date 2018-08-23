import jsonrpcclient
from services import registry

if __name__ == '__main__':

    try:
        with open('/home/artur/flowers_names.txt', 'r') as my_f:
            for line in my_f:
                url = line.split(';')[0]
                name = line.split(';')[1]
                # Service ONE - Arithmetics
                # jsonrpc_method = input('Which method (flowers|dogs|cars)? ')
                # model = input('Model (ResNet18|50|101|152): ')
                # img_path = input('Image Path: ')
                jsonrpc_port = registry['resnet_image_recognition_service']['jsonrpc']
                r = jsonrpcclient.request("http://127.0.0.1:{}".format(jsonrpc_port),
                                          'flowers',
                                          model='ResNet18',
                                          img_path=url)
                top5 = r['result']['top_5']
                print(name, top5)

    except Exception as e:
        print(e)
