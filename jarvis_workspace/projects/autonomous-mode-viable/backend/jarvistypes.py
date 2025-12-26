from typing import Any, Dict, List, Optional, Union

class JarvisTypes:
    @staticmethod
    def get_types() -> Dict[str, Any]:
        return {
            "Any": Any,
            "Dict": Dict,
            "List": List,
            "Optional": Optional,
            "Union": Union,
        }