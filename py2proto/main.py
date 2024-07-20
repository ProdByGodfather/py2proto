import os
import sys
import subprocess
from typing import Dict, List, Tuple, Type
import importlib.util
import platform
import typing

class ProtoGenerator:
    messages: Dict[str, Dict[str, str]] = {}
    services: List[Tuple[str, str, str]] = []

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        cls.messages = {}
        cls.services = []
        for attr_name, attr_value in cls.__dict__.items():
            if isinstance(attr_value, type):
                if issubclass(attr_value, ProtoGenerator):
                    cls._add_message(attr_name, attr_value.__annotations__)
            elif attr_name == 'service':
                cls._add_service(attr_value)

    @classmethod
    def _add_message(cls, name: str, fields: Dict[str, Type]):
        proto_fields = {}
        for field_name, field_type in fields.items():
            proto_fields[field_name] = cls._get_proto_type(field_type)
        cls.messages[name] = proto_fields

    @staticmethod
    def _get_proto_type(python_type):
        type_mapping = {
            int: "int32",
            float: "float",
            str: "string",
            bool: "bool",
            bytes: "bytes",
            "int64": "int64",
            "uint32": "uint32",
            "uint64": "uint64",
            "sint32": "sint32",
            "sint64": "sint64",
            "fixed32": "fixed32",
            "fixed64": "fixed64",
            "sfixed32": "sfixed32",
            "sfixed64": "sfixed64",
            "double": "double",
            "enum": "enum",
            "message": "message"
        }

        if isinstance(python_type, str):
            return type_mapping.get(python_type, python_type)
        
        origin = typing.get_origin(python_type)
        if origin == list:
            args = typing.get_args(python_type)
            if args:
                return f"repeated {ProtoGenerator._get_proto_type(args[0])}"
            return "repeated string"
        elif origin == dict:
            args = typing.get_args(python_type)
            if len(args) == 2:
                key_type = ProtoGenerator._get_proto_type(args[0])
                value_type = ProtoGenerator._get_proto_type(args[1])
                return f"map<{key_type}, {value_type}>"
            return "map<string, string>"
        
        return type_mapping.get(python_type, "string")

    @classmethod
    def _add_service(cls, service_def):
        cls.services.append(service_def)

    @classmethod
    def generate_proto(cls, package_name: str, file_name: str, output_dir: str = None):
        if output_dir is None:
            output_dir = os.getcwd()
        else:
            os.makedirs(output_dir, exist_ok=True)
        
        proto_path = os.path.join(output_dir, f"{file_name}.proto")

        proto_content = f"syntax = \"proto3\";\n\npackage {package_name};\n\n"

        for message_name, fields in cls.messages.items():
            proto_content += f"message {message_name} {{\n"
            for i, (field_name, field_type) in enumerate(fields.items(), start=1):
                if field_type.startswith("repeated"):
                    proto_content += f"  {field_type} {field_name} = {i};\n"
                elif field_type.startswith("map"):
                    proto_content += f"  {field_type} {field_name} = {i};\n"
                else:
                    proto_content += f"  {field_type} {field_name} = {i};\n"
            proto_content += "}\n\n"

        for service_name, request, response in cls.services:
            proto_content += f"service {service_name} {{\n"
            proto_content += f"  rpc SendMessage ({request}) returns ({response}) {{}}\n"
            proto_content += "}\n"

        with open(proto_path, "w") as f:
            f.write(proto_content)

        print(f"Proto file '{proto_path}' generated successfully.")
        return proto_path

    @staticmethod
    def check_and_install_grpcio_tools():
        try:
            import grpc_tools.protoc
            print("grpcio-tools is already installed.")
            return True
        except ImportError:
            print("grpcio-tools is not installed. Attempting to install...")
            try:
                subprocess.check_call([sys.executable, "-m", "pip", "install", "grpcio-tools"])
                print("grpcio-tools has been successfully installed.")
                return True
            except subprocess.CalledProcessError as e:
                print(f"Failed to install grpcio-tools: {e}")
                return False

    @staticmethod
    def generate_pb2(proto_file: str, output_dir: str = None):
        if not ProtoGenerator.check_and_install_grpcio_tools():
            print("Unable to proceed without grpcio-tools.")
            return

        try:
            system = platform.system().lower()
            if system == "windows":
                python_command = sys.executable
            elif system in ["linux", "darwin"]:  # darwin is for macOS
                python_command = "python3"
            else:
                raise OSError(f"Unsupported operating system: {system}\nplease install grpcio-tools")

            proto_path = os.path.abspath(proto_file)
            proto_dir = os.path.dirname(proto_path)
            
            if output_dir is None:
                output_dir = os.getcwd()
            else:
                os.makedirs(output_dir, exist_ok=True)

            subprocess.run([python_command, '-m', 'grpc_tools.protoc',
                            f'-I{proto_dir}',
                            f'--python_out={output_dir}',
                            f'--grpc_python_out={output_dir}',
                            proto_path],
                           check=True)
            
            base_name = os.path.splitext(os.path.basename(proto_file))[0]
            print(f"Generated {base_name}_pb2.py and {base_name}_pb2_grpc.py in {output_dir} successfully.")
        except subprocess.CalledProcessError as e:
            print(f"Error generating pb2 files: {e}")
            print(f"Command used: {' '.join(e.cmd)}")
        except OSError as e:
            print(f"OS Error: {e}")
        except Exception as e:
            print(f"An unexpected error occurred: {e}")

def relation(request: str, response: str):
    return ("MessageService", request, response)