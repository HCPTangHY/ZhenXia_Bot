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
    preText="\t你正穿越迷宫般的小巷，眼前没有一个人影。黑暗的砖墙上排列着后门和冒着蒸汽的通风口，你经常不得不绕过满溢的垃圾桶和一堆堆空箱子才能继续前进。\n\t当你绕过一堆板条箱时，忽然听见一个中性声音从阴影中呼唤：“嘿，又见面了。想不想做一笔买卖？当然，依旧不要多问……”\n\t你转过身，面向那个鬼鬼祟祟的商人，盘算着是要接受对方的提议，还是赶紧赶你的路……(输入0/1选择)\n"
    choice = [
        '\t你不在乎这个鬼鬼祟祟的家伙要兜售什么东西，便无视了他，继续赶路了。你离开了这个可疑的角色，而他中性的声音却又从你身后传来，我们会再见面的……',
        '\t你不在乎这个鬼鬼祟祟的家伙要兜售什么东西，便无视了他，继续赶路了。你离开了这个可疑的角色，而他中性的声音却又从你身后传来，我们会再见面的……'
    ]

class monoEventSecretMoney(monoEvent):
    type = 'secretMoney'
    preText = '\t你正穿越迷宫般的小巷，你注意到一个棕色的纸包裹无辜地躺在金属垃圾桶旁。即便只是匆匆一瞥，你也能看出那不是什么旧垃圾，它仍被完好封印着。你看不到任何陷阱的迹象，而且这个包裹看上去被完全遗弃了，因此你决定上前去检查一番。\n\t你弯下腰去查看，那是个被棕色包裹纸包着，用胶带封好的方方正正的中型盒子。盒子侧面的标签被某种液体弄脏了，你分辨不出上面写了什么。直到一股麝香气味突然充满了你的鼻腔，你这才意识到那液体实际上是一些黏糊糊的白色精液。正当你思考着是什么原因令这个包裹被遗弃在这里时，你注意到墙上和地上到处都是飞溅的精液。(输入0选择)'

    def make_choice(self, c: int):
        money = random.randint(2,7)*10
        self.user.add_money(money)
        self.choice = [f'事到如今已经无法知道这个包裹原本是给谁的了，为了不让它被浪费，你小心翼翼地剥开包裹纸，露出了里面的{money}火币']
        return self.choice[0]

class monoEventLewdWordle(monoEvent):
    type = 'lewdWordle'
    preText = '\t你正穿越迷宫般的小巷，里面排列着一系列嵌入的门道。当你经过一个凹槽时，一个人影突然从阴影中跳出来，挡住了你的去路。你向后一跳，侥幸躲过了对准你腹部的一击，然后做好战斗的架势。抬头一看，一个沃兜正对你恶狠狠地笑。“怎么事？”它问道，看到你一副战斗准备的架势，不禁轻笑，“如果你放弃就好办多了！”\n\t显而易见，你已经让她有感觉了，从它那游走你全身上下的饥渴视线，你很清楚她想对你做的事情。一想到一旦战败就会被这欲火焚身的沃兜不可描述，你做好了战斗的准备。(输入0/1选择)'
    choice = [
        'battle',
        '你被迫和这个沃兜做了不可描述的事情，事后，它扬长而去，留你独自在小巷休息……'
    ]
    postText = {
        'battleWin':'沃兜倒在地上，完全被打败了。它抬头看着你，渴望地呜咽着，咬着它的嘴唇。你看到它的眼睛中仍然流露出饥渴、淫荡的神情。它将手伸向单词，开始抚摸它自己，发出可怜的呜呜声，在地上扭动着：“~啊！~你在等什么？！快来！“它哀求着。\n\t你不理它，翻了翻它掉落在地上的背包，拿走了10火币，对这个沃兜攻击无辜路人的事做法感到厌恶，皱着眉头看着它说：“我不想再抓到你这样做。下次见到你时，我会和执法者在一起，你自己看看他们会怎么对付你。”\n“等等，我只是需要钱！你不能这么做……”沃兜开始结结巴巴，执法者介入的威胁让她清醒了过来。\n\t你没兴趣听这个罪犯说什么，你打断了她：“把嘴闭上！如果你需要钱，就去找份工作！你竟敢为你的犯罪活动狡辩！在我决定马上去找执法者之前，快给我滚！”\n\t你看到沃兜泪流满面，意识到自己没有资格争辩，便默默地站起来跑开了，甚至没有向你的方向有过一次回头。看到它的反应，你可以肯定再也不会在这条小巷里看到它了。你对自己对付这个卑鄙之人的方式感到很满意，出发继续赶路……',
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
    def end(self,state:GuessResult):
        if state==GuessResult.WIN:
            self.user.add_money(10)
            return self.postText['battleWin']
        else:
            return self.postText['battleLoss']
class monoEventLootWordle(monoEvent):
    type = 'lootWordle'
    preText = '\t你正穿越迷宫般的小巷，里面排列着一系列嵌入的门道。当你经过一个凹槽时，一个人影突然从阴影中跳出来，挡住了你的去路。你向后一跳，侥幸躲过了对准你腹部的一击，然后做好战斗的架势。抬头一看，一个沃兜正对你恶狠狠地笑。“怎么事？”它问道，看到你一副战斗准备的架势，不禁轻笑，“如果你放弃就好办多了！”\n\t尽管你让她稍稍有了感觉，但她看起来并不是完全只对你的身体感兴趣，更可能是想在你战败后抢劫你。(输入0/1选择)'
    choice = [
        'battle',
        'give money'
    ]
    postText = {
        'giveMoney':'为了避免战斗，你后退一步，抓起一堆火币递给它：“我不想惹事，拜托你，收下我的钱，让我离开这儿！”',
        'battleWin':'沃兜倒在地上，完全被击败了。她抬头瞥了你一眼，目光投向地板，在那短短的一瞬间，你看到它的眼睛里流露出绝望而悔恨的神情。她发出可怜的呜呜声，试图从你身边闪开，显然是在担心你的意图。“求，求你拿走我的钱离开吧！”它恳求道，把火币丢在你的脚边。\n\t你不理它，翻了翻它掉落在地上的背包，拿走了10火币，对这个沃兜攻击无辜路人的事做法感到厌恶，皱着眉头看着它说：“我不想再抓到你这样做。下次见到你时，我会和执法者在一起，你自己看看他们会怎么对付你。”\n“等等，我只是需要钱！你不能这么做……”沃兜开始结结巴巴，执法者介入的威胁让她清醒了过来。\n\t你没兴趣听这个罪犯说什么，你打断了她：“把嘴闭上！如果你需要钱，就去找份工作！你竟敢为你的犯罪活动狡辩！在我决定马上去找执法者之前，快给我滚！”\n\t你看到沃兜泪流满面，意识到自己没有资格争辩，便默默地站起来跑开了，甚至没有向你的方向有过一次回头。看到它的反应，你可以肯定再也不会在这条小巷里看到它了。你对自己对付这个卑鄙之人的方式感到很满意，出发继续赶路……',
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
    def end(self,state):
        if state==GuessResult.WIN:
            self.user.add_money(10)
            return self.postText['battleWin']
        else:
            self.user.add_money(-(self.user.money))
            return self.postText['battleLoss']