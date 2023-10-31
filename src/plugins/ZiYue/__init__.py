from nonebot import on_message,on_command
from nonebot.rule import to_me,command
from nonebot.params import Arg,CommandArg
from nonebot.matcher import Matcher
from nonebot.typing import T_State
from nonebot.adapters import MessageTemplate
from nonebot.adapters.red import Bot,Message,MessageEvent
from nonebot.adapters.red.message import MessageSegment
from nonebot_plugin_saa import Image,MessageFactory

import sqlite3,time,re,shutil,random

newBook = on_command("新建语录",priority=10,block=True)
@newBook.handle()
async def addNewBook(event:MessageEvent,args: Message = CommandArg()):
    book = args.extract_plain_text()
    if book:
        conn = sqlite3.connect("data/ZiYue.db")
        cur = conn.cursor()
        cur.execute("select * from books;")
        data = cur.fetchall()
        print(data)
        id = 1
        for item in data:
            if id<=item[0]:
                id = item[0]+1
        cur.execute(
            f"insert into books(id,name,creater,created_at) values({id},'{book}','{event.sendMemberName}',{time.time()});"
            )
        conn.commit()
        cur.close()
        t = time.localtime()
        await newBook.send(f"{book}已立案，建立时间{t.tm_year}-{t.tm_mon}-{t.tm_mday} {t.tm_hour}:{t.tm_min}:{t.tm_sec}")
    else:
        await newBook.send("请输入语录名")

newSen = on_command("上传语录",priority=10,block=True)
@newSen.handle()
async def _(matcher: Matcher,state: T_State,args: Message = CommandArg()):
    book = args.extract_plain_text()
    if book:
        pass
    else:
        await newSen.finish("未选择语录")
    state['book'] = args.extract_plain_text()
    newSen.set_arg(matcher,"prompt",message=args)

@newSen.got("prompt", prompt=MessageTemplate("请上传内容(图片形式) ：目标语录 {book}"))
async def Sentence_upload(state: T_State,event: MessageEvent,prompt: Message = Arg(), msg: Message = Arg("prompt")):
    rt = r"\[image:.*'path': '(.*?)',.*\]"
    path = re.findall(rt, str(msg))
    fileName = re.findall(r"\[image:.*'path': '.*Ori\\\\(.*?)',.*\]", str(msg))
    print(str(msg))
    if len(path) == 0:
        resp = "请上传图片"
        await newSen.reject_arg('prompt', MessageSegment.reply(event.msgSeq) + resp)
    print(path[0])
    try:
        shutil.copy(path[0],'data/ZiYueImg/')
    except:
        path[0] = re.sub(r'Ori','Thumb',path[0])
        path[0] = re.sub('.jpg','_0.jpg',path[0])
        shutil.copy(path[0],'data/ZiYueImg/')
        fileName[0] = re.sub('.jpg','_0.jpg',fileName[0])
    book = state['book']
    if book:
        conn = sqlite3.connect("data/ZiYue.db")
        cur = conn.cursor()
        cur.execute("select * from sentence;")
        data = cur.fetchall()
        bid = cur.execute(f"select id from books where name='{book}'").fetchone()
        if len(bid)==0:
            await newBook.send("未找到语录")
        else:
            bid = bid[0]
        id = iid = 1
        for item in data:
            if id<=item[0]:
                id = item[0]+1
            if item[3]==bid:
                if iid<=item[1]:
                    iid = item[1]+1
        print(fileName[0])
        cur.execute(
            f"insert into sentence(id,iid,content,book,uploader,updated_at) values({id},{iid},'{fileName[0]}',{bid},'{event.sendMemberName}',{time.time()});"
        )
        conn.commit()
        cur.close()
        await newBook.send("记录成功\n语录唯一ID：{}\n{}内ID{}".format(id,book,iid))

randomSentence = on_command("随机语录",priority=10,block=True)
@randomSentence.handle()
async def randomSen(event:MessageEvent,args: Message = CommandArg()):
    conn = sqlite3.connect("data/ZiYue.db")
    cur = conn.cursor()
    if args.extract_plain_text():
        book = args.extract_plain_text()
        bid = cur.execute(f"select id from books where name='{book}'").fetchone()
        if len(bid)==0:
            pass
        else:
            bid = bid[0]
            cur.execute(f"select * from sentence where book={bid};")
            data = cur.fetchall()
            s = list(random.choice(data))
            t = time.localtime(s[5])
    else:
        cur.execute("select * from sentence;")
        data = cur.fetchall()
        s = list(random.choice(data))
        book = cur.execute("select name from books where id={}".format(s[3])).fetchone()[0]
        t = time.localtime(s[5])
    conn.commit()
    cur.close()
    if ".jpg" in s[2]:
        await randomSentence.send(f"==={book} {s[1]}===\n"+MessageSegment.image(f"data/ZiYueImg/{s[2]}")+f"\n==========\n上传人：{s[4]}\n收录时间：{t.tm_year}-{t.tm_mon}-{t.tm_mday} {t.tm_hour}:{t.tm_min}:{t.tm_sec}")
    else:
        await randomSentence.send(f"==={book} {s[1]}===\n{s[2]}\n==========\n上传人：{s[4]}\n收录时间：{t.tm_year}-{t.tm_mon}-{t.tm_mday} {t.tm_hour}:{t.tm_min}:{t.tm_sec}")
