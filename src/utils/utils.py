from pydantic import BaseModel

def strip_values(data: BaseModel, size_limits: dict) -> BaseModel:
    """
    Strip values in the data model if they exceed the specified size limits.

    :param data: Pydantic model containing the data to be processed.
    :param size_limits: Dictionary containing the size limits for each field.
    :return: Processed data model with values stripped to the size limits.
    """
    for key, limit in size_limits.items():
        value = getattr(data, key, None)
        if value and isinstance(value, str) and len(value) > limit:
            setattr(data, key, value[:limit])
    return data