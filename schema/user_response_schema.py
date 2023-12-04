from pydantic import BaseModel


class UserRegisterResponse(BaseModel):
    message: str
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "message": "register success",

                }
            ]
        }
    }
