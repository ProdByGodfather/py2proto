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