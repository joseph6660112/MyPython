import random
class Character:
    def __init__(self,name,hp,atk):
        self.name=name
        self.hp=hp
        self.atk=atk
    def alive(self):
        return self.hp>0
    def dead(self):
        return self.hp<=0
    def 攻(self):
        ch=input('(1)普攻(2)特殊攻擊')
        if ch=='1':
            damage=self.atk
        else:
            倍率=random.choice([0.8,1.2])
            damage = (self.atk)*倍率
        return damage
    def 守(self):
        cho = input('(1)抵擋(2)閃避')
        if cho == '1':
            減傷=0.5
        else:
            倍率 = random.choice([0, 1])
            減傷 = 倍率
        return 減傷
    def 電腦攻(self):
        動作 = random.choice(['1', '2'])
        if 動作 == '1': return self.atk
        return self.atk * random.choice([0.8, 1.2])
    def 電腦守(self):
        動作 = random.choice(['1', '2'])
        if 動作 == '1': return 0.5
        return random.choice([0, 1])
class 戰士(Character):
    def __init__(self, name):
        super().__init__(name,hp=500,atk=50)
class 法師(Character):
    def __init__(self, name):
        super().__init__(name,hp=300,atk=100)
class 坦克(Character):
    def __init__(self, name):
        super().__init__(name,hp=800,atk=30)
print("歡迎來到對戰遊戲！請選擇你的職業：")
player_name=input('please input your name')
while True:
    ch=input(f"你好{player_name},請選擇您的職業1.戰士 (血量中,傷害中)  2.法師 (高攻擊)  3.坦克 (高血量):")
    if ch=="1":
        player=戰士(player_name)
        break
    elif ch=="2":
        player=法師(player_name)
        break
    elif ch=="3":
        player=坦克(player_name)
        break
    else :
        print('叫你輸入123')
        continue
print(f'您的職業是{type(player).__name__}血量{player.hp}攻擊{player.atk}')
def 選擇對手():
    n=random.choice(['1','2','3'])
    if n=="1":
        對手=戰士("電腦戰士")
    elif n=="2":
        對手=法師("電腦法師")
    elif n=="3":
        對手=坦克("電腦坦克")
    print(f'對手的職業是{對手.name}血量{對手.hp}攻擊{對手.atk}')
    return 對手
enemy=選擇對手()
while True:
    #玩家回合
    扣血=player.攻()
    防禦=enemy.電腦守()
    print(f'您打出了{扣血}')
    if 防禦 == 0:
        print(f"{enemy.name}閃避成功")
    elif 防禦 == 0.5:
        print(f"{enemy.name}防禦成功")
    elif 防禦 == 1:
        print(f"{enemy.name}閃避失敗")
    print(f'{type(player).__name__}造成了{扣血*防禦}點傷害')
    enemy.hp-=(扣血*防禦)
    print(f'對手剩餘{enemy.hp}血')
    if enemy.dead():
        print(f'{player_name}win')
        break
    # 玩家回合
    扣血 = enemy.電腦攻()
    防禦 = player.守()
    print(f'對手打出了{扣血}')
    if 防禦 == 0:
        print(f"{player_name}閃避成功")
    elif 防禦 == 0.5:
        print(f"{player_name}防禦成功")
    elif 防禦 == 1:
        print(f"{player_name}閃避失敗")
    print(f'{enemy.name}造成了{扣血 * 防禦}點傷害')
    player.hp -= (扣血 * 防禦)
    print(f'{player_name}剩餘{player.hp}血')
    if player.dead():
        print(f'{enemy.name}win')
        break