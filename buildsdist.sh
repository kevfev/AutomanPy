#!/bin/bash
echo "==> This script builds a source distribution."
echo "==> installing grpcio-tools.."
if pip install grpcio-tools; then
	echo "==> grpcio-tools installed or already installed.."
else
	echo "$(tput setaf 1)==> ERROR: Failed to install grpcio-tools.$(tput sgr0)"
	exit 1
fi
echo "==> installing googleapis-common-protos.."
if pip install googleapis-common-protos; then
	echo "==> googleapis-common-protos installed or already installed.."
else
	echo "$(tput setaf 1)==> ERROR: Failed to install googleapis-common-protos.$(tput sgr0)"
	exit 1
fi
echo "==>  sbt compiling/packing project.."
if sbt clean compile pack; then
	echo "==> sbt successfully compiled/packed pyautoman.."
	cp -R target/pack src/main/automanpy/automanpy/core/rpc_server/
	cp -R README.md src/main/automanpy/
	echo "==>  compiling python protobuf files.."
	cd src/main/automanpy/
	if python -m grpc_tools.protoc -I ../protobuf/ --python_out=. --grpc_python_out=. ../protobuf/automanpy/core/*.proto ../protobuf/automanpy/core/grpc_classes/*.proto; then
		echo "==>  running setup file..."
		python setup.py clean sdist
		echo "==>  finished setting up."
	else
		echo "$(tput setaf 1)==> ERROR: Failed to compile protobuf definition files$(tput sgr0)"
		exit 1
	fi
else
	echo "$(tput setaf 1)==> ERROR: sbt failed to compile or pack pyautoman, please see console for error messages $(tput sgr0)"
	exit 1
fi