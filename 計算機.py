def 加 (x,y):
    return x+y
def 減 (x,y):
    return x-y
def 乘 (x,y):
    return x*y
def 除 (x,y):
    商=int(x//y)
    餘=int(x%y)
    if 餘==0:
        return [商]
    else:
        return [商,餘]
while True:
    i=input('(1)加(2)減(3)乘(4)除,或任意鍵離開')
    if i=='1':
        o=int(input('please input frist number'))
        t=int(input('please input second number'))
        print(f'{加(o,t )}')
    elif i=='2':
        o=int(input('please input frist number'))
        t=int(input('please input second number'))
        print(f'{減(o,t )}')
    elif i=='3':
        o=int(input('please input frist number'))
        t=int(input('please input second number'))
        print(f'{乘(o,t )}')
    elif i=='4':
        o=int(input('please input frist number'))
        t=int(input('please input second number'))
        res=除(o,t )
        if len(res)==1:
            print(f'{res[0]}')
        else:
            print(f'{res[0]}...{res[1]}')
    else :
        break