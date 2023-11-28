from nonebot import require
from nonebot import on_command,on_message
from nonebot.adapters import Event,Message
from nonebot.params import CommandArg
from nonebot.adapters.red import MessageSegment
from asyncio import TimerHandle

require("Index_user_management")
require("wordle_zhenxia")

from ..Index_user_management import *
from .models import *
import re,datetime,random

def std_position_out(gid,u:ncUser):
    ptext = u.position.name+"\n"+u.position.desc+random.choice(u.position.diffDesc)+"\n\n你可以选择：\n"
    for i in range(len(u.position.choice)):
        ptext += f"[{i}] {u.position.choice[i].split('|')[0]}\n"
    return ptext

askWhere = on_command("查询位置",aliases={"position"},priority=10,block=True)
@askWhere.handle()
async def ask_where(event:Event):
    gid = event.get_session_id().split("_")[0]
    u = ncGroup(gid).find_user(event.get_user_id())
    if not u:
        await askWhere.finish("你还没注册呢！发送注册来让小霞认识一下你吧！")
    else:
        await askWhere.finish(MessageSegment.at(event.get_user_id())+"\n你在 "+std_position_out(gid,u))

choiceAction = on_command("选择",aliases={"choice"},priority=10,block=True)
@choiceAction.handle()
async def choice_action(event:Event,args:Message = CommandArg()):
    gid = event.get_session_id().split("_")[0]
    u = ncGroup(gid).find_user(event.get_user_id())
    targetIndex = args.extract_plain_text()
    if not u:
        await choiceAction.finish("你还没注册呢！发送注册来让小霞认识一下你吧！")
    else:
        targetCommand = u.position.choice[int(targetIndex)].split("|")[1].split(":")
        command = targetCommand[0]
        if len(targetCommand)==1:
            returnText = getattr(u,command)
        else:
            parse = targetCommand[1]
            returnText = getattr(u,command)(parse)
        await choiceAction.finish(MessageSegment.at(event.get_user_id())+f"\n{returnText}\n"+"你在 "+std_position_out(gid,u))

askUser = on_command("查询",priority=9,block=True)
@askUser.handle()
async def ask_user(event:MessageEvent):
    u = Group(event.scene).find_user_by_qid(event.get_user_id())
    if not u:
        await choiceAction.finish("你还没注册呢！发送注册来让小霞认识一下你吧！")
    ncU = ncGroup(event.scene).find_user(event.get_user_id())
    text = '左手武器：'+ncU.leftHand+"\n右手武器："+ncU.rightHand+"\n"
    for i in range(len(ncU.inventory)):
        text += f"[{i}] {ncU.inventory[i]}\n"
    await askUser.finish(MessageSegment.at(event.get_user_id())+f"\n您好！{u.nickname}\n当前火币：{round(u.money,2)}\n"+text+"输入查看 编号 来查看物品")

readInventory = on_command("查看",aliases={"lookI"},priority=10,block=True)
@readInventory.handle()
async def read_inventory(event:Event,args:Message = CommandArg()):
    gid = event.get_session_id().split("_")[0]
    u = ncGroup(gid).find_user(event.get_user_id())
    targetIndex = args.extract_plain_text()
    if not u:
        await readInventory.finish("你还没注册呢！发送注册来让小霞认识一下你吧！")
    else:
        if targetIndex=="左手":itemName=u.leftHand
        elif targetIndex=="右手":itemName=u.rightHand
        else:itemName = u.inventory[int(targetIndex)]
        item = Item.search_by_name(gid,itemName)
        await readInventory.finish(MessageSegment.at(event.get_user_id())+f"\n~{item.name}~\n\n{item.desc}")