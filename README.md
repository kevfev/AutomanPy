# AutomanPy
Python bindings for AutoMan. See [AutoMan](https://automan-lang.github.io/). 
This package is currently in development.

### System Requirements
To use this package you must be running Python 2.7.15 or 3.2+,Java 8, and Scala 2.11.7+. This package relies on [ScalaPB](https://scalapb.github.io/) and [gRPC](https://grpc.io/). If you use SBT to build this project, all Scala dependencies will be downloaded. To install gRPC for Python (needed for the Python client), follow these [instructions](https://grpc.io/docs/quickstart/python.html).


### How to Install
Use pip to install AutoManPy. 
```
pip install automanpy
```
This software package is currently in development, and will be updated regularly for bug fixes, etc. 
If you want to upgrade, or force the installation of the latest version, use '--no-cache-dir' and '--upgrade'
```
pip install --no-cache-dir automanpy --upgrade
```

### How to Build Source
The easiest way to build this project is by using [SBT](https://www.scala-sbt.org/).To build the source automatically, you can run `./buildproject.sh` located in the root directory. This relies on sbt being installed.  
To build this project manually, from the /AutomanPy directory, run
```
sbt clean compile pack
```
SBT will also compile the necessary .proto into Scala classes automatically. To generate the the python files needed, `grpcio-tools` and `googleapis-common-protos` need to be installed. These python dependencies are automatically installed by pip if this package is installed from the provided tarball (). To install the necessary packages manually, run the following two commands:
```
pip install grpcio-tools
pip install googleapis-common-protos
```
To use gRPC generate the python files needed for interacting with the RPC service, from the /AutomanPy directory, run the following command:

```
python -m grpc_tools.protoc -I src/main/protobuf/ --python_out=src/main/automanpy/automanpy/core/grpc_gen_classes/ --grpc_python_out=src/main/automanpy/automanpy/core/grpc_gen_classes src/main/protobuf/core/grpc_gen_classes/automanlib_rpc.proto src/main/protobuf/core/grpc_gen_classes/automanlib_classes.proto src/main/protobuf/core/grpc_gen_classes/automanlib_wrappers.proto
```

Move the files compiled by sbt into the correct directory by copying them:
```
cp -r target/pack/ src/main/automanpy/automanpy/core/rpc/server/
```

Then change to the directory containing setup.py and run it from there:
```
cd src/main/automanpy/
python setup.py clean sdist
```

### Example Code 
See how to get started, and example code for submitting single and multiple estimate tasks in [`examples/`](https://github.com/kevfev/AutomanPy/tree/master/examples)

### API
See the API under [`API/`](https://github.com/kevfev/AutomanPy/tree/master/API)


