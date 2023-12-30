import asyncio
from asyncio import TimerHandle
from typing import Dict
from nonebot import require,on_message
from nonebot.rule import Rule
from nonebot.matcher import Matcher
from nonebot.adapters import Event
from nonebot.params import EventPlainText

require("Index_user_management")

from .model import *
from .utils import *
from ..Index_user_management import *

import re,random

hangmans = []
timers: Dict[str, TimerHandle] = {}
class Enermy():
    def __init__(self,type,participate:dict,object:Hangman) -> None:
        self.type = type
        self.participate:dict = participate
        self.object = object
async def stop_game(matcher: Matcher, event:Event,session: str,user:User):
    timers.pop(session, None)
    gid = event.get_session_id().split("_")[0]
    for i in range(len(hangman)):
        if hangmans[i]['session']==session:
            e:Enermy = hangmans[i]['enermy']
            hangmans.pop(i)
            msg = "猜单词超时，游戏结束！"
            msg += f"\n{e.object.result}"
            await matcher.finish(msg)

def set_timeout(matcher: Matcher,event, session: str, user:User,timeout: float = 300):
    timer = timers.get(session, None)
    if timer:
        timer.cancel()
    loop = asyncio.get_running_loop()
    timer = loop.call_later(
        timeout, lambda: asyncio.ensure_future(stop_game(matcher,event,session,user))
    )
    timers[session] = timer
def hangman_battle(matcher:Matcher,event:Event,user:User,enermy:Enermy):
    set_timeout(matcher,event,event.get_session_id(),user)
    for h in hangmans:
        if h['enermy']==enermy:
            letterOrWord = event.get_plaintext()
            enermy.participate[user.qid] = enermy.participate.get(user.qid,0)+1
            if '投降'==letterOrWord:
                return GuessResult.LOSS,enermy
            state = enermy.object.guess(letterOrWord)
            hangmans[hangmans.index(h)]['enermy'] = enermy
    return state,enermy
def game_running(event: Event) -> bool:
    for hm in hangmans:
        if hm['session'].split("_")[0]==event.get_session_id().split("_")[0]:
            return True
    return False
def get_word_input(msg: str = EventPlainText()) -> bool:
    if re.fullmatch(r"[a-zA-Z]", msg) or re.fullmatch(r"^[a-zA-Z]{3,8}$", msg) or msg=='投降':
        return True
    return False

hangman = on_command("hangman",aliases={"吊人"},priority=12,block=True)
@hangman.handle()
async def hangman_action(event:Event):
    gid = event.get_session_id().split("_")[0]
    u = User.find_user_by_qid(event.get_user_id())
    if not u:
        await hangman.finish("你还没注册呢！发送注册来让小霞认识一下你吧！")
    else:
        for h in hangmans:
            if h['session'].split("_")[0]==gid:
                await hangman.finish("有一个Hangman在进行哦")
        if random.random()<=0.2:
            word,meaning = random_word("CET6",random.choice([3,4,4,5,5,5,6,6,7]))
            e = Enermy('精英',{},Hangman(word,meaning))
            hangmans.append({'session':event.get_session_id(),'enermy':e,'from':'explore'})
            await hangman.finish(MessageSegment.image(e.object.draw())+f"\n你遇到了精英Hangman！\n你有{e.object.chance}次机会猜出单词，单词长度为{e.object.length}，请发送字母或单词")
        else:
            word,meaning = random_word("CET4",random.choice([5,5,5,5,6]))
            e = Enermy('野生',{},Hangman(word,meaning))
            hangmans.append({'session':event.get_session_id(),'enermy':e,'from':'explore'})
            await hangman.finish(MessageSegment.image(e.object.draw())+f"\n你遇到了野生Hangman！\n你有{e.object.chance}次机会猜出单词，单词长度为{e.object.length}，请发送字母或单词")
lwMatcher = on_message(Rule(game_running) & get_word_input, block=True, priority=12)
@lwMatcher.handle()
async def _(event: Event):
    gid = event.get_session_id().split("_")[0]
    u = User.find_user_by_qid(event.get_user_id())
    if not u:
        await lwMatcher.finish("你还没注册呢！发送注册来让小霞认识一下你吧！")
    else:
        for w in hangmans:
            gid = event.get_session_id().split("_")[0]
            if gid==w['session'].split("_")[0]:
                user = User.find_user_by_qid(event.get_user_id())
                state,e = hangman_battle(lwMatcher,event,user,w['enermy'])
                if state==GuessResult.WIN or state==GuessResult.LOSS:
                    hangmans[hangmans.index(w)]['enermy'] = e
                    hangmans.pop(hangmans.index(w))
                    if state==GuessResult.LOSS:
                        await lwMatcher.finish(MessageSegment.image(e.object.draw())+f'\n{e.object.result}\n')
                    elif state==GuessResult.WIN:
                        moneyDesc = None
                        for key,val in e.participate.items():
                            money = val*0.8
                            moneyDesc += MessageSegment.at(key)+f" 获得{round(money,2)}火币!\n"
                            User.find_user_by_qid(key).add_money(money)
                        await lwMatcher.finish(MessageSegment.image(e.object.draw())+f'\n{e.object.result}\n战斗胜利！\n'+moneyDesc)
                else:
                    await lwMatcher.send(MessageSegment.image(e.object.draw()))
                break