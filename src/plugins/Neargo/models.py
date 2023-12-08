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
    def __init__(self,id:str,name:str,desc:str,choice:str,owner:str,players:list[User]) -> None:
        self.id:str = id
        self.name:str = name
        self.desc:str = desc.split("|")[0]
        if len(desc.split("|"))==1:self.diffDesc=['']
        else:self.diffDesc:list[str] = desc.split("|")[1].split(" ")
        self.choice:list[str] = choice.split(" ")
        self.owner:str = owner
        self.player:list[User] = players
    def get_upper_position(self,uid):
        for c in self.choice:
            if '离开' in c:
                upperID=re.search(r"(?<=离开\|move_to:).*",c).group()
                return Position.search_by_id(upperID,uid)
        return Position(0,'','','','',[])
    def update(self):
        conn = sqlite3.connect(f"data/INDEX/Neargo.db")
        cur = conn.cursor()
        cur.execute(
            f"UPDATE position SET name='{self.name}',desc='{self.desc}|{' '.join(self.diffDesc)}',choice='{' '.join(self.choice)}',owner='{self.owner}' where id='{self.id}';")
        conn.commit()
        conn.close()
    def delete_position(self):
        conn = sqlite3.connect(f"data/INDEX/Neargo.db")
        cur = conn.cursor()
        cur.execute(f"DELETE from position where id='{self.id}';")
        conn.commit()
        conn.close()
    @staticmethod
    def search_by_id(id,uid):
        conn = sqlite3.connect(f"data/INDEX/Neargo.db")
        cur = conn.cursor()
        data = cur.execute(f"select * from position where id='{id}';").fetchone()
        askUser = User.find_user_by_uid(uid)
        us = []
        users = cur.execute(f"select uid,position from user").fetchall()
        for u in users:
            user = User.find_user_by_uid(u[0])
            for g in askUser.groups:
                if g in user.groups and u[1]==id:us.append(user)
                break
        cur.close()
        if not data:return Position(0,None,None,None,None,None)
        else:return Position(id,data[1],data[2],data[3],data[4],us)
    @staticmethod
    def new_position(id,name,desc,choice,owner):
        conn = sqlite3.connect(f"data/INDEX/Neargo.db")
        cur = conn.cursor()
        cur.execute(f"INSERT INTO position values('{id}','{name}','{desc}','{choice}','{owner}')")
        conn.commit()
        conn.close()
    @staticmethod
    def get_all_position(uid):
        conn = sqlite3.connect(f"data/INDEX/Neargo.db")
        cur = conn.cursor()
        data = cur.execute(f"select id from position").fetchall()
        conn.commit()
        conn.close()
        ps = []
        for d in data:
            ps.append(Position.search_by_id(d[0],uid))
        return ps
def Neargo_init():
    if not os.path.exists('data/Neargo'):
            os.makedirs('data/Neargo')
    conn = sqlite3.connect(f"data/INDEX/Neargo.db")
    cur = conn.cursor()
    cur.execute("create table if not exists user(uid TEXT PRIMARY KEY,position TEXT,crime REAL,inventory TEXT,HP REAL,AP REAL)")
    data = cur.execute("PRAGMA table_info(position)").fetchall()
    if not data:
        cur.execute("create table if not exists position(id TEXT PRIMARY KEY,name TEXT,desc TEXT,choice TEXT,owner TEXT)")
    postions = []
    pcsv = pandas.read_csv(os.path.dirname(__file__)+"/positions.csv",encoding="utf-8",header=0)
    for p in pcsv.values:
        postions.append(p.tolist())
    for p in postions:
        cur.execute(f"INSERT OR IGNORE INTO position values('{p[0]}','{p[1]}','{p[2]}','{p[3]}','{p[4]}')")
        conn.commit()
    data = cur.execute("PRAGMA table_info(item)").fetchall()
    if not data:
        cur.execute("create table if not exists item(id TEXT PRIMARY KEY,name TEXT,desc TEXT,choice TEXT,formula TEXT)")
    items = []
    icsv = pandas.read_csv(os.path.dirname(__file__)+"/items.csv",encoding="utf-8",header=0)
    for i in icsv.values:
        items.append(i.tolist())
    for i in items:
        cur.execute(f"INSERT OR IGNORE INTO item values('{i[0]}','{i[1]}','{i[2]}','{i[3]}','{i[4]}')")
        conn.commit()
    conn.commit()
    cur.close()

