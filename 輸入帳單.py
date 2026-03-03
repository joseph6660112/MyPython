def mylist(name,money):
    print(f'hi,{name}你的今日明細')
    for d in money:
        print(f'cost {d}')
    print(f'總共花了{sum(money)}')
y=input('pleas input your name')
l=[]
for q in [1,2,3]:
    i=int(input('請輸入你的第'+str(q)+'筆花費'))
    l.append(i)
mylist(y,l)
