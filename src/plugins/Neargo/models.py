from nonebot import require
from PIL import Image as PILIMG
from PIL import ImageDraw
import os,pandas
from enum import Enum

require("Index_user_management")
require("wordle_zhenxia")

from ..Index_user_management import *

class Position():
    id=gid=0
    name = desc = owner = ''
    def __init__(self,id:int,name:str,desc:str,choice:str,owner:str) -> None:
        self.id:int = id
        self.name:str = name
        self.desc:str = desc.split("|")[0]
        if len(desc.split("|"))==1:self.diffDesc=['']
        else:self.diffDesc:list[str] = desc.split("|")[1].split(" ")
        self.choice:list[str] = choice.split(" ")
        self.owner:str = owner
    @staticmethod
    def search_by_id(gid,id):
        conn = sqlite3.connect(f"data/Neargo/{gid}.db")
        cur = conn.cursor()
        data = cur.execute(f"select * from position where id={id};").fetchone()
        cur.close()
        if not data:return Position(0,None,None,None,None)
        else:return Position(id,data[1],data[2],data[3],data[4])
class ncGroup(Group):
    def __init__(self,gid) -> None:
        self.gid = gid
        if not os.path.exists('data/INDEX'):
            os.makedirs('data/INDEX')
        conn = sqlite3.connect(f"data/INDEX/{self.gid}.db")
        cur = conn.cursor()
        user = cur.execute(f"select * from user;").fetchall()
        conn.close()
        if not os.path.exists('data/Neargo'):
            os.makedirs('data/Neargo')
        conn = sqlite3.connect(f"data/Neargo/{self.gid}.db")
        cur = conn.cursor()
        cur.execute("create table if not exists user(uid TEXT PRIMARY KEY,position TEXT,crime REAL,inventory TEXT)")
        data = cur.execute("PRAGMA table_info(user)").fetchall()
        findFalg=False
        for d in data:
            if 'inventory'==d[1]:
                findFalg=True
        if not findFalg:
            cur.execute("alter table user add column inventory TEXT")
        for u in user:
            cur.execute(f"INSERT OR IGNORE INTO user(uid,position,crime,inventory) VALUES({u[0]},1,0,',')")
        data = cur.execute("PRAGMA table_info(position)").fetchall()
        if not data:
            cur.execute("create table if not exists position(id INTEGER PRIMARY KEY,name TEXT,desc TEXT,choice TEXT,owner TEXT)")
        postions = []
        pcsv = pandas.read_csv(os.path.dirname(__file__)+"/positions.csv",encoding="utf-8",header=0)
        for p in pcsv.values:
            postions.append(p.tolist())
        for p in postions:
            cur.execute(f"INSERT OR IGNORE INTO position values({p[0]},'{p[1]}','{p[2]}','{p[3]}','{p[4]}')")
            conn.commit()
        data = cur.execute("PRAGMA table_info(item)").fetchall()
        if not data:
            cur.execute("create table if not exists item(id INTEGER PRIMARY KEY,name TEXT,desc TEXT,price REAL)")
        items = []
        icsv = pandas.read_csv(os.path.dirname(__file__)+"/items.csv",encoding="utf-8",header=0)
        for i in icsv.values:
            items.append(i.tolist())
        for i in items:
            cur.execute(f"INSERT OR IGNORE INTO item values({i[0]},'{i[1]}','{i[2]}',{i[3]})")
            conn.commit()
        data = cur.execute(f"select * from user;").fetchall()
        for d in data:
            if not d[3]:
                cur.execute(f"UPDATE user SET inventory='' where uid='{d[0]}';")
        conn.commit()
        cur.close()

    def find_user(self,qid):
        conn = sqlite3.connect(f"data/INDEX/{self.gid}.db")
        cur = conn.cursor()
        u = cur.execute(f"select uid,money from user where qid='{qid}';").fetchone()
        conn.close()
        conn = sqlite3.connect(f"data/Neargo/{self.gid}.db")
        cur = conn.cursor()
        data = cur.execute(f"select * from user where uid='{u[0]}';").fetchone()
        conn.close()
        if not data:
            return False
        else:
            return ncUser(self,data[0],u[1],data[1],data[2],data[3])
    # def draw_map(self):
    #     if not os.path.exists('data/Monopoly/user/'+self.gid):
    #         os.makedirs('data/Monopoly/user/'+self.gid)
    #     avaters = os.listdir('data/Monopoly/user/'+self.gid)
    #     for k,f in enumerate(avaters):
    #         avaters[k] = os.path.splitext(f)[0].split("_")
    #         if int(avaters[k][1])-time.time()>=3600000:
    #             image_url= "https://q1.qlogo.cn/g?b=qq&nk="+str(avaters[k][0])+"&s=640"
    #             print(image_url)
    #             proxies = {"http": "http://127.0.0.1:7890","https": "http://127.0.0.1:7890",}
    #             urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    #             try:
    #                 res = requests.get(image_url,verify=False,proxies=proxies)
    #             except:
    #                 res = requests.get(image_url,verify=False)
    #             with open(f'data/Monopoly/user/{self.gid}/{avaters[k][0]}_{int(time.time())}.png', 'wb') as f:
    #                 f.write(res.content)
    #     conn = sqlite3.connect(f"data/INDEX/{self.gid}.db")
    #     cur = conn.cursor()
    #     data = cur.execute(f"select * from map;").fetchall()
    #     mapSrc = PILIMG.open(os.path.dirname(__file__)+'/map.png').convert('RGB')
    #     mapImg = PILIMG.new("RGB",(mapSrc.size[0]*100,mapSrc.size[1]*100),(255,255,255))
    #     draw = ImageDraw.Draw(mapImg)
    #     for d in data:
    #         fill = ChunkType[d[4]]
    #         if fill.name =="roadEvent":
    #             fill = ChunkType["road"]
    #         draw.rounded_rectangle([d[1]*100,d[2]*100,d[1]*100+100,d[2]*100+100],radius=20,fill=fill.value,width=3)
    #         us = cur.execute(f"select * from user where position={d[0]};").fetchall()
    #         thisLine = 0
    #         j=i=0
    #         for u in us:
    #             avater = None
    #             for a in avaters:
    #                 if a[0]==u[1]:
    #                     avater = PILIMG.open(f'data/Monopoly/user/{self.gid}/{a[0]}_{a[1]}.png').convert("RGB")
    #             if not avater:
    #                 image_url= "https://q1.qlogo.cn/g?b=qq&nk="+str(u[1])+"&s=640"
    #                 print(image_url)
    #                 proxies = {"http": "http://127.0.0.1:7890","https": "http://127.0.0.1:7890",}
    #                 urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    #                 try:
    #                     res = requests.get(image_url,verify=False,proxies=proxies)
    #                 except:
    #                     res = requests.get(image_url,verify=False)
    #                 with open(f'data/Monopoly/user/{self.gid}/{u[1]}_{int(time.time())}.png', 'wb') as f:
    #                     f.write(res.content)
    #                 avater = PILIMG.open(f'data/Monopoly/user/{self.gid}/{u[1]}_{int(time.time())}.png').convert("RGB")
    #             if thisLine==3:
    #                 thisLine=0
    #                 j+=1
    #                 i-=3
    #             mapImg.paste(avater.resize((32,32)),(d[1]*100+10+i*32,d[2]*100+10+j*32))
    #             thisLine+=1
    #             i+=1
    #     mapImg.save('data/map.png')
