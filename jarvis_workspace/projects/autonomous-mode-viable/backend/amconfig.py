from typing import Any, Callable, Dict, List, Optional, Tuple, Union

# Custom types for Autonomous Mode
class AMConfig(Dict[str, Any]):
    pass

class AMState(Dict[str, Any]):
    pass

class AMAction(Union[Callable[[AMState], None], str]):
    pass

class AMIntent(Tuple[str, Dict[str, Any]]):
    pass