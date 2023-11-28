from nonebot import on_message,on_command
from nonebot.adapters import Event,Message
from nonebot.params import CommandArg
from nonebot.rule import Rule
import os,pandas,random,re

class Food:
    def __init__(self,data:list[str]) -> None:
        self.name = data[0]
        self.recipe = data[1].split("、")
        if isinstance(data[4],str):self.tag = data[4].split("、")
        else:self.tag = [data[4]]
        self.methods = data[5]
        self.tools = data[6].split("、")
foods = []
def read_recipe():
    recipe = pandas.read_csv(os.path.dirname(__file__)+"/recipe.csv",encoding="utf-8",header=0)
    for f in recipe.values:
        foods.append(Food(f.tolist()))

read_recipe()
def check_eat_what(event:Event):
    return "吃什么" in event.get_plaintext()
eatWhat = on_message(rule=Rule(check_eat_what),priority=10,block=True)
@eatWhat.handle()
async def eat_what(event:Event):
    food = random.choice(foods).name
    await eatWhat.finish(food+"！")
eatSome = on_command("吃点",priority=12,block=True)
@eatSome.handle()
async def eat_some(args: Message = CommandArg()):
    tag = args.extract_plain_text()
    fs = []
    for f in foods:
        if tag in f.tag:fs.append(f)
    if len(fs)==0:await eatSome.finish("没有"+tag+"！")
    else:
        food = random.choice(fs).name
        await eatSome.finish(food+"！")