class Item():
    def __init__(self,id,name,desc,price) -> None:
        self.id,self.name,self.desc,self.price = id,name,desc,price
    @staticmethod
    def search_by_name(gid,name):
        conn = sqlite3.connect(f"data/Neargo/{gid}.db")
        cur = conn.cursor()
        data = cur.execute(f"select * from item where name='{name}';").fetchone()
        cur.close()
        if not data:return Item(0,None,None,None)
        else:return Item(data[0],name,data[2],data[3])

class ncUser(User):
    crime =0
    def __init__(self, group:ncGroup,uid,money,positionID,crime,inventory:str) -> None:
        self.group = group
        self.uid = uid
        self.money = money
        self.position = Position.search_by_id(self.group.gid,positionID)
        self.crime:int = crime
        self.inventory:list[str] = []
        self.leftHand = self.rightHand = ''
        inventory = inventory.split(",")
        for i in inventory:
            i = i.split(":")
            if i[0] == "LH":self.leftHand = i[1]
            elif i[0]=="RH":self.rightHand = i[1]
            else:
                if i[0] != '':self.inventory.append(i[0])
    def add_crime(self,crime):
        self.crime += crime
        conn = sqlite3.connect(f"data/Neargo/{self.group.gid}.db")
        cur = conn.cursor()
        cur.execute(f"UPDATE user SET crime={self.crime} where uid='{self.uid}';")
        conn.commit()
        conn.close()
    def add_item(self,itemID):
        conn = sqlite3.connect(f"data/Neargo/{self.group.gid}.db")
        cur = conn.cursor()
        name = cur.execute(f"select name from item where id={itemID};").fetchone()[0]
        self.inventory.append(name)
        inventory = f"LH:{self.leftHand},RH:{self.rightHand},"+",".join(self.inventory)
        cur.execute(f"UPDATE user SET inventory='{inventory}' where uid='{self.uid}';")
        conn.commit()
        conn.close()
    def move_to(self,pid):
        self.position = Position.search_by_id(self.group.gid,pid)
        conn = sqlite3.connect(f"data/Neargo/{self.group.gid}.db")
        cur = conn.cursor()
        cur.execute(f"UPDATE user SET position='{self.position.id}' where uid='{self.uid}';")
        conn.commit()
        conn.close()
        return ""
    def buy_item(self,itemID):
        conn = sqlite3.connect(f"data/Neargo/{self.group.gid}.db")
        cur = conn.cursor()
        price = cur.execute(f"select price from item where id={itemID};").fetchone()[0]
        if self.money-price>=0:
            self.add_money(-price)
            self.add_item(itemID)
        conn.commit()
        conn.close()
        return ''