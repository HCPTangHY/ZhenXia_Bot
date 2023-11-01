from nonebot import on_message,on_command
from nonebot.rule import to_me,command
from nonebot.params import Arg,CommandArg
from nonebot.matcher import Matcher
from nonebot.typing import T_State
from nonebot.adapters import MessageTemplate
from nonebot.adapters.red import Bot,Message,MessageEvent
from nonebot.adapters.red.message import MessageSegment

import sqlite3,time,re,random,requests,urllib3

async def stdSentenceOut(matcher:Matcher,data:tuple,bookName):
    t = time.localtime(data[5])
    if "[IMG:" in data[2]:
        md5 = re.findall(r'\[IMG:(.*?)\]', data[2])[0].upper()
        image_url= "https://gchat.qpic.cn/gchatpic_new/0/0-0-"+md5+'/0?term=2&amp;is_origin=0'

        proxies = {"http": "http://127.0.0.1:7890","https": "http://127.0.0.1:7890",}
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        res = requests.get(image_url,verify=False,proxies=proxies)
        with open('data/ZiYueImg/0.gif', 'wb') as f:
            f.write(res.content)
        await matcher.send(f"==={bookName} {data[1]}===\n"+MessageSegment.image('data/ZiYueImg/0.gif')+f"\n==========\n上传人：{data[4]}\n收录时间：{t.tm_year}-{t.tm_mon}-{t.tm_mday} {t.tm_hour}:{t.tm_min}:{t.tm_sec}")
    else:
        await matcher.send(f"==={bookName} {data[1]}===\n{data[2]}\n==========\n上传人：{data[4]}\n收录时间：{t.tm_year}-{t.tm_mon}-{t.tm_mday} {t.tm_hour}:{t.tm_min}:{t.tm_sec}")

async def stdEchoOut(matcher:Matcher,data:tuple,):
    if "[IMG:" in data[1]:
        md5 = re.findall(r'\[IMG:(.*?)\]', data[1])[0].upper()
        image_url= "https://gchat.qpic.cn/gchatpic_new/0/0-0-"+md5+'/0?term=2&amp;is_origin=0'

        proxies = {"http": "http://127.0.0.1:7890","https": "http://127.0.0.1:7890",}
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        res = requests.get(image_url,verify=False,proxies=proxies)
        with open('data/ZiYueImg/0.gif', 'wb') as f:
            f.write(res.content)
        await matcher.send(f"===回声洞 {data[0]}===\n"+MessageSegment.image('data/ZiYueImg/0.gif'))
    else:
        await matcher.send(f"===回声洞 {data[0]}===\n{data[1]}\n")

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
            f"insert into books(id,name,creater,created_at) values({id},'{book}','{event.sendNickName}',{time.time()});"
            )
        conn.commit()
        cur.close()
        t = time.localtime()
        await newBook.send(f"{book}已立案，建立时间{t.tm_year}-{t.tm_mon}-{t.tm_mday} {t.tm_hour}:{t.tm_min}:{t.tm_sec}")
    else:
        await newBook.send("请输入语录名")

newSen = on_command("上传语录",priority=10,block=True)
@newSen.handle()
async def newSentence(event:MessageEvent,args:Message=CommandArg()):
    book = args.extract_plain_text()
    if book:
        pass
    else:
        await newSen.finish("未选择语录")
    text = ''
    for e in event.records[0].elements:
        if e.picElement:
            md5 = e.picElement.md5HexStr
            content = '[IMG:'+md5+']'
            break
        else:
            if e.textElement:
                text += e.textElement.content
    if text!='':
        content = text
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
    cur.execute(
        f"insert into sentence(id,iid,content,book,uploader,updated_at) values({id},{iid},'{content}',{bid},'{event.sendNickName}',{time.time()});"
    )
    conn.commit()
    cur.close()
    await newBook.send(f"记录成功\n语录唯一ID：{id}\n{book}内ID：{iid}")

randomSen = on_command("随机语录",priority=10,block=True)
@randomSen.handle()
async def randomSentence(event:MessageEvent,args: Message = CommandArg()):
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
        book = cur.execute(f"select name from books where id={s[3]}").fetchone()[0]
        t = time.localtime(s[5])
    conn.commit()
    cur.close()
    await stdSentenceOut(randomSen,s,book)

askSen = on_command("查询语录",priority=10,block=True)
@askSen.handle()
async def askSentence(event:MessageEvent,args: Message = CommandArg()):
    args = args.extract_plain_text().split(" ")
    conn = sqlite3.connect("data/ZiYue.db")
    cur = conn.cursor()
    if len(args) == 1:
        cur.execute(f"select * from sentence where id={int(args[0])};")
        s = cur.fetchone()
        book = cur.execute(f"select name from books where id={s[3]}").fetchone()[0]
        await stdSentenceOut(askSen,s,book)
    else:
        bid = cur.execute(f"select id from books where name='{args[0]}'").fetchone()[0]
        cur.execute(f"select * from sentence where book={bid} and iid={int(args[1])};")
        s = cur.fetchone()
        await stdSentenceOut(askSen,s,args[0])
    conn.commit()
    cur.close()

newEcho = on_command("传入回声",aliases={"人格复制"},priority=10,block=True)
@newEcho.handle()
async def newEchoUpdate(event:MessageEvent,args:Message=CommandArg()):
    text = ''
    for e in event.records[0].elements:
        if e.picElement:
            md5 = e.picElement.md5HexStr
            content = '[IMG:'+md5+']'
            break
        else:
            if e.textElement:
                text += e.textElement.content
    if text!='':
        content = text
    conn = sqlite3.connect("data/ZiYue.db")
    cur = conn.cursor()
    try:
        cur.execute("select * from echo;")
    except:
        cur.execute("CREATE TABLE echo(id INT PRIMARY KEY,content TEXT,updated_at REAL);")
        cur.execute("select * from echo;")
    data = cur.fetchall()
    id = 0
    for item in data:
        if id<=item[0]:
            id = item[0]+1
        if item[1]==content:
            newEcho.finish(MessageSegment.at(event.get_user_id())+"小笨蛋，已经有相同回声了哦！")
    cur.execute(
        f"insert into echo(id,content,updated_at) values({id},'{content}',{time.time()});"
    )
    conn.commit()
    cur.close()
    await newEcho.send(f"人格复制已完成！\n回声编号：{id}")

ask_echo = on_command("回声洞",priority=10,block=True)
@ask_echo.handle()
async def askEcho(event:MessageEvent,args: Message = CommandArg()):
    args = args.extract_plain_text().split(" ")
    conn = sqlite3.connect("data/ZiYue.db")
    cur = conn.cursor()
    print(args)
    if args[0] != '':
        cur.execute(f"select * from echo where id={int(args[0])};")
        s = cur.fetchone()
        await stdEchoOut(ask_echo,s)
    else:
        cur.execute("select * from echo;")
        data = cur.fetchall()
        s = list(random.choice(data))
        await stdEchoOut(ask_echo,s)
    conn.commit()
    cur.close()
