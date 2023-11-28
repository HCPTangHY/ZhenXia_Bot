import asyncio
from asyncio import TimerHandle
from typing import Dict
from nonebot.matcher import Matcher
from nonebot.adapters import Event
import re

from .models import *
from ..wordle_zhenxia import Wordle,GuessResult

wordles = []
timers: Dict[str, TimerHandle] = {}
async def stop_game(matcher: Matcher, event:Event,session: str,user:monoUser):
    timers.pop(session, None)
    for i in range(len(wordles)):
        if wordles[i]['session']==session:
            e:Enermy = wordles[i]['enermy']
            wordles.pop(i)
            msg = "猜单词超时，游戏结束！"
            if len(e.object.guessed_words) >= 1:
                user.add_money(-e.object.length+2)
                msg += f"\n{e.object.result}\n你被{e.type}沃兜抢走了{e.object.length-2}火币！\n"+MessageSegment.at(event.get_user_id())
            await matcher.finish(msg)

def set_timeout(matcher: Matcher,event, session: str, user:monoUser,timeout: float = 300):
    timer = timers.get(session, None)
    if timer:
        timer.cancel()
    loop = asyncio.get_running_loop()
    timer = loop.call_later(
        timeout, lambda: asyncio.ensure_future(stop_game(matcher,event,session,user))
    )
    timers[session] = timer
def wordle_battle(matcher:Matcher,event:Event,user:monoUser,enermy:Enermy):
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
            state = enermy.object.guess(word)
            wordles[wordles.index(w)]['enermy'] = enermy
    return state,enermy