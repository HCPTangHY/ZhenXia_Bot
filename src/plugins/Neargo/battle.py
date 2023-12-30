from .models import *

import random

class Battle():
    def __init__(self,attacker:ncUser,defender:ncUser):
        self.attacker = attacker
        self.defender = defender
        self.damagePool = {"attacker":[],"defender":[]}
        self.report = []
    def battle_active(self):
        return self.attacker.HP>0 and self.defender.HP>0
    def defend_escape(self):
        return self.defender.HP<30 and self.defender.HP>0
    def attack_win(self):
        if self.defend_escape() and self.attacker.HP>0: return True
        if self.defender.HP<=0 and self.attacker.HP>0: return True
        if self.attacker.HP<=0:return False
    def make_damage(self,camp,damage):
        self.damagePool[camp].append(damage)
    def throw_damage(self,camp,damage):
        self.damagePool[camp].append(damage)
    def fight_damage(self,camp,hand):
        campUser:ncUser = getattr(self,camp)
        handWeapon = getattr(campUser,hand)
        item = Item.search_by_id(handWeapon.split("|")[-1].split(":")[-1])
        skillName = item.battleSkill.split("|")[0]
        if skillName=='':skillName='拳击'
        skill = item.battleSkill.split("|")[-1].split(":")
        if len(skill)==1:skill=['make_damage',1]
        damageModi = 1
        damageModiText = ''
        damageDice = random.random()
        if damageDice<0.1:damageModi=2;damageModiText='暴击！'
        if damageDice>0.8:damageModi=0;damageModiText='Miss!'
        getattr(self,skill[0])(str(camp),float(skill[1])*damageModi)
        if 'throw' in item.battleSkill.split("|")[-1].split(":")[0]:
            if camp=='attacker' and hand=='leftHand':self.attacker.leftHand=''
            if camp=='attacker' and hand=='rightHand':self.defender.rightHand=''
            if camp=='defender' and hand=='leftHand':self.attacker.leftHand=''
            if camp=='defender' and hand=='rightHand':self.defender.rightHand=''
        self.report.append(f"{User.find_user_by_uid(campUser.uid).nickname} 用 {item.name}{skillName}，造成{float(skill[1])*damageModi}点伤害！{damageModiText}")
    def fight(self):
        while self.battle_active():
            if self.defend_escape():break
            self.damagePool["attacker"].clear()
            self.damagePool["defender"].clear()
            self.fight_damage('attacker','leftHand')
            self.fight_damage('attacker','rightHand')
            self.fight_damage('defender','leftHand')
            self.fight_damage('defender','rightHand')

            for d in self.damagePool['attacker']:
                self.defender.HP-=d
            for d in self.damagePool['defender']:
                self.attacker.HP-=d

            self.report.append(f"{User.find_user_by_uid(self.attacker.uid).nickname}剩余{self.attacker.HP}/100")
            self.report.append(f"{User.find_user_by_uid(self.defender.uid).nickname}剩余{self.defender.HP}/100")
        if self.defend_escape() and self.attacker.HP>0:
            self.report.append(f"{User.find_user_by_uid(self.defender.uid).nickname}逃走了！")
        if self.attack_win():self.report.append(f"战斗结束{User.find_user_by_uid(self.attacker.uid).nickname}胜利！")
        else:self.report.append(f"战斗结束{User.find_user_by_uid(self.defender.uid).nickname}胜利！")
        if self.attack_win():
            money = random.randrange(int(self.defender.money/4),int(self.defender.money/2))
            self.defender.add_money(-money)
            self.attacker.add_money(money)
            self.report.append(f"{User.find_user_by_uid(self.attacker.uid).nickname}抢走了{money}火币")
            for i in self.defender.inventory:
                if random.random()<0.5:
                    self.report.append(f"{User.find_user_by_uid(self.attacker.uid).nickname}抢走了{i.split(':')[0]}")
                    self.defender.delete_item(i.split(':')[1])
                    self.attacker.add_item(i.split(':')[1])
        else:
            money = random.randrange(int(self.attacker.money/4),int(self.attacker.money/2))
            self.attacker.add_money(-money)
            self.defender.add_money(money)
            self.report.append(f"{User.find_user_by_uid(self.defender.uid).nickname}抢走了{money}火币")
            for i in self.attacker.inventory:
                if random.random()<0.5:
                    self.report.append(f"{User.find_user_by_uid(self.attacker.uid).nickname}抢走了{i}")
                    self.attacker.delete_item(i.split(':')[1])
                    self.defender.add_item(i.split(':')[1])
        self.attacker.update()
        self.defender.update()

# u1 = ncUser.find_user(1847680031)
# u2 = ncUser.find_user(878735639)
# b = Battle(u1,u2)
# b.fight()
# print("\n".join(b.report))