class Item():
    def __init__(self,id,name,desc,choice:str,formula) -> None:
        self.id,self.name,self.desc,self.formula = id,name,desc,formula
        self.battleSkill = choice.split("/")[-1].split(" ")
        self.choice = choice.split("/")[0].split(" ")
    @staticmethod
    def search_by_id(id):
        conn = sqlite3.connect(f"data/INDEX/Neargo.db")
        cur = conn.cursor()
        data = cur.execute(f"select * from item where id='{id}';").fetchone()
        cur.close()
        if not data:return Item(0,'','','','')
        else:return Item(data[0],data[1],data[2],data[3],data[4])
    @staticmethod
    def new_item(id,name,desc,choice,formula):
        conn = sqlite3.connect(f"data/INDEX/Neargo.db")
        cur = conn.cursor()
        cur.execute(f"INSERT INTO position values('{id}','{name}','{desc}','{choice}','{formula}')")
        conn.commit()
        conn.close()

    def update(self):
        conn = sqlite3.connect(f"data/INDEX/Neargo.db")
        cur = conn.cursor()
        cur.execute(
            f"UPDATE item SET name='{self.name}',desc={self.desc},choice='{' '.join(self.choice)}/{''.join(self.battleSkill)}',formula='{self.formula}' where uid='{self.id}';")
        conn.commit()
        conn.close()

