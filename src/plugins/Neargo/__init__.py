from nonebot import require
from nonebot import on_command,on_message
from nonebot.adapters import Event,Message
from nonebot.params import CommandArg
from nonebot.permission import SUPERUSER
from nonebot.adapters.red import Bot,MessageEvent,MessageSegment
from nonebot.adapters.red.bot import ForwardNode
from asyncio import TimerHandle

require("Index_user_management")
require("wordle_zhenxia")

from ..Index_user_management import *
from .models import *
from .battle import *
import re,datetime,random
from PIL import Image,ImageFont,ImageDraw2

def std_position_out(u:ncUser):
    users = ''
    for p in u.position.player:
        if p.uid==u.uid:continue
        if p.nickname!='':users += f'{p.nickname} '
        else: users += MessageSegment.at(p.qid)+' '
    if users!='':users+='在这里\n'
    ptext = u.position.name+"\n"+u.position.desc+"\n"+random.choice(u.position.diffDesc)+"\n"+users+"\n你可以选择：\n"
    for i in range(len(u.position.choice)):
        ptext += f"[{i}] {u.position.choice[i].split('|')[0]}\n"
    return ptext

askWhere = on_command("查询位置",aliases={"position"},priority=10,block=True)
@askWhere.handle()
async def ask_where(event:Event):
    gid = event.get_session_id().split("_")[0]
    u = ncUser.find_user(event.get_user_id())
    if u=='NoUser':
        await askWhere.finish("你还没注册呢！发送注册来让小霞认识一下你吧！")
    else:
        await askWhere.finish(MessageSegment.at(event.get_user_id())+"\n你在 "+std_position_out(u))

choiceAction = on_command("选择",aliases={"choice"},priority=10,block=True)
@choiceAction.handle()
async def choice_action(event:Event,args:Message = CommandArg()):
    gid = event.get_session_id().split("_")[0]
    u = ncUser.find_user(event.get_user_id())
    targetIndex = args.extract_plain_text().split(' ')
    if u=='NoUser':
        await choiceAction.finish("你还没注册呢！发送注册来让小霞认识一下你吧！")
    else:
        targetCommand = u.position.choice[int(targetIndex[0])].split("|")[1].split(":")
        command = targetCommand[0]
        if len(targetCommand)==1:
            if ('rename' in command) or ('redesc' in command):
                returnText=getattr(u,command)(targetIndex[1])
            else:returnText = getattr(u,command)()
        else:
            parses = targetCommand[1].split(";")
            if len(parses)==1:
                returnText=getattr(u,command)(parses[0])
            elif len(parses)==2:returnText=getattr(u,command)(parses[0],parses[1])
        await choiceAction.finish(MessageSegment.at(event.get_user_id())+f"\n{returnText}\n"+"你在 "+std_position_out(u))

askUser = on_command("查询背包",priority=9,block=True)
@askUser.handle()
async def ask_user(event:MessageEvent):
    gid = event.get_session_id().split("_")[0]
    u = User.find_user_by_qid(event.get_user_id())
    if u=='NoUser':
        await choiceAction.finish("你还没注册呢！发送注册来让小霞认识一下你吧！")
    ncU = ncUser.find_user(event.get_user_id())
    ncU.open_inventory()
    await askUser.finish(MessageSegment.at(event.get_user_id())+f"\n您好！{u.nickname}\n{std_position_out(ncU)}")

