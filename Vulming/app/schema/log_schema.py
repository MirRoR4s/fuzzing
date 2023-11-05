import datetime
from pydantic import BaseModel
from typing import Optional, List

class Data(BaseModel):
    total: int
    list: List

class Response(BaseModel):
    code: int 
    msg: str

class CommonResponse(BaseModel):
    code: int 
    msg: str
    data: dict

class ListResponse(BaseModel):
    code: int 
    msg: str
    data: Data

class S_ListResponse(BaseModel):
    code: int 
    msg: str
    data: List

    
class AuditorlogField(BaseModel):
    info: str

class ApiAccessLogField(BaseModel):
    role: Optional[str] = None
    userName: Optional[str] = None
    object: Optional[str] = None
    type: Optional[str] = None
    pageSize: int
    page: int

class SetApiAccessLogField(BaseModel):
    role: str
    userName: str
    type:str