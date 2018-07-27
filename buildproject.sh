#!/bin/bash

sbt clean compile pack
cp -R target/pack src/main/pyautoman/pyautoman/core/rpc_server/
python -m grpc_tools.protoc -I src/main/protobuf/ --python_out=src/main/pyautoman/pyautoman/core/grpc_gen_classes --grpc_python_out=src/main/pyautoman/pyautoman/core/grpc_gen_classes src/main/protobuf/automanlib_rpc.proto src/main/protobuf/automanlib_classes.proto src/main/protobuf/automanlib_wrappers.proto
cd src/main/pyautoman/
#python setup.py clean --all sdist
