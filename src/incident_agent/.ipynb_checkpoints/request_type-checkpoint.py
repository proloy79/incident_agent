from enum import Enum

class RequestType(Enum):
    INITIALIZE="initialize"
    TOOL_CALL = "callTool"
    GET_RESOURCE = "getResource"