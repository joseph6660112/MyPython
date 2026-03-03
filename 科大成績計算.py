Mc=12
Mn=12
Me=8
Mm=11
max_=15
def c ():
    try:
        s=[Mc,Me,Mm,Mn]
        name=['國文','英文','數學','自然']
        tt=0
        ttw=0
        for i in range(4):
            w=float(input(f'請輸入{name[i]}的權重'))
            tt+=w*s[i]
            ttw+=w*max_
        print(f'你的成績是{round((tt/ttw)*100,2)}')
    except:
        print('輸入數字')
while True:
    c()
    again=input('enter下一間,q離開')
    if again.lower()=='q':
        break