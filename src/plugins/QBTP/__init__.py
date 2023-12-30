from nonebot import require,on_message
from nonebot.adapters import Event
from nonebot.rule import Rule
from nonebot.adapters.red import PrivateMessageEvent

from ..Index_user_management import *

import re,json,time

keys = [{"3652469329":"RvQdiRnJ3eosMBmL7NnL"},{"1847680031":"thyqbtp"},{"1781396647":"g-675KxYtSXj3KGFUKMeaBPuBsc"}]
def check_authentification(id:str,key:str):
    for k in keys:
        if id in k:return k[id]==key
    return False
def check_QBTP_message(event:PrivateMessageEvent):
    if "QBTP=" in event.get_plaintext():
        return True
    return False
onQBTP = on_message(rule=Rule(check_QBTP_message),priority=10,block=True)
@onQBTP.handle()
async def on_QBTP(event:PrivateMessageEvent):
    data = re.sub("QBTP=","",event.get_plaintext())
    data = json.loads(data)
    header = data["header"]
    Action = data["body"]["Action"]
    content = data["body"]["content"]
    footer = data["footer"]
    if check_authentification(header["From"],header["Authentication"]) and header["From"]==event.get_user_id() and header["To"]=="3046199658":
        if time.time()-footer["timestamp"]<=5000:
            if Action=="addMoney":
                u = User.find_user_by_qid(str(content["user_id"]))
                if u=='NoUser':await onQBTP.finish("NoUser!")
                if u.money+float(content["money"])<=0:
                    await onQBTP.send("火币不足")
                else:
                    u.add_money(content["money"])
                await onQBTP.finish(
                    f'QBTP={{"header":{{"From":"3046199658","To":"{event.get_user_id()}","Content-Type":"JSON"}},"body":{{"content":{{"user_id":"{content["user_id"]}","user_money":{u.money}}},"footer":{{"timestamp":{time.time()}}}}}}}')
        else:await onQBTP.finish("时间超时！")
    else:await onQBTP.finish("鉴权失败！")

# testQBTP = on_message(rule=Rule(check_QBTP_message),priority=9,block=True)
# @testQBTP.handle()
# async def on_QBTP(event:PrivateMessageEvent):
#     data = re.sub("QBTP=","",event.get_plaintext())
#     data = json.loads(data)
#     header = data["header"]
#     action = data["body"]["Action"]
#     content = data["body"]["content"]
#     footer = data["footer"]
#     if check_authentification(header["From"],header["Authentication"]) and header["From"]==event.get_user_id() and header["To"]=="3046199658":
#         if time.time()-footer["timestamp"]<=5000:
#             if action=="addMoney":
#                 u = User.find_user_by_qid(content["user_id"])
#                 await testQBTP.send(u)
#                 u.add_money(content["money"])
#                 await testQBTP.finish('QBTP="header":{"From":"3046199658","To":"{}","Content-Type":"JSON"},"body":{"content":{"group_id":{},"user_id":{},"user_money":{}}}}'.format(event.get_user_id(),content["group_id"],content["user_id"],u.money))
#         else:await testQBTP.finish("时间超时！")
#     else:await testQBTP.finish("鉴权失败！")
# generated_key = secrets.token_urlsafe(15)