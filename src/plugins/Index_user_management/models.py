import os,sqlite3

class Group:
    gid = -1
    def __init__(self,gid) -> None:
        self.gid = gid
        if not os.path.exists('data/INDEX'):
            os.makedirs('data/INDEX')
        conn = sqlite3.connect(f"data/INDEX/{self.gid}.db")
        cur = conn.cursor()
        cur.execute("create table if not exists user(uid TEXT PRIMARY KEY,qid TEXT,nickname TEXT,money REAL)")
        conn.commit()
        cur.close()

    def new_user(self,qid,nickname):
        if self.findUser(qid):
            return False
        conn = sqlite3.connect(f"data/INDEX/{self.gid}.db")
        cur = conn.cursor()
        data = cur.execute(f"select * from user;").fetchall()
        id = 1
        for item in data:
            if id<=int(item[0]):
                id = int(item[0])+1
        cur.execute(
            f"insert into user(uid,qid,nickname,money) values({id},'{qid}','{nickname}',{10});"
            )
        conn.commit()
        cur.close()

    def find_user(self,qid):
        conn = sqlite3.connect(f"data/INDEX/{self.gid}.db")
        cur = conn.cursor()
        data = cur.execute(f"select * from user where qid='{qid}';").fetchall()
        conn.close()
        if len(data)==0:
            return False
        else:
            u = User(self)
            u.uid = data[0][0]
            u.nickname = data[0][2]
            u.money = data[0][3]
            return u

class User:
    uid = -1
    nickname = ''
    money = -1
    def __init__(self,group:Group) -> None:
        self.group = group

    def rename(self,new_name):
        self.nickname = new_name
        conn = sqlite3.connect(f"data/INDEX/{self.group.gid}.db")
        cur = conn.cursor()
        cur.execute(f"UPDATE user SET nickname='{new_name}' where uid='{self.uid}';")
        conn.commit()
        conn.close()

    def add_money(self,money):
        self.money += money
        print(self.money)
        conn = sqlite3.connect(f"data/INDEX/{self.group.gid}.db")
        cur = conn.cursor()
        cur.execute(f"UPDATE user SET money={self.money} where uid='{self.uid}';")
        conn.commit()
        conn.close()
