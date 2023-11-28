from nonebot import require
from PIL import Image as PILIMG
from PIL import ImageDraw
import os,numpy,random,requests,urllib3,time
from enum import Enum

require("Index_user_management")
require("wordle_zhenxia")

from ..Index_user_management import *
from ..wordle_zhenxia import Wordle

class ChunkType(Enum):
    estate = (0,128,0)
    road = (128,128,128)
    cityHall = (255,255,0)
    roadEvent = (33,191,197)
    bar = (255,0,255)
    salveShop = (255,0,128)
    roadGate = (0,255,0)
    gate = (255,0,0)
    null = (255,255,255)
class ChunkName(Enum):
    estate = '空地产'
    road = '道路'
    cityHall = '市政厅'
    roadEvent = '道路'
    bar = '酒吧'
    salveShop = '海伦娜精品店'
    roadGate = '门前大道'
    gate = '城门'
    null = ''
class Chunk():
    cid=x=y = 0
    chunkName = chunkType = owner = ''
    @staticmethod
    def search_by_xy(gid,x,y):
        conn = sqlite3.connect(f"data/INDEX/{gid}.db")
        cur = conn.cursor()
        data = cur.execute(f"select * from map where x={x} and y={y};").fetchone()
        cur.close()
        if not data:
            p = Chunk()
            p.cid = None
            p.x = None
            p.y = None
            p.chunkName = None
            p.chunkType = None
            p.owner = None
        else:
            p = Chunk()
            p.cid = data[0]
            p.x = data[1]
            p.y = data[2]
            p.chunkName = data[3]
            p.chunkType = data[4]
            p.owner = data[5]
        return p
    @staticmethod
    def search_by_id(gid,cid):
        conn = sqlite3.connect(f"data/INDEX/{gid}.db")
        cur = conn.cursor()
        data = cur.execute(f"select * from map where cid={cid};").fetchone()
        cur.close()
        if not data:
            p = Chunk()
            p.cid = None
            p.x = None
            p.y = None
            p.chunkName = None
            p.chunkType = None
            p.owner = None
        else:
            p = Chunk()
            p.cid = data[0]
            p.x = data[1]
            p.y = data[2]
            p.chunkName = data[3]
            p.chunkType = data[4]
            p.owner = data[5]
        return p
    def can_walk(self):
        return self.chunkType=='road' or self.chunkType=='roadEvent' or self.chunkType=='roadGate' or self.chunkType=='cityHall' or self.chunkType=='bar' or self.chunkType=='salveShop'
