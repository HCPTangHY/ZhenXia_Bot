from nonebot import on_command
from nonebot.adapters import Event,Message
from nonebot.params import CommandArg
from nonebot.adapters.red import MessageSegment,Bot

import os,traceback

from .models import *

askMap = on_command("查询星图",aliases={"askMap"},priority=10,block=True)
@askMap.handle()
async def ask_map(bot:Bot):
    try:
        BoF_init()
        if os.path.exists('data/BoFMap.png'):
            await askMap.finish(MessageSegment.image('data/BoFMap.png'))
        Star.draw_map()
        await askMap.finish(MessageSegment.image('data/BoFMap.png'))
    except Exception as e:await askMap.finish(e)
reMap = on_command("reMap",priority=1,block=True)
@reMap.handle()
async def r_m():
    try:
        Star.draw_map()
        await askMap.finish(MessageSegment.image('data/BoFMap.png'))
    except Exception as e:await askMap.finish(e)

activeC = None
askCountry = on_command("askCountry",priority=10,block=True)
@askCountry.handle()
async def ask_c(args:Message = CommandArg()):
    global activeC
    activeC = Country.search_by_tag(args.extract_plain_text())
    print(activeC)
    await askCountry.finish(f"{activeC.tag}\n{activeC.name}\n{activeC.color}")
updateCountry = on_command("updateCountry",priority=10,block=True)
@updateCountry.handle()
async def update_c(args:Message = CommandArg()):
    args = args.extract_plain_text().split(',')
    if args[0]=='name':activeC.name = args[1]
    if args[0]=='color':activeC.color = args[1]
    activeC.update()
    await updateCountry.finish(f"{activeC.tag}\n{activeC.name}\n{activeC.color}")
newCountry = on_command("newCountry",priority=10,block=True)
@newCountry.handle()
async def new_c(args:Message = CommandArg()):
    Country.new_country(args.extract_plain_text())
    global activeC
    activeC = Country.search_by_tag(args.extract_plain_text())
    await newCountry.finish(f"{activeC.tag}\n{activeC.name}\n{activeC.color}")
activeS = None
askStar = on_command("askStar",priority=10,block=True)
@askStar.handle()
async def ask_s(args:Message = CommandArg()):
    global activeS
    activeS = Star.search_by_id(args.extract_plain_text())
    await askStar.finish(f"{activeS.id}\n{activeS.name}\n{activeS.owner}\n{activeS.controller}")
updateStar = on_command("updateStar",priority=10,block=True)
@updateStar.handle()
async def update_s(args:Message = CommandArg()):
    args = args.extract_plain_text().split(',')
    if args[0]=='name':activeS.name = args[1]
    if args[0]=='owner':activeS.owner = args[1];activeS.controller = args[1]
    if args[0]=='controller':activeS.controller = args[1]
    activeS.update()
    await updateStar.finish(f"{activeS.id}\n{activeS.name}\n{activeS.owner}\n{activeS.controller}")
