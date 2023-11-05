from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List

class Data(BaseModel):
    # total: int
    list: dict
#!!
class CommonResponse(BaseModel):
    code: int 
    msg: str
    data: dict

class ListResponse(BaseModel):
    code: int 
    msg: str
    data: list

# class GetAllDeviceListFiled(BaseModel):
# class GetAllDeviceNetworkSpeedFiled(BaseModel):
# class GetAllDeviceStatusFiled(BaseModel):

class DeviceField(BaseModel):
    info: str
    
class SyncAllDeviceTimeField(BaseModel):
    syncTime: int

class SyncDeviceTimeByMACField(BaseModel):
    macAddress: str
    syncTime: int

class SetDeviceWorkTimeRangeByMACField(BaseModel):
    macAddress: str
    beginTime: str
    endTime: str

class SetAllDeviceWorkTimeRangeFiled(BaseModel):
    beginTime: str
    endTime: str

class DeleteDeviceFromListByMACField(BaseModel):
    macAddress: str

#####################################################
class GetConfigField(BaseModel):
    configName: str

class SaveConfigField(BaseModel):
    configName: str
    config: str

class EmptyDeviceDatabaseField(BaseModel):
    macAddress: str