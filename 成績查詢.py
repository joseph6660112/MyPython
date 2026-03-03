成績=['國','12','英','8','數','11','自','12']
操作=input('請輸入操作指令(A)查詢該科成績(B)修改(C)刪除(D)新增').upper()
if 操作 == 'A':
    查=input('查詢科目為:')
    print(f'該科分數為{成績[成績.index(查)+1]}')
elif 操作 =='B':
    目標=input('請輸入要修改的科目')
    正確=input('正確成績為')
    成績[成績.index(目標)+1]=正確
    print(f'您{成績[成績.index(目標)]}的分數為{成績[成績.index(目標)+1]}分')
elif 操作 =='C':
    re=input('請輸入要刪除的科目')
    位置=成績.index(re)
    成績.pop(位置)
    成績.pop(位置)
    print(成績)
elif 操作 =='D':
    mo=input('請輸入要新增的科目')
    mon=input('請輸入該科目成績')
    成績.extend([mo,mon])
    print(成績)