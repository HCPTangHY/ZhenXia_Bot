from nonebot import on_message
from nonebot.rule import to_me
from nonebot.adapters.red import Bot,Message,MessageEvent
from nonebot.adapters.red.message import MessageSegment

import re,os,random


models = ["枕小霞2.0","枕小霞1.6","文和武乱1.0","东方1.0","大明王朝1.0","科幻1.0"]
modelPath = ["model/ZX2.0","model/ZX1.6","model/whwl1.0","model/TH1.0","model/1566","model/sf1.0"]

ask = on_message(rule=to_me())
g_message = on_message(priority=20)

modelUsing = models[0]
modelUsing = models[0]
groups = {872847025:{"reMsg":"", "msgQueue":[],"msgHistory":[],"lastMsg":""}}
def group_init(group_id:int,groups:list):
    groups[group_id] = {"reMsg":"", "msgQueue":[","],"msgHistory":[],"lastMsg":""}
    print(groups)
def msg_preprocess(msg:str):
    msg = re.sub(r'\[CQ:.*?\]',' ',msg)
    msg = msg.strip()
    msg = msg.replace(" ","")
    if msg == '':msg = '。'
    return msg
def reply_process(text:str):
    text = re.sub(r'.*?chatbot:','',text)
    text = re.sub(r'#.*#','',text)
    text = text.strip()
    if text == '':text = '？？'
    return text
def msgQueueInput(msgQueue : list,msg : str):
    msgQueue.append(msg)
    if len(msgQueue)>8:
        msgQueue.pop(0)
    return msgQueue
def GPTchat(history:str):
    path = modelPath[models.index(modelUsing)]
    print(history)
    content = os.popen('cd ./GPT2_chitchat && python interact.py --model_path {} --max_history_len 7 --one_ans True --history {}'.format(path,history))
    text = content.read()
    text = reply_process(text)
    print(text)
    return text

@ask.handle()
async def askGPT(event:MessageEvent):
    group_id = int(event.scene)
    if group_id not in groups:
        group_init(group_id,groups)
    msg = event.message.extract_plain_text()
    msg = msg.strip()
    msg = msg.replace(" ","")
    if (groups[group_id]["msgQueue"][-1]!=msg):
        groups[group_id]["msgQueue"] = msgQueueInput(groups[group_id]["msgQueue"],msg)
    history = " ".join(groups[group_id]["msgQueue"])
    ans = GPTchat(history)
    # await Bot.send_group_message(Bot,int(group_id),message=f'[CQ:reply,id:{event.msgId}]'+ans)
    groups[group_id]["msgQueue"] = msgQueueInput(groups[group_id]["msgQueue"],ans)
    Bot.send_group_message(Bot,int(group_id),message=MessageSegment.reply(ans,message_id=event.msgId,sender_uin=group_id)+MessageSegment.at(event.get_user_id())+' '+ans)
    if ans == "？":
        ans = GPTchat(history)
        print(ans)
        if ans != '？':
            await ask.reject(ans)
        else:
            await ask.reject("?")
    else:
        await ask.reject(MessageSegment.reply(ans,message_id=event.msgId,sender_uin=group_id)+MessageSegment.at(event.get_user_id())+' '+ans)


@g_message.handle()
async def g_m(event:MessageEvent):
    group_id = int(event.scene)
    if group_id not in groups:
        group_init(group_id,groups)
    if (groups[group_id]["lastMsg"] == event.message and groups[group_id]['reMsg'] != event.message):
        groups[group_id]['reMsg'] = event.message
        await ask.send(event.message)
    msg = event.message.extract_plain_text()
    msg = msg.strip()
    msg = msg.replace(" ","")
    if (msg != '') and ('[CQ:' not in msg) and ('/' not in msg) and ('wordle' not in msg):
        groups[group_id]["msgQueue"] = msgQueueInput(groups[group_id]["msgQueue"],msg)
    groups[group_id]["lastMsg"] = event.message
    if random.random()<0.175:
        history = " ".join(groups[group_id]["msgQueue"])
        print(history)
        ans = GPTchat(history)
        groups[group_id]["msgQueue"] = msgQueueInput(groups[group_id]["msgQueue"],ans)
        Bot.send_group_message(Bot,int(group_id),ans)
        if ans == "？":
            ans = GPTchat(history)
            print(ans)
            if ans != '？':
                await ask.reject(ans)
            else:
                await ask.reject("?")
        else:
            await ask.send(ans)