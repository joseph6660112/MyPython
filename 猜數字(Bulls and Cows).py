import random
print('歡迎來到 猜數字遊戲 (Bulls and Cows)')
while True:
    action=input('(1)查詢遊戲規則(2)開始遊戲(3)結束')
    if action=='1':
        print('''
 A 代表：數字正確，且位置也正確。
 B 代表：數字正確，但位置不對。
 範例：答案是 "1234"，你猜 "1356","1" 是A,"3"是B，結果為"1A1B"''')
    elif action=='2':
        正確答案=[str(n) for n in random.sample(range(10),4)]
        次數 = 0
        while True:
            your_answer =list(input('請輸入四位數字'))
            if len(your_answer) != 4:
                print('請輸入"剛好四位"數字！')
                continue
            if your_answer==正確答案:
                print(f'恭喜回答正確！你總共猜了{次數+1}次。')
                break
            elif your_answer!=正確答案:
                次數+=1
                a=0
                b=0
                for anws in range(4):
                    if 正確答案[anws]==your_answer[anws]:
                        a+=1
                    elif your_answer[anws]in 正確答案:
                        b+=1
                print(f'可惜猜錯了,目前猜錯{次數}次,{a}A{b}B')
    elif action == '3':
        print('謝謝遊玩,下次見')
        break