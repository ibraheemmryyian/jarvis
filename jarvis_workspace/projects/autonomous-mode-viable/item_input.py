from pydantic import BaseModel, validator

class ItemInput(BaseModel):
    name: str
    description: str = None

    @validator("name")
    def name_must_contain_space(cls, v):
        if " " not in v:
            raise ValueError("must contain space")
        return v.title()