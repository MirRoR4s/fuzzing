# # routers/log_api.py
# import base64
# import json
# from loguru import logger
# from fastapi import APIRouter, Depends, Header, Response, HTTPException, status
# from schema.log_schema import AuditorlogField, ApiAccessLogField
# from .users_api import oauth2_scheme, revoked_tokens

# router = APIRouter(prefix="/log", tags=["日志管理"])



# #获取审计日志接口
# @router.post('/auditorLog', name="获取审计日志")
# async def get_auditor_log(log_info: AuditorlogField, token: str = Depends(oauth2_scheme)):
#         if token in revoked_tokens:
#             raise HTTPException(
#                 status_code=status.HTTP_401_UNAUTHORIZED,
#                 detail="Token out date",
#                 headers={"WWW-Authenticate": "Bearer"},
#             )
#         return user_controller.get_current_user(token)
#     auth_role_levle = get_current_user_role_level(token) 
#     if auth_role_levle[0] != "auditor" :  
#         return {'code': 411, 'msg': '权限不足'}
#     else:
#         loginfo = log_info.info
#         decrypted_data = decrypt_aes(key, iv, loginfo)
#         decrypted_data_dict = json.loads(decrypted_data)
#         protocolType = decrypted_data_dict.get('protocolType')
#         sourceIP = decrypted_data_dict.get('sourceIP')
#         destIP = decrypted_data_dict.get('destIP')
#         eventType = decrypted_data_dict.get('eventType')
#         level = decrypted_data_dict.get('level')
#         page = decrypted_data_dict.get('page')
#         pageSize = decrypted_data_dict.get('pageSize')
#         currentname = auth_role_levle[2]
#         controller = LogController(currentname)
#         return controller.get_auditor_log(protocolType, sourceIP,destIP, eventType,level,page, pageSize)
        
    
        

# #获取操作日志接口
# @router.post('/apiAccessLog', name="获取操作日志")
# async def get_api_access_log(log_info: AuditorlogField,token: str = Depends(oauth2_scheme)):
#     auth_role_levle = get_current_user_role_level(token) 
#     if auth_role_levle[0] != "auditor" :  
#         return {'code': 411, 'msg': '权限不足'}
#     else:
#         loginfo = log_info.info
#         decrypted_data = decrypt_aes(key, iv, loginfo)
#         decrypted_data_dict = json.loads(decrypted_data)
#         role = decrypted_data_dict.get('role')
#         level = decrypted_data_dict.get('level')
#         username = decrypted_data_dict.get('userName')
#         object = decrypted_data_dict.get('object')
#         type = decrypted_data_dict.get('type')
#         page = decrypted_data_dict.get('page')
#         pageSize = decrypted_data_dict.get('pageSize')
#         currentname = auth_role_levle[2]
#         controller = LogController(currentname)
#         return controller.get_api_access_log(role,level,username,object,type,page,pageSize)


# # >>下载操作日志备份文件
# @router.get('/apiAccessLogBackUp', name="下载操作日志备份文件")
# async def api_access_log_backup(token: str = Depends(oauth2_scheme)):
#     auth_role_levle = get_current_user_role_level(token) 
#     if not (auth_role_levle[0] == "admin" and auth_role_levle[1] == "high"):  
#         return {'code': 411, 'msg': '权限不足'}
#     else:   
#         currentname = auth_role_levle[2]
#         controller = LogController(currentname)
#         file_path = controller.log_get_APIAccess_log_file()[1]
#         file_name = controller.log_get_APIAccess_log_file()[0]  
#         file_content = open(file_path, 'rb').read()
#         return Response(content=file_content, 
#             media_type='application/octet-stream',
#             headers={'Content-Disposition': f'attachment; filename="{file_name}"'})


# # >>获取用户操作统计结果
# @router.get('/getStatistics', name="获取用户操作统计结果")
# async def get_statistics(token: str = Depends(oauth2_scheme)):
#     auth_role_levle = get_current_user_role_level(token) 
#     if auth_role_levle[0] != "auditor" :  
#         return {'code': 411, 'msg': '权限不足'}
#     else:
#         currentname = auth_role_levle[2]
#         controller = LogController(currentname)
#         return controller.log_get_user_operation_statistics()
        
# #>>下载审计日志备份文件
# @router.get('/auditorLogBackUp',name="下载审计日志备份文件")
# async def auditor_log(token: str = Depends(oauth2_scheme)):
#     auth_role_levle = get_current_user_role_level(token) 
#     if auth_role_levle[0] != "admin" or auth_role_levle[1] != "high":  
#         return {'code': 411, 'msg': '权限不足'}
#     else:
#         currentname = auth_role_levle[2]
#         controller = LogController(currentname)
#         file_path = controller.log_get_auditor_log_file()[1]
#         file_name = controller.log_get_auditor_log_file()[0]
#         file_content = open(file_path, 'rb').read()
#         return Response(content=file_content, 
#             media_type='application/octet-stream',
#             headers={'Content-Disposition': f'attachment; filename="{file_name}"'})

# # >>清空审计日志数据库:
# @router.post('/emptyAuditorLog', name="清空审计日志数据库")
# async def empty_auditor_log(token: str = Depends(oauth2_scheme)):
#     auth_role_levle = get_current_user_role_level(token) 
#     if auth_role_levle[0] != "admin" or auth_role_levle[1] != "high": 
#         return {'code': 411, 'msg': '权限不足'}
#     else:
#         currentname = auth_role_levle[2]
#         controller = LogController(currentname)
#         return controller.log_empty_auditor_log()
        

# #>>获取后端当前磁盘用量:
# @router.get('/getDiskusage',name="获取后端当前磁盘用量")
# async def get_diskusage(token: str = Depends(oauth2_scheme)):
#     auth_role_levle = get_current_user_role_level(token) 
#     if auth_role_levle[0] != "admin" or auth_role_levle[1] == "root":
#         return {'code': 411, 'msg': '权限不足'}
#     else:
#         currentname = auth_role_levle[2]
#         controller = LogController(currentname)
#         return controller.log_get_server_diskusage()
        

# #>>获取异常事件统计结果:
# @router.get('/eventStatistics' ,name="获取异常事件统计结果")
# async def get_event_statistics(token: str = Depends(oauth2_scheme)):
#     auth_role_levle = get_current_user_role_level(token) 
#     if auth_role_levle[0] != "auditor": 
#         return {'code': 411, 'msg': '权限不足'}
#     else:
#         currentname = auth_role_levle[2]
#         controller = LogController(currentname)
#         return controller.log_get_events_statistics()
       