lootUser = on_command("打劫",aliases={'loot'},priority=10,block=True)
@lootUser.handle()
async def loot_user(event:MessageEvent,bot:Bot):
    gid = event.get_session_id().split("_")[0]
    u = ncUser.find_user(event.get_user_id())
    target = re.search(r"(?<='user_id': ').*?(?=')",str(event.get_message())).group()
    target = ncUser.find_user(target)
    if u=='NoUser':
        await lootUser.finish("你还没注册呢！发送注册来让小霞认识一下你吧！")
    if target=='NoUser':
        await lootUser.finish("对方还没注册呢！让Ta发送注册来让小霞认识一下吧！")
    atPosition = False
    for user in u.position.player:
        if user.uid==target.uid:atPosition=True;break
    if not atPosition:await lootUser.finish("你们不在同一个地方！没法打劫Ta！")
    if target.uid==u.uid:await lootUser.finish("你是？")
    if target.HP<=30:
        if random.random()>0.25:await lootUser.finish("Ta逃走了！")
    b = Battle(u,target)
    b.fight()
    maxLenth = len(b.report[0])
    for r in b.report:
        if len(r)>maxLenth:maxLenth=len(r)
    font = ImageFont.truetype("simhei",15,encoding='utf-8')
    img = Image.new("RGBA",(17*maxLenth,17*len(b.report)), (255,255,255))
    draw = ImageDraw.Draw(img)
    draw.text((5,5),"\n".join(b.report),(0,0,0),font=font)
    img.save('data/Neargo/battle.png')
    u = ncUser.find_user(event.get_user_id())
    target = re.search(r"(?<='user_id': ').*?(?=')",str(event.get_message())).group()
    target = ncUser.find_user(target)
    if u.HP<=0:
        await bot.send_group_message(gid,MessageSegment.at(event.get_user_id())+u.rescue()+"\n"+std_position_out(u))
    if target.HP<=0:
        targetQ = re.search(r"(?<='user_id': ').*?(?=')",str(event.get_message())).group()
        await bot.send_group_message(gid,MessageSegment.at(targetQ)+target.rescue()+"\n"+std_position_out(target))
    await lootUser.finish(MessageSegment.image('data/Neargo/battle.png'))

emergencyRelease = on_command("紧急脱离",aliases={'emergencyRelease'},priority=10,block=True)
@emergencyRelease.handle()
async def e_release(event:Event):
    u = User.find_user_by_qid(event.get_user_id())
    if u=='NoUser':
        await emergencyRelease.finish("你还没注册呢！发送注册来让小霞认识一下你吧！")
    ncU = ncUser.find_user(event.get_user_id())
    if ncU.position.id!=0:await emergencyRelease.finish("你不需要脱离哦")
    conn = sqlite3.connect(f"data/INDEX/Neargo.db")
    cur = conn.cursor()
    data = cur.execute(f"select position from user where uid='{u.uid}';").fetchone()[0]
    fromP = data.split("/")[-1]
    cur.execute(f"UPDATE user SET position='{fromP}' where uid='{u.uid}';")
    conn.commit()
    conn.close()
    ncU = ncUser.find_user(event.get_user_id())
    await emergencyRelease.finish(MessageSegment.at(event.get_user_id())+"脱离成功！\n你在 "+std_position_out(ncU))


activePosition = None
askPositionByid = on_command("askPosition",priority=9,block=True)
@askPositionByid.handle()
async def ask_item_by_id(event:Event,args:Message = CommandArg()):
    if event.get_user_id()!="1847680031":await askPositionByid.finish()
    u = User.find_user_by_qid(event.get_user_id())
    global activePosition
    if not activePosition:activePosition = Position.search_by_id(args.extract_plain_text(),u.uid)
    else:
        if activePosition.id!=args:activePosition = Position.search_by_id(args.extract_plain_text(),u.uid)
    await askPositionByid.finish(f"ID：{activePosition.id}\nname：{activePosition.name}\ndesc：{activePosition.desc}|{' '.join(activePosition.diffDesc)}\nchoice：{' '.join(activePosition.choice)}\nowner：{activePosition.owner}")

changeToCsv = on_command("changeToCsv",priority=9,block=True)
@changeToCsv.handle()
async def ask_item_by_id(event:Event,args:Message = CommandArg()):
    if event.get_user_id()!="1847680031":await changeToCsv.finish()
    global activePosition
    if not activePosition:changeToCsv.finish()
    await changeToCsv.finish(f"{activePosition.id},{activePosition.name},{activePosition.desc}|{' '.join(activePosition.diffDesc)},{' '.join(activePosition.choice)},{activePosition.owner}")

updatePosition = on_command("updatePosition",priority=9,block=True)
@updatePosition.handle()
async def update_item(event:Event,args:Message = CommandArg()):
    if event.get_user_id()!="1847680031":await updatePosition.finish()
    global activePosition
    args = args.extract_plain_text().split(',')
    if args[0]=='name':activePosition.name = args[1]
    if args[0]=='desc':activePosition.desc = args[1]
    if args[0]=='descDiff':activePosition.diffDesc = args[1].split(" ")
    if args[0]=='choice':activePosition.choice = args[1].split(" ")
    if args[0]=='owner':activePosition.owner = args[1]
    activePosition.update()
    await updatePosition.finish(f"FINISH!\nID：{activePosition.id}\nname：{activePosition.name}\ndesc：{activePosition.desc}|{' '.join(activePosition.diffDesc)}\nchoice：{' '.join(activePosition.choice)}\nowner：{activePosition.owner}")

