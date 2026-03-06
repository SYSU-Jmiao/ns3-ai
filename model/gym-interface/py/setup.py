# Copyright (c) 2023 Huazhong University of Science and Technology
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation;
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#
# Author: Muyuan Shen <muyuan_shen@hust.edu.cn>


import os
import subprocess
import sys
from setuptools import setup, find_packages


def generate_proto():
    """Generate messages_pb2.py from messages.proto.

    The generated file is version-tied to the installed protobuf runtime, so
    it must NOT be committed to the repository; instead it is regenerated here
    each time the package is (re-)installed.

    Resolution order:
      1. grpc_tools.protoc  – ships with grpcio-tools, always version-matched
      2. system ``protoc``  – available when protobuf-compiler is installed
    """
    script_dir = os.path.dirname(os.path.abspath(__file__))
    proto_file = os.path.abspath(
        os.path.join(script_dir, "..", "messages.proto")
    )
    proto_dir = os.path.dirname(proto_file)
    out_dir = os.path.join(script_dir, "ns3ai_gym_env")

    if not os.path.isfile(proto_file):
        print(
            "WARNING: messages.proto not found at {}; "
            "messages_pb2.py will not be generated.".format(proto_file),
            file=sys.stderr,
        )
        return

    # 1. Try grpc_tools (always version-matched to the installed protobuf).
    try:
        import grpc_tools
        from grpc_tools import protoc as grpc_protoc

        # grpc_tools bundles google/protobuf/*.proto under its _proto dir.
        grpc_proto_include = os.path.join(
            os.path.dirname(grpc_tools.__file__), "_proto"
        )
        ret = grpc_protoc.main(
            [
                "grpc_tools.protoc",
                "-I{}".format(proto_dir),
                "-I{}".format(grpc_proto_include),
                "--python_out={}".format(out_dir),
                proto_file,
            ]
        )
        if ret == 0:
            print("ns3ai_gym_env setup: generated messages_pb2.py via grpc_tools")
            return
    except ImportError:
        pass

    # 2. Fall back to the system protoc binary.
    try:
        result = subprocess.run(
            [
                "protoc",
                "-I{}".format(proto_dir),
                "--python_out={}".format(out_dir),
                proto_file,
            ],
            check=True,
            stderr=subprocess.PIPE,
            text=True,
        )
        print("ns3ai_gym_env setup: generated messages_pb2.py via system protoc")
        return
    except subprocess.CalledProcessError as exc:
        print(
            "WARNING: system protoc failed:\n{}".format(exc.stderr),
            file=sys.stderr,
        )
    except FileNotFoundError:
        pass

    print(
        "WARNING: Could not generate messages_pb2.py from messages.proto.\n"
        "The ns3ai_gym_env package will not work until this file exists.\n"
        "To fix, choose one of:\n"
        "  1. Build the project with CMake first (./ns3 build ai)\n"
        "  2. pip install grpcio-tools  then re-install this package\n"
        "  3. sudo apt install protobuf-compiler  then re-install this package",
        file=sys.stderr,
    )


generate_proto()

setup(
    name="ns3ai_gym_env",
    version="0.0.1",
    packages=find_packages(),
    install_requires=["numpy", "gymnasium", "protobuf"],
)
