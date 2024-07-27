# py2proto

py2proto is a powerful Python library that simplifies the process of creating gRPC services and Protocol Buffer definitions. It automatically generates .proto files, gRPC code, and Swagger UI documentation from Python class definitions.

## Features

- Automatic generation of .proto files from Python classes
- Generation of gRPC Python code
- Swagger UI generation for easy API testing and documentation
- Support for complex data types (lists, dictionaries)
- Custom output directory setting
- Built-in Swagger UI server

## Installation

Install py2proto using pip:

```bash
pip install py2proto
```

## Usage

1. Import necessary modules:

```python
from py2proto import ProtoGenerator, relation
from typing import List, Dict
```
2. Define your message classes:
```python
class MessageProto(ProtoGenerator):
    class MessageRequest(ProtoGenerator):
        message: str
        number: int

    class MessageResponse(ProtoGenerator):
        message: str

    # relation(`relation Name`, `request function`, `returnes fucntion`)
    service = relation("SendMessage", "MessageRequest", "MessageResponse")
```
3. Generate files and run Swagger UI:
```python
if __name__ == "__main__":
    # set_output_directory(`The destination directory for dumping json, pb2 and proto files`)
    MessageProto.set_output_directory("outputs")
    # generate_proto(`proto package name`, `proto file name`)
    proto_file = MessageProto.generate_proto("messageservice", "message_service")
    # generate_pb2(`proto file`)
    MessageProto.generate_pb2(proto_file)
    # generate_wsagger(`proto file`)
    swagger_file = MessageProto.generate_swagger(proto_file
    # run_swagger(`version`, `port`)
    MessageProto.run_swagger(version="2.0.1", port=5937)
```

This script will generate a .proto file in the 'protos/' directory and pb2 files in the 'outputs/' directory.
Finally, the output of the generated proto file will be as follows:

## Detailed Function Explanations

### relation(method_name: str, request: str, response: str)
Defines a gRPC service method with its request and response types.

Example:
```python
service = relation("SendMessage", "MessageRequest", "MessageResponse")
```

### set_output_directory(directory: str)
Sets the output directory for generated files.

Example:
```python
MessageProto.set_output_directory("custom_output")
```

### generate_proto(package_name: str, file_name: str) -> str
Generates a .proto file based on the defined classes.

Example:
```python
proto_file = MessageProto.generate_proto("mypackage", "myservice")
```

### generate_pb2(proto_file: str)
Generates Python gRPC code from the .proto file.

Example:
```python
MessageProto.generate_pb2(proto_file)
```

### generate_swagger(proto_file: str) -> str
Generates a Swagger JSON file for API documentation.

Example:
```python
swagger_file = MessageProto.generate_swagger(proto_file)
```

### run_swagger()
Starts a Flask server to serve the Swagger UI.

Example:
```python
MessageProto.run_swagger()
```

## Advanced Usage
You can use complex data types in your message definitions:
```python
class ComplexProto(ProtoGenerator):
    class ComplexRequest(ProtoGenerator):
        list_field: List[str]
        dict_field: Dict[str, int]

    class ComplexResponse(ProtoGenerator):
        result: List[Dict[str, str]]

    service = relation("ComplexRequest", "ComplexResponse")
```

## Multiple Services
Define multiple services in a single Proto class:
```python
class MultiServiceProto(ProtoGenerator):
    class Request1(ProtoGenerator):
        field1: str

    class Response1(ProtoGenerator):
        result1: str

    class Request2(ProtoGenerator):
        field2: int

    class Response2(ProtoGenerator):
        result2: int

    service1 = relation("Request1", "Response1")
    service2 = relation("Request2", "Response2")
```

## Why Use py2proto?
1. Simplicity: Define your gRPC services using familiar Python syntax.
2. Automation: Automatically generate .proto files and gRPC code.
3. Documentation: Get Swagger UI documentation out of the box.
4. Flexibility: Support for complex data types and multiple services.
5. Time-saving: Reduce boilerplate code and manual proto file writing.

## Requirements

- Python 3.6+
- grpcio
- grpcio-tools
- Flask (for Swagger UI)


## Supported Data Types

py2proto supports the following Protocol Buffer data types:

- str `(string)`
- int `(int32)`
- float `(float)`
- bool `(bool)`
- bytes `(bytes)`
- "int64" `(int64)`
- "uint32" `(uint32)`
- "uint64" `(uint64)`
- "sint32" `(sint32)`
- "sint64" `(sint64)`
- "fixed32" `(fixed32)`
- "fixed64" `(fixed64)`
- "sfixed32" `(sfixed32)`
- "sfixed64" `(sfixed64)`
- "double" `(double)`
- List[Type] `(repeated)`
- Dict[KeyType, ValueType] `(map)`


## Contributing
Contributions are welcome! Please feel free to submit a Pull Request.
