from typing import Dict, Any, Optional
from core.orchestration.lifecycle_record import TaskLifecycleRecord
from core.orchestration.persistence import atomic_write, safe_load

def substitute_variables(task_node: Dict[str, Any], record: Optional[TaskLifecycleRecord], state_path: str) -> Dict[str, Any]:
    variables = {}
    if record:
        variables = record.variables
    else:
        state = safe_load(state_path, {})
        variables = state.get("variables", {})

    def replace_val(v):
        if isinstance(v, str):
            for name, val in variables.items():
                placeholder = "{{" + name + "}}"
                if placeholder in v:
                    v = v.replace(placeholder, str(val))
        elif isinstance(v, dict):
            return {k: replace_val(val) for k, val in v.items()}
        elif isinstance(v, list):
            return [replace_val(item) for item in v]
        return v

    return replace_val(task_node)
