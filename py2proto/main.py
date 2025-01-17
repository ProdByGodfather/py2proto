import os
import sys
import subprocess
from typing import Dict, List, Tuple, Type
import importlib
import platform
import typing
import json
from google.protobuf.json_format import MessageToDict, ParseDict
from grpc_tools import protoc
import grpc
from flask import Flask, request, jsonify, abort

class ProtoGenerator:
    messages: Dict[str, Dict[str, str]] = {}
    services: List[Tuple[str, str, str, str]] = []
    output_directory: str = os.getcwd()

    @classmethod
    def set_output_directory(cls, directory: str):
        cls.output_directory = os.path.abspath(directory)
        os.makedirs(cls.output_directory, exist_ok=True)

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
            int: "int32", float: "float", str: "string", bool: "bool", bytes: "bytes",
            "int64": "int64", "uint32": "uint32", "uint64": "uint64",
            "sint32": "sint32", "sint64": "sint64", "fixed32": "fixed32",
            "fixed64": "fixed64", "sfixed32": "sfixed32", "sfixed64": "sfixed64",
            "double": "double", "enum": "enum", "message": "message"
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
    def generate_proto(cls, package_name: str, file_name: str):
        proto_path = os.path.join(cls.output_directory, f"{file_name}.proto")
        proto_content = f"syntax = \"proto3\";\n\npackage {package_name};\n\n"
        for message_name, fields in cls.messages.items():
            proto_content += f"message {message_name} {{\n"
            for i, (field_name, field_type) in enumerate(fields.items(), start=1):
                proto_content += f"  {field_type} {field_name} = {i};\n"
            proto_content += "}\n\n"
        for service_name, method_name, request, response in cls.services:
            proto_content += f"service {service_name} {{\n"
            proto_content += f"  rpc {method_name} ({request}) returns ({response}) {{}}\n"
            proto_content += "}\n"
        with open(proto_path, "w") as f:
            f.write(proto_content)
        print(f"Proto file '{proto_path}' generated successfully.")
        return proto_path
    @classmethod
    def generate_swagger(cls, proto_file):
        swagger_file = os.path.join(cls.output_directory, "swagger.json")
        
        protoc.main((
            '',
            f'-I{cls.output_directory}',
            f'--python_out={cls.output_directory}',
            f'--grpc_python_out={cls.output_directory}',
            proto_file
        ))
        
        module_name = os.path.splitext(os.path.basename(proto_file))[0]
        sys.path.append(cls.output_directory)
        pb2 = importlib.import_module(f"{module_name}_pb2")
        pb2_grpc = importlib.import_module(f"{module_name}_pb2_grpc")
    
        swagger = {
            "swagger": "2.0",
            "info": {"title": module_name, "version": "1.0.0"},
            "schemes": ["http"],
            "consumes": ["application/json"],
            "produces": ["application/json"],
            "paths": {}
        }
    
        type_mapping = {
            1: "number", 2: "number", 3: "string", 4: "string", 5: "number",
            6: "string", 7: "number", 8: "boolean", 9: "string", 11: "string",
            13: "number", 14: "string", 15: "number", 16: "string", 17: "number", 18: "string",
        }
    
        def descriptor_to_json(descriptor):
            fields = {}
            for field in descriptor.fields:
                field_type = type_mapping.get(field.type, "string")
                if field.type == field.TYPE_MESSAGE:
                    field_type = descriptor_to_json(field.message_type)
                elif field.type == field.TYPE_ENUM:
                    field_type = "string"
                if field.label == field.LABEL_REPEATED:
                    fields[field.name] = {"type": "array", "items": {"type": field_type}}
                else:
                    fields[field.name] = {"type": field_type}
            return {"type": "object", "properties": fields}
    
        for service_name, service in pb2.DESCRIPTOR.services_by_name.items():
            for method in service.methods:
                path = f"/{service_name}/{method.name}"
                swagger["paths"][path] = {
                    "get": {
                        "summary": method.name,
                        "parameters": [
                            {
                                "in": "query",
                                "name": "server_url",
                                "type": "string",
                                "required": True,
                                "description": "gRPC server URL (e.g., localhost:50051)"
                            }
                        ] + [
                            {
                                "in": "query",
                                "name": field.name,
                                "type": type_mapping.get(field.type, "string"),
                                "required": False,
                                "description": f"Field {field.name}"
                            } for field in method.input_type.fields
                        ],
                        "responses": {
                            "200": {
                                "description": "Successful response",
                                "schema": descriptor_to_json(method.output_type)
                            }
                        }
                    }
                }
    
        with open(swagger_file, 'w') as f:
            json.dump(swagger, f, indent=2)
        
        return swagger_file

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

    @classmethod
    def generate_pb2(cls, proto_file: str):
        if not ProtoGenerator.check_and_install_grpcio_tools():
            print("Unable to proceed without grpcio-tools.")
            return
        try:
            system = platform.system().lower()
            python_command = sys.executable if system == "windows" else "python3"
            proto_path = os.path.abspath(proto_file)
            proto_dir = os.path.dirname(proto_path)
            subprocess.run([python_command, '-m', 'grpc_tools.protoc',
                            f'-I{proto_dir}',
                            f'--python_out={cls.output_directory}',
                            f'--grpc_python_out={cls.output_directory}',
                            proto_path],
                           check=True)
            base_name = os.path.splitext(os.path.basename(proto_file))[0]
            print(f"Generated {base_name}_pb2.py and {base_name}_pb2_grpc.py in {cls.output_directory} successfully.")
        except Exception as e:
            print(f"An error occurred: {e}")

    @classmethod
    def generate_grpc_code(cls, languages, proto_file, port=50051):
        supported_languages = ['python', 'javascript']
        for lang in languages:
            if lang not in supported_languages:
                print(f"Warning: {lang} is not supported. Skipping.")
                continue
            
            cls._generate_server(lang, proto_file, port)
            cls._generate_client(lang, proto_file, port)

    @classmethod
    def _generate_server(cls, language, proto_file, port):
        output_dir = os.path.join(cls.output_directory, language)
        os.makedirs(output_dir, exist_ok=True)
        
        if language == 'python':
            cls._generate_python_server(proto_file, port, output_dir)
        elif language == 'javascript':
            cls._generate_javascript_server(proto_file, port, output_dir)

    @classmethod
    def _generate_client(cls, language, proto_file, port):
        output_dir = os.path.join(cls.output_directory, language)
        os.makedirs(output_dir, exist_ok=True)
        
        if language == 'python':
            cls._generate_python_client(proto_file, port, output_dir)
        elif language == 'javascript':
            cls._generate_javascript_client(proto_file, port, output_dir)

    @classmethod
    def _generate_python_server(cls, proto_file, port, output_dir):
        server_code = f"""
import grpc
from concurrent import futures
import {os.path.splitext(os.path.basename(proto_file))[0]}_pb2 as pb2
import {os.path.splitext(os.path.basename(proto_file))[0]}_pb2_grpc as pb2_grpc

class MessageService(pb2_grpc.MessageServiceServicer):
    def SendMessage(self, request, context):
        message = f"Received: {{request.message}}"
        return pb2.MessageResponse(message=message)

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    pb2_grpc.add_MessageServiceServicer_to_server(MessageService(), server)
    server.add_insecure_port('[::]:{port}')
    server.start()
    server.wait_for_termination()

if __name__ == '__main__':
    serve()
"""
        with open(os.path.join(output_dir, 'server.py'), 'w') as f:
            f.write(server_code)

    @classmethod
    def _generate_python_client(cls, proto_file, port, output_dir):
        client_code = f"""
import grpc
import {os.path.splitext(os.path.basename(proto_file))[0]}_pb2 as pb2
import {os.path.splitext(os.path.basename(proto_file))[0]}_pb2_grpc as pb2_grpc

def run():
    with grpc.insecure_channel('localhost:{port}') as channel:
        stub = pb2_grpc.MessageServiceStub(channel)
        response = stub.SendMessage(pb2.MessageRequest(message='Hello, Server!'))
    print("Client received: " + response.message)

if __name__ == '__main__':
    run()
"""
        with open(os.path.join(output_dir, 'client.py'), 'w') as f:
            f.write(client_code)

    @classmethod
    def _generate_javascript_server(cls, proto_file, port, output_dir):
        server_code = f"""
const grpc = require('grpc');
const protoLoader = require('@grpc/proto-loader');

const PROTO_PATH = './{os.path.basename(proto_file)}';

const packageDefinition = protoLoader.loadSync(PROTO_PATH, {{
    keepCase: true,
    longs: String,
    enums: String,
    defaults: true,
    oneofs: true
}});

const protoDescriptor = grpc.loadPackageDefinition(packageDefinition);
const messageService = protoDescriptor.MessageService;

function sendMessage(call, callback) {{
    callback(null, {{ message: 'Hello ' + call.request.message }});
}}

function main() {{
    const server = new grpc.Server();
    server.addService(messageService.service, {{ sendMessage: sendMessage }});
    server.bind('0.0.0.0:{port}', grpc.ServerCredentials.createInsecure());
    server.start();
    console.log('Server running at http://0.0.0.0:{port}');
}}

main();
"""
        with open(os.path.join(output_dir, 'server.js'), 'w') as f:
            f.write(server_code)

    @classmethod
    def _generate_javascript_client(cls, proto_file, port, output_dir):
        client_code = f"""
const grpc = require('grpc');
const protoLoader = require('@grpc/proto-loader');

const PROTO_PATH = './{os.path.basename(proto_file)}';

const packageDefinition = protoLoader.loadSync(PROTO_PATH, {{
    keepCase: true,
    longs: String,
    enums: String,
    defaults: true,
    oneofs: true
}});

const protoDescriptor = grpc.loadPackageDefinition(packageDefinition);
const messageService = protoDescriptor.MessageService;

function main() {{
    const client = new messageService('localhost:{port}', grpc.credentials.createInsecure());
    client.sendMessage({{ message: 'Hello, Server!' }}, (error, response) => {{
        if (!error) {{
            console.log('Client received: ' + response.message);
        }} else {{
            console.error(error);
        }}
    }});
}}

main();
"""
        with open(os.path.join(output_dir, 'client.js'), 'w') as f:
            f.write(client_code)

    @classmethod
    def generate_grpc_files(cls, languages, proto_file, port=50051):
        cls.generate_pb2(proto_file)
        cls.generate_grpc_code(languages, proto_file, port)

    @classmethod
    def run_flask(cls):
        swagger_file = os.path.join(cls.output_directory, "swagger.json")
        
        app = Flask(__name__)
        
        swagger_file_path = os.path.abspath(swagger_file)

        sys.path.append(cls.output_directory)

        @app.route('/')
        def swagger_ui():
            return """
            <!DOCTYPE html>
            <html lang="en">
            <head>
                <meta charset="UTF-8">
                <title>Swagger UI</title>
                <link rel="stylesheet" type="text/css" href="https://cdnjs.cloudflare.com/ajax/libs/swagger-ui/3.51.1/swagger-ui.css" >
                <script src="https://cdnjs.cloudflare.com/ajax/libs/swagger-ui/3.51.1/swagger-ui-bundle.js"> </script>
            </head>
            <body>
                <div id="swagger-ui"></div>
                <script>
                    window.onload = function() {
                        SwaggerUIBundle({
                            url: "/swagger.json",
                            dom_id: '#swagger-ui',
                            presets: [
                                SwaggerUIBundle.presets.apis,
                                SwaggerUIBundle.SwaggerUIStandalonePreset
                            ],
                            layout: "BaseLayout"
                        })
                    }
                </script>
            </body>
            </html>
            """

        @app.route('/swagger.json')
        def swagger_json():
            try:
                print(f"Serving swagger file from: {swagger_file_path}")
                with open(swagger_file_path, 'r') as f:
                    swagger_data = json.load(f)
                return jsonify(swagger_data)
            except Exception as e:
                print(f"Error serving swagger file: {e}")
                abort(500)

        @app.route('/<service>/<method>', methods=['GET'])
        def grpc_request(service, method):
            server_url = request.args.get('server_url')
            if not server_url:
                return jsonify({"error": "server_url is required"}), 400
            
            try:
                pb2 = importlib.import_module(f"message_service_pb2")
                pb2_grpc = importlib.import_module(f"message_service_pb2_grpc")

                channel = grpc.insecure_channel(server_url)
                stub_class = getattr(pb2_grpc, f"{service}Stub")
                stub = stub_class(channel)

                request_class = getattr(pb2, f"{method}Request")
                request_message = request_class()
                for field in request_class.DESCRIPTOR.fields:
                    value = request.args.get(field.name)
                    if value is not None:
                        if field.type == field.TYPE_MESSAGE:
                            sub_message = getattr(request_message, field.name)
                            ParseDict(json.loads(value), sub_message)
                        elif field.type in [field.TYPE_INT32, field.TYPE_INT64]:
                            setattr(request_message, field.name, int(value))
                        elif field.type == field.TYPE_BOOL:
                            setattr(request_message, field.name, value.lower() == 'true')
                        else:
                            setattr(request_message, field.name, value)

                grpc_method = getattr(stub, method)
                response = grpc_method(request_message)

                response_dict = MessageToDict(response, preserving_proto_field_name=True)
                return jsonify(response_dict)
            except Exception as e:
                print(f"Error processing gRPC request: {e}")
                return jsonify({"error": str(e)}), 500

        @app.route('/generate_grpc', methods=['POST'])
        def generate_grpc():
            data = request.json
            languages = data.get('languages', [])
            proto_file = data.get('proto_file')
            port = data.get('port', 50051)

            if not languages or not proto_file:
                return jsonify({"error": "Missing required parameters"}), 400

            try:
                cls.generate_grpc_files(languages, proto_file, port)
                return jsonify({"message": "gRPC files generated successfully"}), 200
            except Exception as e:
                return jsonify({"error": str(e)}), 500

        print(f"Starting Swagger UI on port 5000")
        app.run(debug=True, port=5000)

def relation(method_name: str, request: str, response: str):
    return ("MessageService", method_name, request, response)