class monoGroup(Group):
    def __init__(self,gid) -> None:
        self.gid = gid
        if not os.path.exists('data/INDEX'):
            os.makedirs('data/INDEX')
        conn = sqlite3.connect(f"data/INDEX/{self.gid}.db")
        cur = conn.cursor()
        cur.execute("create table if not exists user(uid TEXT PRIMARY KEY,qid TEXT,nickname TEXT,money REAL)")
        data = cur.execute("PRAGMA table_info(user)").fetchall()
        findFalg=False
        for d in data:
            if 'position'==d[1]:
                findFalg=True
        if not findFalg:
            cur.execute("alter table user add column position INTEGER")
        findFalg=False
        for d in data:
            if 'crime'==d[1]:
                findFalg=True
        if not findFalg:
            cur.execute("alter table user add column crime REAL")
        findFalg=False
        for d in data:
            if 'state'==d[1]:
                findFalg=True
        if not findFalg:
            cur.execute("alter table user add column state INTEGER")
        data = cur.execute("PRAGMA table_info(map)").fetchall()
        if not data:
            cityHallKey = 0
            cur.execute("create table if not exists map(cid INTEGER PRIMARY KEY,x INTEGER,y INTEGER,chunkName TEXT,chunkType TEXT,owner TEXT)")
            map = PILIMG.open(os.path.dirname(__file__)+'/map.png').convert('RGB')
            map = numpy.asarray(map).tolist()
            k=0
            for i in range(len(map)):
                for j in range(len(map[i])):
                    type = ChunkType(tuple(map[i][j]))
                    if type.name=='null':continue
                    cur.execute(f"insert into map values({k},{j},{i},'{ChunkName[type.name].value}','{type.name}','city')")
                    conn.commit()
                    if type.name == 'cityHall':
                        cityHallKey = k
                    k+=1
        cityHallKey = cur.execute(f"select cid from map where chunkType='cityHall';").fetchone()[0]
        print(cityHallKey)
        data = cur.execute(f"select * from user;").fetchall()
        for d in data:
            if not d[4]:
                cur.execute(f"UPDATE user SET position={int(cityHallKey)} where uid='{d[0]}';")
            if not d[5]:
                cur.execute(f"UPDATE user SET crime=0 where uid='{d[0]}';")
            if not d[6]:
                cur.execute(f"UPDATE user SET state=0 where uid='{d[0]}';")
        conn.commit()
        cur.close()

    def new_user(self,qid,nickname):
        if self.find_user(qid):
            return False
        conn = sqlite3.connect(f"data/INDEX/{self.gid}.db")
        cur = conn.cursor()
        data = cur.execute(f"select * from user;").fetchall()
        cityHallKey = cur.execute(f"select cid from map where chunkType='cityHall';").fetchone()[0]
        id = 1
        for item in data:
            if id<=int(item[0]):
                id = int(item[0])+1
        cur.execute(
            f"insert into user(uid,qid,nickname,money,position,crime,state) values({id},'{qid}','{nickname}',{10},{cityHallKey},0,0);"
            )
        conn.commit()
        cur.close()

    def find_user(self,qid):
        conn = sqlite3.connect(f"data/INDEX/{self.gid}.db")
        cur = conn.cursor()
        data = cur.execute(f"select * from user where qid='{qid}';").fetchall()
        conn.close()
        if not data:
            return False
        else:
            return monoUser(self,data[0][0],data[0][2],data[0][3],data[0][4],data[0][5],data[0][6])
    def draw_map(self):
        if not os.path.exists('data/Monopoly/user/'+self.gid):
            os.makedirs('data/Monopoly/user/'+self.gid)
        avaters = os.listdir('data/Monopoly/user/'+self.gid)
        for k,f in enumerate(avaters):
            avaters[k] = os.path.splitext(f)[0].split("_")
            if int(avaters[k][1])-time.time()>=3600000:
                image_url= "https://q1.qlogo.cn/g?b=qq&nk="+str(avaters[k][0])+"&s=640"
                print(image_url)
                proxies = {"http": "http://127.0.0.1:7890","https": "http://127.0.0.1:7890",}
                urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
                try:
                    res = requests.get(image_url,verify=False,proxies=proxies)
                except:
                    res = requests.get(image_url,verify=False)
                with open(f'data/Monopoly/user/{self.gid}/{avaters[k][0]}_{int(time.time())}.png', 'wb') as f:
                    f.write(res.content)
        conn = sqlite3.connect(f"data/INDEX/{self.gid}.db")
        cur = conn.cursor()
        data = cur.execute(f"select * from map;").fetchall()
        mapSrc = PILIMG.open(os.path.dirname(__file__)+'/map.png').convert('RGB')
        mapImg = PILIMG.new("RGB",(mapSrc.size[0]*100,mapSrc.size[1]*100),(255,255,255))
        draw = ImageDraw.Draw(mapImg)
        for d in data:
            fill = ChunkType[d[4]]
            if fill.name =="roadEvent":
                fill = ChunkType["road"]
            draw.rounded_rectangle([d[1]*100,d[2]*100,d[1]*100+100,d[2]*100+100],radius=20,fill=fill.value,width=3)
            us = cur.execute(f"select * from user where position={d[0]};").fetchall()
            thisLine = 0
            j=i=0
            for u in us:
                avater = None
                for a in avaters:
                    if a[0]==u[1]:
                        avater = PILIMG.open(f'data/Monopoly/user/{self.gid}/{a[0]}_{a[1]}.png').convert("RGB")
                if not avater:
                    image_url= "https://q1.qlogo.cn/g?b=qq&nk="+str(u[1])+"&s=640"
                    print(image_url)
                    proxies = {"http": "http://127.0.0.1:7890","https": "http://127.0.0.1:7890",}
                    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
                    try:
                        res = requests.get(image_url,verify=False,proxies=proxies)
                    except:
                        res = requests.get(image_url,verify=False)
                    with open(f'data/Monopoly/user/{self.gid}/{u[1]}_{int(time.time())}.png', 'wb') as f:
                        f.write(res.content)
                    avater = PILIMG.open(f'data/Monopoly/user/{self.gid}/{u[1]}_{int(time.time())}.png').convert("RGB")
                if thisLine==3:
                    thisLine=0
                    j+=1
                    i-=3
                mapImg.paste(avater.resize((32,32)),(d[1]*100+10+i*32,d[2]*100+10+j*32))
                thisLine+=1
                i+=1
        mapImg.save('data/map.png')
