player_1=input('input player 1 name:')
player_2=input('input player 2 name:')
goods_price=int(input('input goods price:'))
chance=0
while True:
    chance+=1
    _1_goods_price=int(input('input 1_goods price:'))
    _2_goods_price=int(input('input 2_goods price:'))
    if goods_price==_1_goods_price or goods_price==_2_goods_price or chance==3:
        break
    elif abs(goods_price-_1_goods_price)>abs(goods_price-_2_goods_price):
        print(f'{player_2} nearly goods price')
    else:
        print(f'{player_1} nearly goods price')
if goods_price==_1_goods_price:
    print(f'congratulation {player_1} win,price is {goods_price}')
elif goods_price==_2_goods_price:
    print(f'congratulation {player_2} win,price is {goods_price}')
elif chance==3:
    print(f'you lose and true answer is {goods_price}')