class ncUser(User):
    crime =0
    def __init__(self,groups:list,uid,money,positionID,crime,inventory:str,HP,AP) -> None:
        Neargo_init()
        self.groups,self.uid,self.money = groups,uid,money
        self.position = Position.search_by_id(positionID,uid)
        self.crime,self.HP,self.AP = crime,HP,AP
        self.inventory:list[str] = []
        self.leftHand = self.rightHand = ''
        inventory = inventory.split(",")
        for i in inventory:
            i = i.split("|")
            if len(i)==1:i.append('')
            if i[0] == "LH":self.leftHand = i[1]
            elif i[0]=="RH":self.rightHand = i[1]
            else:
                if i[0] != '':self.inventory.append(i[0])
    @staticmethod
    def find_user(qid):
        u = User.find_user_by_qid(qid)
        if not u:
            return 'NoUser'
        conn = sqlite3.connect(f"data/INDEX/Neargo.db")
        cur = conn.cursor()
        data = cur.execute(f"select * from user where uid='{u.uid}';").fetchone()
        if not data:
            cur.execute(f"INSERT OR IGNORE INTO user(uid,position,crime,inventory,HP,AP) VALUES({u.uid},'PublicSquare',0,',',100,100)")
            conn.commit()
            conn.close()
            return ncUser(u.groups,u.uid,u.money,'PublicSquare',0,',')
        conn.close()
        return ncUser(u.groups,u.uid,u.money,data[1],data[2],data[3],data[4],data[5])

    def update(self):
        conn = sqlite3.connect(f"data/INDEX/Neargo.db")
        cur = conn.cursor()
        inventory = ','.join(self.inventory)
        cur.execute(
            f"UPDATE user SET position='{self.position.id}',crime={self.crime},inventory='LH|{self.leftHand},RH|{self.rightHand},{inventory}',HP={self.HP},AP={self.AP} where uid='{self.uid}';")
        conn.commit()
        conn.close()
    def add_crime(self,crime):
        self.crime += crime
        self.update()
    def add_item(self,itemID):
        name = Item.search_by_id(itemID).name
        self.inventory.append(name+':'+itemID)
        self.update()
    def delete_item(self,itemID):
        name = Item.search_by_id(itemID).name
        self.inventory.pop(self.inventory.index(name+':'+itemID))
        self.update()
    def move_to(self,pid):
        if '- LOCKED' in self.position.name:
            if self.position.owner!=self.uid and self.position.get_upper_position(self.uid).owner!=self.uid:
                return "房间被锁住了"
        target = Position.search_by_id(pid,self.uid)
        if '- LOCKED' in target.name:
            if target.owner!=self.uid and target.get_upper_position(self.uid).owner!=self.uid:
                return "房间被锁住了"
        if self.AP>=5:self.AP-=5
        else:return '你太累了，走不动了……'
        self.position = target
        self.update()
        return ""
    def buy_item(self,itemID,price):
        name = Item.search_by_id(itemID).name
        if self.money-float(price)>=0:
            self.add_money(-float(price))
            if self.position.owner!="city":
                User.find_user_by_uid(self.position.owner).add_money(float(price))
                for c in self.position.choice:
                    if itemID in c:self.position.choice.pop(self.position.choice.index(c));break
                self.position.update()
            self.add_item(itemID)
            return f'你购买了{name}'
        else:return f'你买不起{name}'
    def buy_house(self,rooms:int):
        rooms = int(rooms)
        canBuy = False
        if self.money>=(rooms-2)*200+600:canBuy=True
        if canBuy:
            upper = self.position.get_upper_position(self.uid)
            restHouse = int(re.search(r"(?<=剩余房屋：)[0-9]",self.position.desc).group())
            if int(restHouse)==0:return '没有房了！'
            self.position.desc = self.position.desc.replace(f"剩余房屋：{restHouse}",f"剩余房屋：{restHouse-1}")
            self.add_money(-((rooms-2)*200+600))
            self.position.update()
            name = User.find_user_by_uid(self.uid).nickname
            choice = ''
            for i in range(rooms):
                Position.new_position(f"{upper.id}_Apartment_{restHouse}_{i}",f"房间{i}",f"房间{i}",f"离开|move_to:{upper.id}_Apartment_{restHouse}",self.uid)
                choice+=f'房间{i}|move_to:{upper.id}_Apartment_{restHouse}_{i} '
            Position.new_position(f"{upper.id}_Apartment_{restHouse}",f"{name}的公寓",f"{name}的公寓",f"{choice}离开|move_to:{upper.id}",self.uid)
            upper.choice.append(f"{name}的公寓|move_to:{upper.id}_Apartment_{restHouse}")
            upper.update()
            return str('你买下了这栋房子')
        else:return str('你买不起这栋房子')
    def divideRooms(self):
        if self.uid!=self.position.owner:return '你不是这间房子的主人！'
        else:
            conn = sqlite3.connect(f"data/INDEX/Neargo.db")
            cur = conn.cursor()
            rooms = int(re.search(r"(?<=有着).*?(?=间房间)",self.position.desc).group())
            c=''
            for i in range(rooms):
                cur.execute(f"INSERT INTO position values('{self.position.id}_{i}','房间{i}','一间空房间','离开|move_to:{self.position.id}','{self.uid}')")
                c += f'靠近房间{i}|move_to:{self.position.id}_{i} '
            c += ' '.join(self.position.choice)
            c = re.sub("分割房间|divideRooms ","",c)
            cur.execute(f"UPDATE position SET choice='{c}' where id='{self.position.id}';")
            conn.commit()
            conn.close()
            return '你分割了房间'
    def open_inventory(self):
        fromP = self.position.id.split("/")[-1]
        if 'inventory' in self.position.id:
            self.close_inventory()
            self.open_inventory()
            return ''
        if self.leftHand=='':leftHand=['','']
        else:leftHand = self.leftHand.split(":")
        if self.rightHand=='':rightHand=['','']
        else:rightHand = self.rightHand.split(":")
        text = f'生命值：{int(self.HP)}/100\n体力值：{int(self.AP)}/100\n左手：'+leftHand[0]+'；右手：'+rightHand[0]
        if self.position.owner!='city':text+=f"\n当前房间所属：{User.find_user_by_uid(self.position.owner).nickname}"
        choice = '打开背包|open_backage '
        if self.position.owner==self.uid or self.position.get_upper_position(self.uid).owner==self.uid:
            for u in self.position.player:
                if u.uid==self.uid:continue
                elif u.uid!=self.position.owner:choice += f"将此房间给{u.nickname}|give_room:{self.position.id};{u.uid} "
            if self.position.get_upper_position(self.uid).owner==self.uid and self.position.owner!=self.uid:choice += f"收回这间房间|give_room:{self.position.id};{self.uid} "
            choice += f"房间改名|rename_position:{self.position.id} 房间描述更改|redesc_position:{self.position.id} "
            if "- LOCKED" in self.position.name:choice += f"房间解锁|lock_room:{self.position.id} "
            else:choice += f"房间上锁|lock_room:{self.position.id} "
        try:Position.new_position(f"{self.uid}/inventory/{fromP}","你的物品栏",text,f"查看左手|check_item:{leftHand[1]} 查看右手|check_item:{rightHand[1]} {choice}关闭物品栏|close_inventory",f'{self.uid}')
        except:pass
        self.move_to(f'{self.uid}/inventory/{fromP}')
        return ""
    def close_inventory(self):
        fromP = self.position.id.split("/")[-1]
        self.position.delete_position()
        self.move_to(fromP)
        return ""
    def open_backage(self):
        fromP = self.position.id.split("/")[-1]
        choice = ''
        for i in self.inventory:
            if i=='':i=['','']
            else:i=i.split(":")
            choice += f"{i[0]}|check_item:{i[1]} "
        try:Position.new_position(f'{self.uid}/inventory/backage/{fromP}','你的背包',"",f'{choice}关闭背包|close_backage',self.uid)
        except:pass
        self.move_to(f'{self.uid}/inventory/backage/{fromP}')
        return ""
    def close_backage(self):
        fromP = self.position.id.split("/")[-1]
        self.position.delete_position()
        self.open_inventory()
        self.move_to(f"{self.uid}/inventory/{fromP}")
        return ""
    def check_item(self,id):
        fromP = self.position.id.split("/")[-1]
        item = Item.search_by_id(id)
        choice = ' '.join(item.choice)+" "
        if 'inventory' in self.position.id:
            invfromP = self.position.id.split("/")[-1]
            upper = Position.search_by_id(invfromP,self.uid)
            choice += f'放在此处|put_item '
            for i in upper.player:
                if i.uid==self.uid:continue
                choice += f"给{i.nickname}|give_item:{i.uid} "
            Position.new_position(f'{self.uid}/check_item/{item.id}/inventory/{fromP}',f'~{item.name}~',item.desc,f'装备左手|equip_item:left;{item.id} 装备右手|equip_item:right;{item.id} {choice}关闭|close_item_check',self.uid)
            self.move_to(f'{self.uid}/check_item/{item.id}/inventory/{fromP}')
        else:
            choice += f"放入背包|get_item:{fromP} "
            Position.new_position(f'{self.uid}/check_item/{item.id}/{fromP}',f'~{item.name}~',item.desc,f'装备左手|equip_item:left;{item.id} 装备右手|equip_item:right;{item.id} {choice}关闭|close_item_check',self.uid)
            self.move_to(f'{self.uid}/check_item/{item.id}/{fromP}')
        return ""
    def close_item_check(self):
        fromP = self.position.id.split("/")[-1]
        self.position.delete_position()
        if 'inventory' in self.position.id:
            self.move_to(f'{self.uid}/inventory/backage/{fromP}')
        else:self.move_to(fromP)
        return ""
    def give_item(self,uid):
        itemID = self.position.id.split("/")[2]
        u = User.find_user_by_uid(uid).qid
        u = ncUser.find_user(u)
        self.delete_item(itemID)
        u.add_item(itemID)
        self.close_item_check()
        self.close_backage()
        self.open_backage()
        return '你把物品给了Ta'
    def put_item(self):
        itemID = self.position.id.split("/")[2]
        positionID = self.position.id.split("/")[-1]
        item = Item.search_by_id(itemID)
        self.delete_item(itemID)
        p:Position = Position.search_by_id(positionID,self.uid)
        p.choice.insert(0,f"{item.name}|check_item:{itemID}")
        p.update()
        self.close_item_check()
        self.close_backage()
        self.open_backage()
        return f"你放下了{item.name}"
    def get_item(self,positionID):
        itemID = self.position.id.split("/")[2]
        item = Item.search_by_id(itemID)
        self.add_item(itemID)
        p:Position = Position.search_by_id(positionID,self.uid)
        p.choice.pop(p.choice.index(f"{item.name}|check_item:{itemID}"))
        p.update()
        self.close_item_check()
        return f"你捡起了{item.name}"
    def give_room(self,roomID,uid):
        p:Position = Position.search_by_id(roomID,self.uid)
        p.owner = uid
        p.update()
        self.open_inventory()
        return "你将这间房间给了Ta"
    def rename_position(self,positionID,newName):
        position:Position = Position.search_by_id(positionID,self.uid)
        oldname = position.name
        position.name = newName
        position.update()
        ps:list[Position] = Position.get_all_position(self.uid)
        for p in ps:
            for c in p.choice:
                if positionID in c:
                    p.choice[p.choice.index(c)] = c.replace(f"{oldname}|move_to:{positionID}",f"{newName}|move_to:{positionID}")
                    p.update()
        self.close_inventory()
        return '你修改了房间名字'
    def redesc_position(self,positionID,new):
        p:Position = Position.search_by_id(positionID,self.uid)
        p.desc = new
        p.update()
        self.close_inventory()
        return '你修改了房间描述'
    def lock_room(self,id):
        target = Position.search_by_id(id,self.uid)
        if " - LOCKED" not in target.name:
            target.name += " - LOCKED"
        else:
            target.name = target.name.replace(' - LOCKED','')
        target.update()
        self.close_inventory()
        return '你切换了房间上锁模式'
    def eat_food(self,hp,ap):
        hp=float(hp);ap=float(ap)
        itemID = self.position.id.split("/")[2]
        if self.HP+hp<=100 and self.AP+ap<=100:self.HP += hp;self.AP += ap
        if 'inventory' in self.position.id:self.delete_item(itemID)
        else:
            fromP = self.position.id.split("/")[-1]
            fromP = Position.search_by_id(fromP,self.uid)
            for c in fromP.choice:
                if itemID in c:fromP.choice.pop(fromP.choice.index(c));break
            fromP.update()
        self.update()
        self.close_item_check()
        if 'inventory' in self.position.id:self.open_inventory();self.open_backage()
        return f"你吃了{Item.search_by_id(itemID).name}"