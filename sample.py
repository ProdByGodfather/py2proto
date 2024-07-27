from py2proto import ProtoGenerator, relation
from typing import List, Dict

class MessageProto(ProtoGenerator):
    class MessageRequest(ProtoGenerator):
        message: str
        number: int

    class MessageResponse(ProtoGenerator):
        message: str

    # relation(`relation Name`, `request function`, `returnes fucntion`)
    service = relation("SendMessage", "MessageRequest", "MessageResponse")

if __name__ == "__main__":
    # set_output_directory(`The destination directory for dumping json, pb2 and proto files`)
    MessageProto.set_output_directory("outputs")
    
    # generate_proto(`proto package name`, `proto file name`)
    proto_file = MessageProto.generate_proto("messageservice", "message_service")
    
    # generate_pb2(`proto file`)
    MessageProto.generate_pb2(proto_file)
    
    # generate_swagger(`proto file`)
    swagger_file = MessageProto.generate_swagger(proto_file)
    
    # run_swagger(`version`, `port`)
    MessageProto.run_swagger(version="2.0.1", port=5937)