newPosition = on_command("newPosition",priority=9,block=True)
@newPosition.handle()
async def new_positon(event:Event,args:Message = CommandArg()):
    if event.get_user_id()!="1847680031":await newPosition.finish()
    global activePosition
    args = args.extract_plain_text()
    u = User.find_user_by_qid(event.get_user_id())
    try:Position.new_position(args,'','','','city')
    except:pass
    activePosition = Position.search_by_id(args,u.uid)
    await newPosition.finish(f"FINISH!\nID：{activePosition.id}\nname：{activePosition.name}\ndesc：{activePosition.desc}|{' '.join(activePosition.diffDesc)}\nchoice：{' '.join(activePosition.choice)}\nowner：{activePosition.owner}")

activeItem = None
askItemByid = on_command("askItem",priority=9,block=True)
@askItemByid.handle()
async def ask_item_by_id(event:Event,args:Message = CommandArg()):
    if event.get_user_id()!="1847680031":await askItemByid.finish()
    u = User.find_user_by_qid(event.get_user_id())
    global activeItem
    if not activeItem:activeItem = Item.search_by_id(args)
    else:
        if activeItem.id!=args:activeItem = Item.search_by_id(args)
    await askItemByid.finish(f"ID：{activeItem.id}\nname：{activeItem.name}-{'&'.join(activeItem.tags)}\ndesc：{activeItem.desc}\nchoice：{' '.join(activeItem.choice)}/{activeItem.battleSkill}\nformula：{activeItem.formula}")

changeToCsv = on_command("changeToCsv",priority=9,block=True)
@changeToCsv.handle()
async def ask_item_by_id(event:Event,args:Message = CommandArg()):
    if event.get_user_id()!="1847680031":await changeToCsv.finish()
    global activeItem
    if not activeItem:changeToCsv.finish()
    await changeToCsv.finish(f"{activeItem.id},{activeItem.name}-{'&'.join(activeItem.tags)},{activeItem.desc},{' '.join(activeItem.choice)}/{activeItem.battleSkill},{activeItem.formula}")

updateItem = on_command("updateItem",priority=9,block=True)
@updateItem.handle()
async def update_item(event:Event,args:Message = CommandArg()):
    if event.get_user_id()!="1847680031":await updateItem.finish()
    global activeItem
    args = args.extract_plain_text().split(',')
    if args[0]=='name':activeItem.name = args[1]
    if args[0]=='tags':activeItem.tags = args[1].split("&")
    if args[0]=='desc':activeItem.desc = args[1]
    if args[0]=='choice':activeItem.choice = args[1].split(" ")
    if args[0]=='battleSkill':activeItem.battleSkill = args[1]
    if args[0]=='formula':activeItem.formula = args[1]
    activeItem.update()
    await updateItem.finish(f"FINISH!\nID：{activeItem.id}\nname：{activeItem.name}-{'&'.join(activeItem.tags)}\ndesc：{activeItem.desc}\nchoice：{' '.join(activeItem.choice)}/{activeItem.battleSkill}\nformula：{activeItem.formula}")

newItem = on_command("newItem",priority=9,block=True)
@newItem.handle()
async def new_item(event:Event,args:Message = CommandArg()):
    if event.get_user_id()!="1847680031":await newItem.finish()
    global activeItem
    args = args.extract_plain_text()
    u = User.find_user_by_qid(event.get_user_id())
    try:Item.new_item(args,'','','','')
    except:pass
    activeItem = Item.search_by_id(args)
    await newItem.finish(f"FINISH!\nID：{activeItem.id}\nname：{activeItem.name}-{'&'.join(activeItem.tags)}\ndesc：{activeItem.desc}\nchoice：{' '.join(activeItem.choice)}/{activeItem.battleSkill}\nformula：{activeItem.formula}")