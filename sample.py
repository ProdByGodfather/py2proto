from py2proto import ProtoGenerator, relation

class MessageProto(ProtoGenerator):
    class MessageRequest(ProtoGenerator):
        message: str
        number: int

    class MessageResponse(ProtoGenerator):
        message: str

    service = relation("SendMessage", "MessageRequest", "MessageResponse")

if __name__ == "__main__":
    # Set output directory
    MessageProto.set_output_directory("outputs")
    
    # Generate proto file
    proto_file = MessageProto.generate_proto("messageservice", "message_service")
    
    # Generate pb2 files
    MessageProto.generate_pb2(proto_file)
    
    # Generate Swagger file
    swagger_file = MessageProto.generate_swagger(proto_file)
    
    # Generate gRPC files for Python and JavaScript
    MessageProto.generate_grpc_files(['python', 'javascript'], proto_file, port=50051)
    
    # Run Swagger UI
    MessageProto.run_flask()

    
