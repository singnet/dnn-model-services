#! /bin/bash
python2 -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. service/service_spec/video_cap.proto
