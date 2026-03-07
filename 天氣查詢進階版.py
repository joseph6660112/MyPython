import requests
city=input('Please enter the city you wish to search for:')
API=input('enter your api key')
網址=f'https://api.openweathermap.org/data/2.5/weather?q={city}&appid={API}'
data=(requests.get(網址))
氣溫=int((data.json()['main']['temp'])-273.15)
狀況=str(data.json()['weather'][0]['description'])
國家=str(data.json()['sys']['country'])
print(f'{國家}的{city}現在的溫度是{氣溫}目前的天氣狀況是{狀況}')

