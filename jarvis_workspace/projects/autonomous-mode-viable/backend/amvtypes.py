from typing import Any, Dict, List, Optional, Union

# Custom types for Autonomous Mode Viable project
class AMVTypes:
    class ConfigData(types.TypedDict):
        config_name: str
        config_value: Any

    class CommandResponse(types.TypedDict):
        status: str
        message: str
        data: Optional[Dict[str, Any]]

    class CommandRequest(types.TypedDict):
        user_id: str
        command_text: str
        context_files: List[str]

    class ContextFile(types.TypedDict):
        file_name: str
        file_content: str

    class FileResponse(types.TypedDict):
        status: str
        message: Optional[str]
        content: Union[bytes, str]