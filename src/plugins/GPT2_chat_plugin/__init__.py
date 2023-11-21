from nonebot import on_message,on_command
from nonebot.rule import to_me
from nonebot.params import CommandArg
from nonebot.adapters.red import Bot,MessageEvent,Message
from nonebot.adapters.red.message import MessageSegment
import re,os,random,time,numpy,subprocess


models = ["枕小霞2.1","枕小霞1.6","文和武乱1.0","大明王朝2.0","50W语料","贴吧300W","微博450W"]
modelPath = ["model/ZX2.1","model/ZX1.6","model/whwl1.0","model/1566","model/model_epoch40_50w","model/tieba","model/weibo"]

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
    text = re.sub('-','',text)
    text = text.strip()
    if len(text)>=2:
        if text[-1] == '，' and text[-2] == '，':
            return text
        else:
            ans = text.split("，")
            ans = numpy.unique(ans).tolist()
            return ans
    else:
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
    p = subprocess.Popen('cd ./GPT2_chitchat && python -i interact.py --model_path {} --max_history_len 7 --one_ans True --history {}'.format(path,history),shell=True,stdout=subprocess.PIPE)
    text = p.stdout.readline().decode('gbk')
    text = reply_process(text)
    print(text)
    return text
ask = on_message(rule=to_me())
@ask.handle()
async def askGPT(bot:Bot,event:MessageEvent):
    group_id = int(event.scene)
    if group_id not in groups:
        group_init(group_id,groups)
    msg = event.message.extract_plain_text()
    msg = msg.strip()
    msg = msg.replace(" ","")
    groups[group_id]["msgQueue"] = msgQueueInput(groups[group_id]["msgQueue"],msg)
    if event.reply:
        text = ''
        for e in event.records[0].elements:
            if e.textElement:
                text+=e.textElement.content
        groups[group_id]["msgQueue"][-1] = text
        groups[group_id]["msgQueue"] = msgQueueInput(groups[group_id]["msgQueue"],msg)
        history = " ".join(groups[group_id]["msgQueue"])
    history = " ".join(groups[group_id]["msgQueue"])
    ans = GPTchat(history)
    if isinstance(ans,list):
        groups[group_id]["msgQueue"] = msgQueueInput(groups[group_id]["msgQueue"],' '.join(ans))
        for i in range(len(ans)):
            if i == 0:
                await bot.send(event,MessageSegment.reply(event.msgSeq,sender_uin=event.senderUin)+MessageSegment.at(event.get_user_id())+' '+ans[i])
            else:
                await bot.send(event,ans[i])
            time.sleep(0.35)
    elif isinstance(ans,str):
        groups[group_id]["msgQueue"] = msgQueueInput(groups[group_id]["msgQueue"],ans)
        await bot.send(event,MessageSegment.reply(event.msgSeq,sender_uin=event.senderUin)+MessageSegment.at(event.get_user_id())+' '+ans)
    if ans == "？":
        history+=' ？'
        ans = GPTchat(history)
        if ans != '？':
            if isinstance(ans,str):
                groups[group_id]["msgQueue"] = msgQueueInput(groups[group_id]["msgQueue"],ans)
                await bot.send(event,ans)
            elif isinstance(ans,list):
                groups[group_id]["msgQueue"] = msgQueueInput(groups[group_id]["msgQueue"],"".join(ans))
                for i in range(len(ans)):
                    await bot.send(event,ans[i])
                    time.sleep(0.35)
            await ask.reject()
        else:
            await ask.reject()
    else:
        await ask.reject()

change_model = on_command("切换模型",aliases={"changeModel"},priority=10,block=True)
@change_model.handle()
async def changeModel(args: Message = CommandArg()):
    m = args.extract_plain_text()
    if m in models:
        global modelUsing
        med = modelUsing
        modelUsing = m
        await change_model.finish(f"正在语言模型{med}，已转化为语言模型{m}")
    else:
        await change_model.finish("未找到模型！")

model_list = on_command("模型列表",aliases={"modelList"},priority=10,block=True)
@model_list.handle()
async def modelList():
    await model_list.finish(f"小霞语言模型列表{models}，当前模型{modelUsing}")

g_message = on_message(priority=100)
@g_message.handle()
async def g_m(bot:Bot,event:MessageEvent):
    group_id = int(event.scene)
    if group_id not in groups:
        group_init(group_id,groups)
    if (groups[group_id]["lastMsg"] == event.message and groups[group_id]['reMsg'] != event.message):
        groups[group_id]['reMsg'] = event.message
        await ask.send(event.message)
    if "明" in event.message.extract_plain_text():
        await ask.send("嘘！不准说「明」，你说「明」，你就咔嚓")
    msg = event.message.extract_plain_text()
    msg = msg.strip()
    msg = msg.replace(" ","")
    if (msg != '') and ('[CQ:' not in msg) and ('/' not in msg) and ('wordle' not in msg):
        groups[group_id]["msgQueue"] = msgQueueInput(groups[group_id]["msgQueue"],msg)
    groups[group_id]["lastMsg"] = event.message
    if random.random()<0.1:
        history = " ".join(groups[group_id]["msgQueue"])
        print(history)
        ans = GPTchat(history)
        if isinstance(ans,str):
            groups[group_id]["msgQueue"] = msgQueueInput(groups[group_id]["msgQueue"],ans)
            await bot.send(event,ans)
        elif isinstance(ans,list):
            groups[group_id]["msgQueue"] = msgQueueInput(groups[group_id]["msgQueue"],"".join(ans))
            for i in range(len(ans)):
                await bot.send(event,ans[i])
                time.sleep(0.35)
        if ans == "？":
            history+=' ？'
            ans = GPTchat(history)
            if ans != '？':
                if isinstance(ans,str):
                    groups[group_id]["msgQueue"] = msgQueueInput(groups[group_id]["msgQueue"],ans)
                    await bot.send(event,ans)
                elif isinstance(ans,list):
                    groups[group_id]["msgQueue"] = msgQueueInput(groups[group_id]["msgQueue"],"".join(ans))
                    for i in range(len(ans)):
                        await bot.send(event,ans[i])
                        time.sleep(0.35)