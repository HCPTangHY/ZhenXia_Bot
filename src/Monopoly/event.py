from typing import Optional
from .models import *
from .battle import *
from ..wordle_zhenxia import random_word,Wordle

events = []
class monoEvent():
    type=''
    preText=''
    choice = []
    def __init__(self,event:Event,user:monoUser) -> None:
        self.event = event
        self.user = user

    def make_choice(self,c:int):
        if len(self.choice)==0:return None
        elif len(self.choice)==1:return self.choice[0]
        else:return self.choice[c]

class monoEventBlackMarket(monoEvent):
    type = 'blackMarket'
    preText="\t你忽然听见一个中性声音从阴影中呼唤：“嘿，又见面了。想不想做一笔买卖……”\n\t你转过身，面向那个鬼鬼祟祟的商人，盘算着是要接受对方的提议，还是赶紧赶你的路……(输入0/1选择)\n"
    choice = [
        '\t你不在乎这个鬼鬼祟祟的家伙要兜售什么东西，便无视了他，继续赶路了。你离开了这个可疑的角色，而他中性的声音却又从你身后传来，我们会再见面的……',
        '\t你不在乎这个鬼鬼祟祟的家伙要兜售什么东西，便无视了他，继续赶路了。你离开了这个可疑的角色，而他中性的声音却又从你身后传来，我们会再见面的……'
    ]

class monoEventSecretMoney(monoEvent):
    type = 'secretMoney'
    preText = '\t你在小巷里找到一个沾满精液的包裹……(输入0选择)'

    def make_choice(self, c: int):
        money = random.randint(2,7)*10
        self.user.add_money(money)
        self.choice = [f'事到如今已经无法知道这个包裹原本是给谁的了，为了不让它被浪费，你小心翼翼地剥开包裹纸，露出了里面的{money}火币']
        return self.choice[0]

class monoEventLewdWordle(monoEvent):
    type = 'lewdWordle'
    preText = '\t你遇到一个色迷迷的沃兜！\n\t显而易见，一旦战败就会被这欲火焚身的沃兜不可描述(输入0/1选择战斗/投降)'
    choice = [
        'battle',
        '你被迫和这个沃兜做了不可描述的事情，事后，它扬长而去，留你独自在小巷休息……'
    ]
    postText = {
        'battleWin':'沃兜完全被打败了。你翻了翻它掉落在地上的背包，拿走了10火币，轰走了它。',
        'battleLoss':'你被迫和这个沃兜做了不可描述的事情，事后，它扬长而去，留你独自在小巷休息……'
        }

    def make_choice(self, c: int):
        if c==0:
            word,meaning = random_word("CET4",random.choice([5,5,5,5,6]))
            e = Enermy('色迷迷的',self.user,[],Wordle(word,meaning))
            wordles.append({'session':self.event.get_session_id(),'enermy':e,'from':'event'})
            return (MessageSegment.image(e.object.draw())+MessageSegment.at(self.event.get_user_id())+f"\n你遇到了野生沃兜！\n你有{e.object.rows}次机会猜出单词，单词长度为{e.object.length}，请发送单词")
        elif c==1:
            return self.choice[1]
    def end(self,state:GuessResult,e:Enermy):
        if state==GuessResult.WIN:
            self.user.add_money(10)
            return self.postText['battleWin']
        else:
            return self.postText['battleLoss']
class monoEventLootWordle(monoEvent):
    type = 'lootWordle'
    preText = '\t你遇到一个凶狠的沃兜！显而易见，它很可能是想在你战败后抢劫你。(输入0/1选择战斗/投降)'
    choice = [
        'battle',
        'give money'
    ]
    postText = {
        'giveMoney':'为了避免战斗，你后退一步，抓起一堆火币递给它：“我不想惹事，拜托你，收下我的钱，让我离开这儿！”',
        'battleWin':'沃兜完全被打败了。你翻了翻它掉落在地上的背包，拿走了10火币，轰走了它。',
        'battleLoss':'你瘫倒在地，被沃兜抢走了所有火币，“早这样不就好了！”沃兜朝你吐了一口唾沫，扬长而去……'
        }
    def make_choice(self, c: int):
        if c==0:
            word,meaning = random_word("CET4",random.choice([5,5,5,5,6]))
            e = Enermy('凶狠的',self.user,[],Wordle(word,meaning))
            wordles.append({'session':self.event.get_session_id(),'enermy':e,'from':'event'})
            return (MessageSegment.image(e.object.draw())+MessageSegment.at(self.event.get_user_id())+f"\n你遇到了野生沃兜！\n你有{e.object.rows}次机会猜出单词，单词长度为{e.object.length}，请发送单词")
        elif c==1:
            self.user.add_money(-(self.user.money/2))
            return self.postText['giveMoney']
    def end(self,state,e:Enermy):
        if state==GuessResult.WIN:
            self.user.add_money(10)
            return self.postText['battleWin']
        else:
            self.user.add_money(-(self.user.money))
            for u in e.participate:
                u.add_money(-(u.money))
            return self.postText['battleLoss']
class monoEventPatrol(monoEvent):
    type = 'patrol'
    preText = '你沿着小巷的一边走下去，突然遇到一对执法者。他们要求对你进行依法搜身，如果你的犯罪很多，他们很可能认出你来……(输入0/1选择被搜身/贿赂他们500火币)'
    choice = [
        '执法者对你进行了搜身，没有发现什么异常。他们感谢你配合工作后就离开了……',
        '执法者对你进行了搜身，他们突然一愣，随机决定立刻逮捕你……',
        '你掏出500火币：“长官……我有急事……您看放我一马呢……”，执法者们微微一笑，告诫你下不为例，扬长而去',
        '你没有500火币，只能接受执法者的搜身了……'
    ]
    def make_choice(self, c: int):
        if c==0:
            if self.user.crime<=4:return self.choice[0]
            else:
                self.user.change_state(1)
                conn = sqlite3.connect(f"data/INDEX/{self.user.group.gid}.db")
                cur = conn.cursor()
                cityHallKey = cur.execute(f"select cid from map where chunkType='cityHall';").fetchone()[0]
                self.user.move_to(cityHallKey)
                return self.choice[1]
        else:
            if self.user.money>=500:
                self.user.add_money(-500)
                return self.choice[2]
            else:
                if self.user.crime<=4:return self.choice[3]+''+self.choice[0]
                else:
                    self.user.change_state(1)
                    conn = sqlite3.connect(f"data/INDEX/{self.user.group.gid}.db")
                    cur = conn.cursor()
                    cityHallKey = cur.execute(f"select cid from map where chunkType='cityHall';").fetchone()[0]
                    self.user.move_to(cityHallKey)
                    return self.choice[3]+''+self.choice[1]