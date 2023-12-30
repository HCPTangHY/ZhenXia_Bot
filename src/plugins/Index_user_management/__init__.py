from nonebot import on_command
from nonebot.adapters import Event
from nonebot.adapters.red import MessageEvent,Message,MessageSegment
from nonebot.params import CommandArg

from .models import *

import re

newUser = on_command("注册",priority=10,block=True)
@newUser.handle()
async def new_user(event:MessageEvent,args: Message = CommandArg()):
    nickname = args.extract_plain_text()
    if nickname=='':
        nickname = event.sendNickName
    User.new_user(event.get_user_id(),event.scene,nickname)
    user = User.find_user_by_qid(event.get_user_id())
    await newUser.finish(MessageSegment.at(event.get_user_id())+f"\n新建用户成功，欢迎{user.nickname}\n使用指令“修改昵称”修改名称\n当前存款{user.money}火币")

changeNickname = on_command("修改昵称",priority=10,block=True)
@changeNickname.handle()
async def change_nickname(event:MessageEvent,args: Message = CommandArg()):
    nickname = args.extract_plain_text()
    if nickname=='':
        await changeNickname.finish("未输入昵称哦")
    User.find_user_by_qid(event.get_user_id()).rename(nickname)
    await changeNickname.finish(f"修改昵称成功！\n当前昵称：{nickname}")

askUser = on_command("查询",priority=10,block=True)
@askUser.handle()
async def ask_user(event:MessageEvent):
    u = User.find_user_by_qid(event.get_user_id())
    if u=='NoUser':
        if event.scene not in u.groups:u.add_group(event.scene)
        await askUser.finish("你还没注册呢！发送注册来让小霞认识一下你吧！")
    await askUser.finish(MessageSegment.at(event.get_user_id())+f"\n您好！{u.nickname}\n当前火币：{round(u.money,2)}")

sendMoney = on_command("汇款",priority=10,block=True)
@sendMoney.handle()
async def send_money(event:Event,args: Message = CommandArg()):
    u = User.find_user_by_qid(event.get_user_id())
    target = re.search(r"(?<='user_id': ').*?(?=')",str(event.get_message())).group()
    target = User.find_user_by_qid(target)
    num = float(args.extract_plain_text())
    if u=='NoUser':
        await sendMoney.finish("你还没注册呢！发送注册来让小霞认识一下你吧！")
    else:
        if num<=0:
            await sendMoney.finish(f"{num}？！你在汇什么啊！")
        if target=='NoUser':
            await sendMoney.finish(f"对方还没注册呢！让Ta发送注册来让小霞认识一下吧！")
        if target.uid==u.uid:
            await sendMoney.finish("你是？")
        else:
            if u.money<num:
                await sendMoney.finish(f"你没有{num}汇给{target.nickname}！")
            else:
                u.add_money(-num)
                target.add_money(num)
                await sendMoney.finish(f"火币到账！你汇了{num}给{target.nickname}！")

askRichRank = on_command("财富排行",priority=10,block=True)
@askRichRank.handle()
async def ask_rich_rank(event:Event):
    gid = event.get_session_id().split("_")[0]
    us = User.rich_rank(gid)
    text = ''
    for i in range(len(us)):
        if i>9:break
        if us[i].nickname!='':text += f'~{i+1}~ {us[i].nickname} ${round(us[i].money)}\n'
        else: text += f'~{i+1}~ '+MessageSegment.at(us[i].qid)+f' ${round(us[i].money)}\n'
    await askRichRank.finish("=== 本群财富排行 ===\n"+text)