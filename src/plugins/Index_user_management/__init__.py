from nonebot import on_command
from nonebot.adapters.red import MessageEvent,Message,MessageSegment
from nonebot.params import CommandArg

from .models import *

new_user = on_command("注册",priority=10,block=True)
@new_user.handle()
async def newUser(event:MessageEvent,args: Message = CommandArg()):
    nickname = args.extract_plain_text()
    if nickname=='':
        nickname = event.sendNickName
    g = Group(event.scene)
    g.new_user(event.get_user_id(),nickname)
    user = g.findUser(event.get_user_id())
    await new_user.finish(MessageSegment.at(event.get_user_id())+f"\n新建用户成功，欢迎{user.nickname}\n使用指令“修改昵称”修改名称\n当前存款{user.money}火币")

change_nickname = on_command("修改昵称",priority=10,block=True)
@change_nickname.handle()
async def changeNickname(event:MessageEvent,args: Message = CommandArg()):
    nickname = args.extract_plain_text()
    if nickname=='':
        await change_nickname.finish("未输入昵称哦")
    g = Group(event.scene)
    g.find_user(event.get_user_id()).rename(nickname)
    await change_nickname.finish(f"修改昵称成功！\n当前昵称：{nickname}")

ask_user = on_command("查询",priority=10,block=True)
@ask_user.handle()
async def askUser(event:MessageEvent):
    u = Group(event.scene).find_user(event.get_user_id())
    await change_nickname.finish(MessageSegment.at(event.get_user_id())+f"\n您好！{u.nickname}\n当前火币：{u.money}")