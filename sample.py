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
    # set_output_directory(`The destination directory for dumping json, pb2 and proto files`)
    MessageProto.set_output_directory("outputs")
    # generate_proto(`proto package name`, `proto file name`)
    proto_file = MessageProto.generate_proto("messageservice", "message_service")
    # generate_pb2(`proto file`)
    MessageProto.generate_pb2(proto_file)
    # generate_wsagger(`proto file`, `version name`)
    swagger_file = MessageProto.generate_swagger(proto_file, "2.0.0")
    # run swagger with Flask
    MessageProto.run_swagger()
    