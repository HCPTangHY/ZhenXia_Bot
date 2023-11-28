from nonebot import require,on_message
from nonebot.adapters import Event
from nonebot.rule import Rule
from nonebot.adapters.red import PrivateMessageEvent

from ..Index_user_management import *

import re,json,time

keys = [{"3652469329":"RvQdiRnJ3eosMBmL7NnL"},{"1847680031":"thyqbtp"}]
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
    if check_authentification(header["From"],header["Authentification"]) and header["From"]==event.get_user_id() and header["To"]=="3046199658":
        if time.time()-footer["timestamp"]<=5000:
            if Action=="addMoney":
                u = Group(content["group_id"]).find_user_by_qid(content["user_id"])
                u.add_money(content["money"])
                await onQBTP.finish('QBTP="header":{"From":"3046199658","To":"{}","Content-Type":"JSON"},"body":{"content":{"group_id":{},"user_id":{},"user_money":{}}}}'.format(event.get_user_id(),content["group_id"],content["user_id"],u.money))
        else:await onQBTP.finish("时间超时！")
    else:await onQBTP.finish("鉴权失败！")

# generated_key = secrets.token_urlsafe(15)