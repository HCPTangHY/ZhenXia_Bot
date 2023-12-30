import sqlite3,os,pandas
from PIL import Image,ImageDraw,ImageFont

def BoF_init():
    conn = sqlite3.connect(f"data/INDEX/BoF.db")
    cur = conn.cursor()
    cur.execute("create table if not exists country(tag TEXT PRIMARY KEY,name TEXT,color TEXT,resourse TEXT,allyWith TEXT,warWith TEXT)")
    cur.execute("create table if not exists stars(id TEXT PRIMARY KEY,name TEXT,x TEXT,y TEXT,type TEXT,controller TEXT,owner TEXT,hyperlane TEXT,havePlanet TEXT)")
    stars = []
    ss = pandas.read_csv(os.path.dirname(__file__)+"/stars.csv",encoding="utf-8",header=0)
    for s in ss.values:
        stars.append(s.tolist())
    for s in stars:
        cur.execute(f"INSERT OR IGNORE INTO stars values('{s[0]}','{s[1]}','{s[2]}','{s[3]}','{s[4]}','{s[5]}','{s[6]}','{s[7]}','{s[9]}')")
        conn.commit()
    conn.commit()
    cur.close()
class Country:
    def __init__(self,tag,name,color,resourse:str,allyWith:str,warWith:str):
        self.tag,self.name,self.color=tag,name,color
        self.resourse = resourse.split(" ")
        self.allyWith = allyWith.split(" ")
        self.warWith = warWith.split(" ")
    def update(self):
        conn = sqlite3.connect(f"data/INDEX/BoF.db")
        cur = conn.cursor()
        cur.execute(f"update country set name='{self.name}',color='{self.color}',resourse='{' '.join(self.resourse)}',allyWith='{' '.join(self.allyWith)}',warWith='{' '.join(self.warWith)}' where tag='{self.tag}';")
        conn.commit()
        conn.close()
    @staticmethod
    def search_by_tag(tag):
        conn = sqlite3.connect(f"data/INDEX/BoF.db")
        cur = conn.cursor()
        data = cur.execute(f"select * from country where tag='{tag}';").fetchone()
        conn.close()
        if not data:return Country('','','','','','')
        return Country(tag,data[1],data[2],data[3],data[4],data[5])
    @staticmethod
    def get_all_country():
        conn = sqlite3.connect(f"data/INDEX/BoF.db")
        cur = conn.cursor()
        data = cur.execute(f"select tag from country;").fetchall()
        conn.close
        c = []
        for d in data:
            c.append(Country.search_by_tag(d[0]))
        return c
    @staticmethod
    def new_country(tag):
        conn = sqlite3.connect(f"data/INDEX/BoF.db")
        cur = conn.cursor()
        cur.execute(f"INSERT OR IGNORE INTO country values('{tag}','','','','','')")
        conn.commit()
        conn.close()
class Star:
    def __init__(self,id,name,x,y,type,owner,controller,hyperlane:str,havePlanet) -> None:
        self.id,self.name,self.x,self.y,self.type=id,name,float(x),float(y),type
        self.owner,self.controller=owner,controller
        self.hyperlane = hyperlane.split(" ")
        self.havePlanet = False if havePlanet==0 else True
    def update(self):
        conn = sqlite3.connect(f"data/INDEX/BoF.db")
        cur = conn.cursor()
        cur.execute(f"update stars set name='{self.name}',type='{self.type}',owner='{self.owner}',controller='{self.controller}',hyperlane='{' '.join(self.hyperlane)}',havePlanet='{1 if self.havePlanet else 0}' where id='{self.id}';")
        conn.commit()
        conn.close()
    def change_owner(self,newOwner):
        self.owner='newOwner';self.update()

    @staticmethod
    def search_by_id(id):
        conn = sqlite3.connect(f"data/INDEX/BoF.db")
        cur = conn.cursor()
        data = cur.execute(f"select * from stars where id='{id}';").fetchone()
        conn.close()
        if not data:return Star(0,'',0,0,'','','','','')
        return Star(id,data[1],data[2],data[3],data[4],data[5],data[6],data[7],data[8])
    @staticmethod
    def get_all_stars():
        conn = sqlite3.connect(f"data/INDEX/BoF.db")
        cur = conn.cursor()
        data = cur.execute(f"select id from stars;").fetchall()
        conn.close
        s = []
        for d in data:
            s.append(Star.search_by_id(d[0]))
        return s
    @staticmethod
    def draw_map():
        from .mapGene import generate_map
        stars:list[Star] = Star.get_all_stars()
        img = generate_map(stars)
        img.save('data/BoFMap.png')
