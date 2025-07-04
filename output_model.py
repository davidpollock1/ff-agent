from pydantic import BaseModel


class OutputModel(BaseModel):
    """_summary_

    Args:
        BaseModel (_type_): _description_
    """

    summary: str
    suggested_changes: str
