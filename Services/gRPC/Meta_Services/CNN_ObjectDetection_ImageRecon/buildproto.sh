#! /bin/bash
python3.6 -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. service/model/ObjectDetection_ImageRecon.proto
