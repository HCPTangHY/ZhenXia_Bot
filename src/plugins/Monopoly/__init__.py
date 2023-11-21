from nonebot import require
from nonebot import on_command,on_message
from nonebot.adapters import Event,Message
from nonebot.params import CommandArg
from nonebot.adapters.red import MessageSegment
from asyncio import TimerHandle

require("Index_user_management")
require("wordle_zhenxia")

from ..Index_user_management import *
from ..wordle_zhenxia import *
from .models import *
from .battle import *
from .event import *
import re,datetime

moveAction = on_command("移动",aliases={"move"},priority=10,block=True)
@moveAction.handle()
async def move_action(event:Event):
    gid = event.get_session_id().split("_")[0]
    u = monoGroup(gid).find_user(event.get_user_id())
    if not u:
        await moveAction.finish("你还没注册呢！发送注册来让小霞认识一下你吧！")
    else:
        for e in events:
            if e['session']==event.get_session_id():await moveAction.finish("你有一个事件待处理！")
        p = u.move()
        if not p:
            await moveAction.finish("你没钱啦！赚点钱再移动吧")
        else:
            monoGroup(gid).draw_map()
            eventText=''
            if p.chunkType=='roadEvent':
                r = random.choice([1,2,2,3,3,3,3,4,4,4,4,4,5,5])
                if r==1:e = monoEventBlackMarket(event,u)
                elif r==2:e = monoEventSecretMoney(event,u)
                elif r==3:e = monoEventLewdWordle(event,u)
                else:e = monoEventLootWordle(event,u)
                events.append({"session":event.get_session_id(),"event":e})
                eventText = e.preText
            crime = ''
            if int(u.crime)==2:crime = '\n执法者觉得你很面熟……'
            elif int(u.crime)==3:crime = '\n执法者正盯着你'
            elif int(u.crime)==4:crime = '\n执法者正在找你！'
            elif int(u.crime)>=5:crime = '\n执法者决定逮捕你！'
            await moveAction.finish(f"你花了2火币来移动，来到了{p.chunkName}"+crime+MessageSegment.image('data/map.png')+eventText)

exitCity = on_command("出城",priority=10,block=True)
@exitCity.handle()
async def exit_city(event:Event):
    gid = event.get_session_id().split("_")[0]
    u = monoGroup(gid).find_user(event.get_user_id())
    if not u:
        await enterCity.finish("你还没注册呢！发送注册来让小霞认识一下你吧！")
    else:
        state = u.exit_room()
        if state:
            await exitCity.finish("你离开了城市，来到了郊外")
        else:
            await exitCity.finish("你不在大门口，没法出城！")

enterCity = on_command("进城",priority=10,block=True)
@enterCity.handle()
async def exit_city(event:Event):
    gid = event.get_session_id().split("_")[0]
    u = monoGroup(gid).find_user(event.get_user_id())
    if not u:
        await enterCity.finish("你还没注册呢！发送注册来让小霞认识一下你吧！")
    else:
        state = u.enter_room()
        if state:
            await enterCity.finish("你进入了城市，站在城门口")
        else:
            await enterCity.finish("你就在城里啊！")

askWhere = on_command("查询位置",aliases={"position"},priority=10,block=True)
@askWhere.handle()
async def ask_where(event:Event):
    gid = event.get_session_id().split("_")[0]
    u = monoGroup(gid).find_user(event.get_user_id())
    if not u:
        await askWhere.finish("你还没注册呢！发送注册来让小霞认识一下你吧！")
    else:
        monoGroup(gid).draw_map()
        crime = ''
        if int(u.crime)==2:crime = '\n执法者觉得你很面熟……'
        elif int(u.crime)==3:crime = '\n执法者正盯着你'
        elif int(u.crime)==4:crime = '\n执法者正在找你！'
        elif int(u.crime)>=5:crime = '\n执法者决定逮捕你！'
        await askWhere.finish(f"你正走在{u.position.chunkName}上"+crime+MessageSegment.image('data/map.png'))

