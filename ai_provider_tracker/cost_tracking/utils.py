from decimal import Decimal, InvalidOperation
from typing import Any, Dict, Iterable, Optional


def to_decimal(value: Any) -> Optional[Decimal]:
    if value is None:
        return None
    if isinstance(value, Decimal):
        return value
    try:
        return Decimal(str(value))
    except (InvalidOperation, ValueError, TypeError):
        return None


def to_plain_data(value: Any) -> Any:
    if value is None:
        return {}
    if isinstance(value, dict):
        return {str(k): to_plain_data(v) for k, v in value.items()}
    if isinstance(value, list):
        return [to_plain_data(v) for v in value]
    if isinstance(value, tuple):
        return [to_plain_data(v) for v in value]
    if hasattr(value, "model_dump"):
        return to_plain_data(value.model_dump())
    if hasattr(value, "dict"):
        return to_plain_data(value.dict())
    if hasattr(value, "__dict__") and not isinstance(value, (str, bytes)):
        return to_plain_data(vars(value))
    return value


def get_nested(data: Dict[str, Any], paths: Iterable[str]) -> Any:
    for path in paths:
        current: Any = data
        for part in path.split("."):
            if isinstance(current, dict) and part in current:
                current = current[part]
            else:
                current = None
                break
        if current is not None:
            return current
    return None
