# main.py
from py2proto import ProtoGenerator, relation

class MessageProto(ProtoGenerator):
    class MessageRequest(ProtoGenerator):
        message: str
        number: int
        big_number: "int64"
        unsigned_number: "uint32"
        repeated_field: str
        map_field: str

    class MessageResponse(ProtoGenerator):
        message: str
        status: str  # Enum handling can be added later
        nested: str  # Message handling can be added later

    service = relation("MessageRequest", "MessageResponse")

if __name__ == "__main__":
    # generate_proto(Package, ProtoFileName, Output Directory)
    file_name = MessageProto.generate_proto("messageservice", "message_service", 'protos/')
    # generate_pb2(ProtoFile, Output Directory)
    MessageProto.generate_pb2(file_name, "outputs/")