lootUser = on_command("打劫",aliases={'loot'},priority=10,block=True)
@lootUser.handle()
async def loot_user(event:Event):
    gid = event.get_session_id().split("_")[0]
    u = monoGroup(gid).find_user(event.get_user_id())
    target = re.search(r"(?<='user_id': ').*?(?=')",str(event.get_message())).group()
    target = monoGroup(gid).find_user(target)
    if not u:
        await askWhere.finish("你还没注册呢！发送注册来让小霞认识一下你吧！")
    else:
        if u.position.cid != target.position.cid:
            await askWhere.finish("你们不在同一个地方！没法打劫Ta！")
        if not target:
            await askWhere.finish("对方还没注册呢！让Ta发送注册来让小霞认识一下吧！")
        else:
            if u.money<10:
                await moveAction.finish("你没钱啦！付不起打劫的成本！")
            else:
                dice1 = int(u.money/10)
                dice1 = random.randint(1,dice1*6)
                dice2 = int(target.money/10)
                dice2 = random.randint(1,dice2*6)
                if dice1>dice2:
                    l = random.randint(1,dice2)
                    u.add_money(l)
                    u.add_crime(l/10)
                    u.add_money(-5)
                    target.add_money(-l)
                    await askWhere.finish(f"你打劫了{target.nickname}！抢走了Ta的{l}火币！耗费了{5}火币！")
                elif dice1==dice2:
                    u.add_money(-10)
                    await askWhere.finish(f"你没能打劫{target.nickname}！耗费了{10}火币！")
                else:
                    l = random.randint(1,dice1)
                    u.add_money(-l)
                    target.add_money(l)
                    await askWhere.finish(f"你没能打劫{target.nickname}！被Ta抢走了{l}火币！")

sendMoney = on_command("汇款",priority=10,block=True)
@sendMoney.handle()
async def send_money(event:Event,args: Message = CommandArg()):
    gid = event.get_session_id().split("_")[0]
    u = monoGroup(gid).find_user(event.get_user_id())
    target = re.search(r"(?<='user_id': ').*?(?=')",str(event.get_message())).group()
    target = monoGroup(gid).find_user(target)
    num = float(args.extract_plain_text())
    if not u:
        await sendMoney.finish("你还没注册呢！发送注册来让小霞认识一下你吧！")
    else:
        if num<=0:
            await sendMoney.finish(f"{num}？！你在汇什么啊！")
        if not target:
            await sendMoney.finish("对方还没注册呢！让Ta发送注册来让小霞认识一下吧！")
        else:
            if u.money<num:
                await sendMoney.finish(f"你没有{num}汇给Ta！")
            else:
                u.add_money(-num)
                target.add_money(num)
                await sendMoney.finish(f"火币到账！你汇了{num}给Ta！")

explore = on_command("探索",aliases={'wordle'},priority=5,block=True)
@explore.handle()
async def Ex(event:Event):
    gid = event.get_session_id().split("_")[0]
    u = monoGroup(gid).find_user(event.get_user_id())
    if not u:
        await explore.finish("你还没注册呢！发送注册来让小霞认识一下你吧！")
    else:
        if u.position.chunkType!='gate':
            await explore.finish("在城里似乎没有什么可以探索的呢")
        else:
            for w in wordles:
                if w['session']==event.get_session_id():
                    await explore.finish("你有一个沃兜在进行哦")
            if random.random()<=0.2:
                word,meaning = random_word("CET6",random.randint(4,7))
                e = Enermy('精英',u,[],Wordle(word,meaning))
                wordles.append({'session':event.get_session_id(),'enermy':e,'from':'explore'})
                await explore.send(MessageSegment.image(e.object.draw())+MessageSegment.at(event.get_user_id())+f"\n你遇到了精英沃兜！\n你有{e.object.rows}次机会猜出单词，单词长度为{e.object.length}，请发送单词")
            else:
                word,meaning = random_word("CET4",random.choice([5,5,5,5,6]))
                e = Enermy('野生',u,[],Wordle(word,meaning))
                wordles.append({'session':event.get_session_id(),'enermy':e,'from':'explore'})
                await explore.send(MessageSegment.image(e.object.draw())+MessageSegment.at(event.get_user_id())+f"\n你遇到了野生沃兜！\n你有{e.object.rows}次机会猜出单词，单词长度为{e.object.length}，请发送单词")

