true='1234'
for 次數 in range(5):
    密碼=input('請輸入密碼')
    if 密碼 == true:
      print('輸入正確')
      break
    elif 密碼!=true and 次數<4:
      print(f'輸入錯誤,剩餘次數{4-次數}')
    elif 密碼!=true and 次數==4:
      print('密碼錯誤,帳號被鎖定')
