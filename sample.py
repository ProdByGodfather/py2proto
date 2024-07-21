from py2proto import ProtoGenerator, relation
from typing import List, Dict

class MessageProto(ProtoGenerator):
    class MessageRequest(ProtoGenerator):
        message: str
        number: int

    class MessageResponse(ProtoGenerator):
        message: str

    service = relation("MessageRequest", "MessageResponse")

if __name__ == "__main__":
    MessageProto.set_output_directory("outputs")

    proto_file = MessageProto.generate_proto("messageservice", "message_service")
    MessageProto.generate_pb2(proto_file)
    swagger_file = MessageProto.generate_swagger(proto_file)

    MessageProto.run_swagger()
    