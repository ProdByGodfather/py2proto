# py2proto

py2proto is a Python library that provides an ORM-like interface for generating gRPC proto files and pb2 files. It simplifies the process of creating and managing Protocol Buffer definitions for gRPC services.

## Features

- ORM-like syntax for defining Protocol Buffer messages and services
- Automatic generation of .proto files
- Automatic generation of pb2 and pb2_grpc files
- Support for various Protocol Buffer data types, including repeated fields
- Easy-to-use API for defining services and message relationships

## Installation

You can install py2proto using pip:

```bash
pip install py2proto
```

## Usage

Here's a basic example of how to use py2proto:

```python
from py2proto import ProtoGenerator, relation
from typing import List, Dict

class MessageProto(ProtoGenerator):
    class MessageRequest(ProtoGenerator):
        message: str
        number: int
        big_number: "int64"
        unsigned_number: "uint32"
        repeated_field: List[str]  # This will be a repeated field
        map_field: Dict[str, int]  # This will be a map field

    class MessageResponse(ProtoGenerator):
        message: str
        status: str
        nested: str

    service = relation("MessageRequest", "MessageResponse")

if __name__ == "__main__":
    # generate_proto(Package, ProtoFileName, Output Directory)
    file_name = MessageProto.generate_proto("messageservice", "message_service", 'protos/')
    # generate_pb2(ProtoFile, Output Directory)
    MessageProto.generate_pb2(file_name, "outputs/")
```

This script will generate a .proto file in the 'protos/' directory and pb2 files in the 'outputs/' directory.
Finally, the output of the generated proto file will be as follows:

```proto
syntax = "proto3";

package messageservice;

message MessageRequest {
  string message = 1;
  int32 number = 2;
  int64 big_number = 3;
  uint32 unsigned_number = 4;
  repeated string repeated_field = 5;
  map<string, int32> map_field = 6;
}

message MessageResponse {
  string message = 1;
  string status = 2;
  string nested = 3;
}

service MessageService {
  rpc SendMessage (MessageRequest) returns (MessageResponse) {}
}
```

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

## API Reference
### ProtoGenerator
The base class for defining Protocol Buffer messages and services.
### relation(request: str, response: str)
A function to define the relationship between request and response messages in a service.
### generate_proto(package_name: str, file_name: str, output_dir: str = None)
Generates a `.proto` file with the specified package name and file name.
- package_name: The name of the package for the Protocol Buffer definitions.
- file_name: The name of the output .proto file (without extension).
- output_dir: (Optional) The directory where the .proto file will be saved. If not specified, it will use the current directory.
### generate_pb2(proto_file: str, output_dir: str = None)
Generates pb2 and pb2_grpc files from the specified `.proto` file.
- proto_file: The path to the .proto file.
- output_dir: **(Optional)** The directory where the pb2 files will be saved. If not specified, it will use the current directory.

## Contributing
Contributions are welcome! Please feel free to submit a Pull Request.
