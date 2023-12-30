import os,sqlite3

class User:
    uid = qid = -1
    nickname = ''
    money = -1
    def __init__(self,uid,qid,groups:list,nickname,money) -> None:
        self.uid,self.qid,self.nickname,self.money = uid,qid,nickname,money
        self.groups = groups
    @staticmethod
    def new_user(qid,gid,nickname):
        if User.find_user_by_qid(qid)!="NoUser":
            return False
        conn = sqlite3.connect(f"data/INDEX/users.db")
        cur = conn.cursor()
        data = cur.execute(f"select * from user;").fetchall()
        id = 1
        for item in data:
            if id<=int(item[0]):
                id = int(item[0])+1
        cur.execute(
            f"INSERT OR IGNORE INTO user(uid,qid,groups,nickname,money) values({id},'{qid}','{gid}','{nickname}',{10});"
            )
        conn.commit()
        cur.close()

    @staticmethod
    def find_user_by_qid(qid):
        conn = sqlite3.connect(f"data/INDEX/users.db")
        cur = conn.cursor()
        data = cur.execute(f"select * from user where qid='{qid}';").fetchall()
        conn.close()
        if len(data)==0:
            return 'NoUser'
        else:
            return User(data[0][0],data[0][1],str(data[0][2]).split(","),data[0][3],data[0][4])
    @staticmethod
    def find_user_by_uid(uid):
        conn = sqlite3.connect(f"data/INDEX/users.db")
        cur = conn.cursor()
        data = cur.execute(f"select * from user where uid='{uid}';").fetchall()
        conn.close()
        if len(data)==0:
            return 'NoUser'
        else:
            return User(data[0][0],data[0][1],str(data[0][2]).split(","),data[0][3],data[0][4])
    @staticmethod
    def rich_rank(gid):
        conn = sqlite3.connect(f"data/INDEX/users.db")
        cur = conn.cursor()
        data = cur.execute(f"select uid,groups from user order by money DESC;").fetchall()
        conn.close()
        us:list[User] = []
        for d in data:
            if gid in str(d[1]):
                us.append(User.find_user_by_uid(d[0]))
        return us
    def add_group(self,gid):
        self.groups.append(gid)
        conn = sqlite3.connect(f"data/INDEX/users.db")
        cur = conn.cursor()
        cur.execute(f"UPDATE user SET groups='{','.join(self.groups)}' where uid='{self.uid}'")
        conn.commit()
    def rename(self,new_name):
        self.nickname = new_name
        conn = sqlite3.connect(f"data/INDEX/users.db")
        cur = conn.cursor()
        cur.execute(f"UPDATE user SET nickname='{new_name}' where uid='{self.uid}';")
        conn.commit()
        conn.close()

    def add_money(self,money):
        self.money += money
        conn = sqlite3.connect(f"data/INDEX/users.db")
        cur = conn.cursor()
        cur.execute(f"UPDATE user SET money={self.money} where uid='{self.uid}';")
        conn.commit()
        conn.close()
