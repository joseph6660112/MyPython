大學面試時間={
    '中央機械與能源':'115.5.15',
    '台師學習科學':'115.5.16',
    '高師物理':'115.5.18',
    '彰師機電':'115.5.21',
    '彰師物理':'115.5.23',
    '高大工商管理':'115.5.15-16',
}
查=input('Please enter the school you wish to search for:')
#下面這行先把keys印出來
計=0
for school in 大學面試時間.keys():
    #若用==則需要輸入完整的keys
    if 查 in school:
    #這邊要在校名裡面的才會跑到這裡
        計+=1
        時間=大學面試時間[school]
        print(f'{school}的面試時間是{時間}')
if 計==0:
    print("沒有這間學校")