class monoUserState(Enum):
    normal = 0
    cityJailed = 1
    illegalJailed = 2

class monoUser(User):
    position = Chunk
    crime =0
    def __init__(self, group: Group,uid,nickname,money,positionID,crime,state) -> None:
        self.group = group
        self.uid = uid
        self.nickname = nickname
        self.money = money
        self.position = Chunk.search_by_id(self.group.gid,positionID)
        self.crime = crime
        self.state = monoUserState(state)
    def get_near_chunk(self):
        up = Chunk.search_by_xy(self.group.gid,self.position.x,self.position.y-1)
        down = Chunk.search_by_xy(self.group.gid,self.position.x,self.position.y+1)
        left = Chunk.search_by_xy(self.group.gid,self.position.x-1,self.position.y)
        right = Chunk.search_by_xy(self.group.gid,self.position.x+1,self.position.y)
        return {'up':up,'down':down,'left':left,'right':right}

    def move(self) -> Chunk:
        if self.money-2<0:
            return False
        else:
            self.add_money(-2)
            dice = random.randrange(1,6)
            while(dice>0):
                nears = self.get_near_chunk()
                if self.position.x<5:
                    if nears['up'].can_walk():self.position = nears['up'];dice-=1;continue
                    if self.position.y<4:
                        if nears['right'].can_walk():self.position = nears['right'];dice-=1;continue
                    else:
                        if nears['left'].can_walk():self.position = nears['left'];dice-=1;continue
                else:
                    if nears['down'].can_walk():self.position = nears['down'];dice-=1;continue
                    if self.position.y<4:
                        if nears['right'].can_walk():self.position = nears['right'];dice-=1;continue
                    else:
                        if nears['left'].can_walk():self.position = nears['left'];dice-=1;continue
                dice-=1
            conn = sqlite3.connect(f"data/INDEX/{self.group.gid}.db")
            cur = conn.cursor()
            cur.execute(f"UPDATE user SET position='{self.position.cid}' where uid='{self.uid}';")
            conn.commit()
            conn.close()
            return self.position
    def move_to(self,cid):
        self.position.cid = cid
        conn = sqlite3.connect(f"data/INDEX/{self.group.gid}.db")
        cur = conn.cursor()
        cur.execute(f"UPDATE user SET position='{self.position.cid}' where uid='{self.uid}';")
        conn.commit()
        conn.close()
    def exit_room(self):
        nears = self.get_near_chunk()
        for k in nears:
            if nears[k].chunkType=='gate':
                self.move_to(nears[k].cid)
                return True
        return False
    def enter_room(self):
        if self.position.chunkType!='gate':
            return False
        else:
            nears = self.get_near_chunk()
            for k in nears:
                if nears[k].can_walk:
                    self.move_to(nears[k].cid)
                    return True
    def add_crime(self,crime):
        self.crime += crime
        conn = sqlite3.connect(f"data/INDEX/{self.group.gid}.db")
        cur = conn.cursor()
        cur.execute(f"UPDATE user SET crime={self.crime} where uid='{self.uid}';")
        conn.commit()
        conn.close()
    def change_state(self,state):
        self.state = monoUserState(state)
        conn = sqlite3.connect(f"data/INDEX/{self.group.gid}.db")
        cur = conn.cursor()
        cur.execute(f"UPDATE user SET state={state} where uid='{self.uid}';")
        conn.commit()
        conn.close()

class Enermy():
    def __init__(self,type,target:monoUser,participate:list,object:Wordle) -> None:
        self.type = type
        self.target = target
        self.participate = participate
        self.object = object