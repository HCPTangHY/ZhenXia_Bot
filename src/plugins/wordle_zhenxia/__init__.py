import asyncio
from asyncio import TimerHandle
from typing import Dict
from nonebot import require,on_message
from nonebot.rule import Rule
from nonebot.matcher import Matcher
from nonebot.adapters import Event
from nonebot.params import EventPlainText

require("Index_user_management")

from nonebot_plugin_wordle import Wordle,GuessResult,random_word
from ..Index_user_management import *

import re,random

wordles = []
timers: Dict[str, TimerHandle] = {}
class Enermy():
    def __init__(self,type,participate:dict,object:Wordle) -> None:
        self.type = type
        self.participate:dict = participate
        self.object = object
        self.wordState = []
        for w in self.object.word:
            self.wordState.append(0)
async def stop_game(matcher: Matcher, event:Event,session: str,user:User):
    timers.pop(session, None)
    gid = event.get_session_id().split("_")[0]
    for i in range(len(wordles)):
        if wordles[i]['session']==session:
            e:Enermy = wordles[i]['enermy']
            wordles.pop(i)
            msg = "猜单词超时，游戏结束！"
            moneyDesc = None
            if len(e.object.guessed_words) >= 1:
                for key,val in e.participate.items():
                    money = val*0.125
                    moneyDesc += MessageSegment.at(key)+f" 获得{-round(money,2)}火币!\n"
                    User.find_user_by_qid(key).add_money(money)
                msg += f"\n{e.object.result}"
            await matcher.finish(msg+"\n"+moneyDesc)

def set_timeout(matcher: Matcher,event, session: str, user:User,timeout: float = 300):
    timer = timers.get(session, None)
    if timer:
        timer.cancel()
    loop = asyncio.get_running_loop()
    timer = loop.call_later(
        timeout, lambda: asyncio.ensure_future(stop_game(matcher,event,session,user))
    )
    timers[session] = timer
def wordle_battle(matcher:Matcher,event:Event,user:User,enermy:Enermy):
    set_timeout(matcher,event,event.get_session_id(),user)
    for w in wordles:
        if w['enermy']==enermy:
            word = event.get_plaintext()
            if '提示'==word:
                hint = enermy.object.get_hint()
                if not hint.replace("*", ""):
                    return 'noHint',enermy
                else: return 'hint',enermy
            elif '投降'==word:
                return GuessResult.LOSS,enermy
            if len(word) != enermy.object.length:
                return 'noLength',enermy
            for i in range(len(enermy.object.word)):
                if enermy.object.word[i]==word[i]:
                    if enermy.wordState[i]==0:enermy.participate[user.qid] = enermy.participate.get(user.qid,0)+2
                    elif enermy.wordState[i]==1:enermy.participate[user.qid] = enermy.participate.get(user.qid,0)+0.5
                    enermy.wordState[i] = 2
                elif enermy.object.word[i] in word:
                    if enermy.wordState[i]==0:
                        enermy.participate[user.qid] = enermy.participate.get(user.qid,0)+0.5
                        enermy.wordState[i] = 1
            state = enermy.object.guess(word)
            wordles[wordles.index(w)]['enermy'] = enermy
    return state,enermy
def game_running(event: Event) -> bool:
    for wd in wordles:
        if wd['session'].split("_")[0]==event.get_session_id().split("_")[0]:
            return True
    return False
def get_word_input(msg: str = EventPlainText()) -> bool:
    if re.fullmatch(r"^[a-zA-Z]{3,8}$", msg) or msg=='投降' or msg=='提示':
        return True
    return False

wordle = on_command("wordle",aliases={"沃兜"},priority=12,block=True)
@wordle.handle()
async def wordle_action(event:Event):
    gid = event.get_session_id().split("_")[0]
    u = User.find_user_by_qid(event.get_user_id())
    if not u:
        await wordle.finish("你还没注册呢！发送注册来让小霞认识一下你吧！")
    else:
        for w in wordles:
            if w['session'].split("_")[0]==gid:
                await wordle.finish("有一个沃兜在进行哦")
        if random.random()<=0.2:
            word,meaning = random_word("CET6",random.choice([3,4,4,5,5,5,6,6,7]))
            e = Enermy('精英',{},Wordle(word,meaning))
            wordles.append({'session':event.get_session_id(),'enermy':e,'from':'explore'})
            await wordle.finish(MessageSegment.image(e.object.draw())+f"\n你遇到了精英沃兜！\n你有{e.object.rows}次机会猜出单词，单词长度为{e.object.length}，请发送单词")
        else:
            word,meaning = random_word("CET4",random.choice([5,5,5,5,6]))
            e = Enermy('野生',{},Wordle(word,meaning))
            wordles.append({'session':event.get_session_id(),'enermy':e,'from':'explore'})
            await wordle.finish(MessageSegment.image(e.object.draw())+f"\n你遇到了野生沃兜！\n你有{e.object.rows}次机会猜出单词，单词长度为{e.object.length}，请发送单词")
wordMatcher = on_message(Rule(game_running) & get_word_input, block=True, priority=12)
@wordMatcher.handle()
async def _(event: Event):
    gid = event.get_session_id().split("_")[0]
    u = User.find_user_by_qid(event.get_user_id())
    if not u:
        await wordle.finish("你还没注册呢！发送注册来让小霞认识一下你吧！")
    else:
        for w in wordles:
            gid = event.get_session_id().split("_")[0]
            if gid==w['session'].split("_")[0]:
                user = User.find_user_by_qid(event.get_user_id())
                state,e = wordle_battle(wordle,event,user,w['enermy'])
                if state==GuessResult.WIN or state==GuessResult.LOSS:
                    wordles[wordles.index(w)]['enermy'] = e
                    wordles.pop(wordles.index(w))
                    if state==GuessResult.LOSS:
                        moneyDesc = None
                        if len(e.participate)==0:moneyDesc=''
                        for key,val in e.participate.items():
                            money = val*0.125
                            moneyDesc += MessageSegment.at(key)+f" 获得{round(money,2)}火币!\n"
                            User.find_user_by_qid(key).add_money(money)
                        await wordle.finish(MessageSegment.image(e.object.draw())+f'\n{e.object.result}\n'+moneyDesc)
                    elif state==GuessResult.WIN:
                        moneyDesc = None
                        for key,val in e.participate.items():
                            money = val*0.8
                            moneyDesc += MessageSegment.at(key)+f" 获得{round(money,2)}火币!\n"
                            User.find_user_by_qid(key).add_money(money)
                        await wordle.finish(MessageSegment.image(e.object.draw())+f'\n{e.object.result}\n战斗胜利！\n'+moneyDesc)
                else:
                    if state=='noHint':
                        await wordle.send("\n你还没有猜对过一个字母哦~再猜猜吧~")
                    elif state=='hint':
                        hint = e.object.get_hint()
                        if user.money>=1:
                            await wordle.send(MessageSegment.image(e.object.draw_hint(hint)))
                        else:
                            await wordle.send('没有火币换取提示哦')
                    elif state=='noLength':
                        pass
                    elif state==GuessResult.DUPLICATE:
                        await wordle.send("你已经猜过这个单词了呢")
                    elif state==GuessResult.ILLEGAL:
                        await wordle.send(f"你确定 {event.get_plaintext()} 是一个合法的单词吗？")
                    else:
                        await wordle.send(MessageSegment.image(e.object.draw()))
                break