def game_running(event: Event) -> bool:
    for wd in wordles:
        if wd['session']==event.get_session_id():
            return True
    return False
def get_word_input(msg: str = EventPlainText()) -> bool:
    if re.fullmatch(r"^[a-zA-Z]{3,8}$", msg) or msg=='投降' or msg=='提示':
        return True
    return False
wordMatcher = on_message(Rule(game_running) & get_word_input, block=True, priority=12)
@wordMatcher.handle()
async def _(event: Event):
    for i in range(len(wordles)):
        if wordles[i]['session']==event.get_session_id():
            gid = event.get_session_id().split("_")[0]
            user = monoGroup(gid).find_user(event.get_user_id())
            if wordles[i]['from']=='explore':state,e = wordle_battle(explore,event,user)
            elif wordles[i]['from']=='event':state,e = wordle_battle(moveAction,event,user)
            if state==GuessResult.WIN or state==GuessResult.LOSS:
                if wordles[i]['from']=='explore':
                    if state==GuessResult.LOSS:
                        user.add_money(-e.object.length+2)
                        wordles.pop(i)
                        await explore.finish(MessageSegment.image(e.object.draw())+MessageSegment.at(event.get_user_id())+f'\n{e.object.result}\n你被{e.type}沃兜打败了，它抢走了你的{e.object.length-2}火币！')
                    elif state==GuessResult.WIN:
                        money = e.object.length-len(e.object.guessed_words)+3
                        wordles.pop(i)
                        user.add_money(money)
                        await explore.finish(MessageSegment.image(e.object.draw())+MessageSegment.at(event.get_user_id())+f'\n{e.object.result}\n战斗胜利！获得{money}火币！')
                elif wordles[i]['from']=='event':
                    for e in events:
                        if e['session']==event.get_session_id():
                            eObj = e['event']
                            postText = eObj.end(state)
                            events.pop(events.index(e))
                            await moveAction.finish(postText)
            else:
                if state=='noHint':
                    await explore.send(MessageSegment.at(event.get_user_id())+"\n你还没有猜对过一个字母哦~再猜猜吧~")
                elif state=='hint':
                    hint = e.object.get_hint()
                    await explore.send(MessageSegment.image(e.object.draw_hint(hint))+MessageSegment.at(event.get_user_id()))
                elif state=='noLength':
                    pass
                elif state==GuessResult.DUPLICATE:
                    await explore.send(MessageSegment.at(event.get_user_id())+"\n你已经猜过这个单词了呢")
                elif state==GuessResult.ILLEGAL:
                    await explore.send(MessageSegment.at(event.get_user_id())+f"\n你确定 {event.get_plaintext()} 是一个合法的单词吗？")
                else:
                    await explore.send(MessageSegment.image(e.object.draw())+MessageSegment.at(event.get_user_id()))
def event_running(event: Event) -> bool:
    for e in events:
        if e['session']==event.get_session_id():
            return True
    return False
def get_choice_input(msg: str = EventPlainText()) -> bool:
    if re.fullmatch(r"^[0-9]$", msg):
        return True
    return False
eventMatcher = on_message(Rule(event_running) & get_choice_input, block=True, priority=12)
@eventMatcher.handle()
async def _(event: Event):
    for i in range(len(events)):
        if events[i]['session']==event.get_session_id():
            gid = event.get_session_id().split("_")[0]
            user = monoGroup(gid).find_user(event.get_user_id())
            e = events[i]['event']
            postText = e.make_choice(int(event.get_plaintext()))
            findW = False
            for w in wordles:
                if w['session']==event.get_session_id():
                    findW==True
            if not findW:
                events.pop(i)
            await eventMatcher.send(postText)