from flask import Flask,request,abort
from linebot import LineBotApi,WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent,TextMessage,TextSendMessage
import tower_line
import requests,os,datetime

#Line_notify模塊
def line_notify(msg):
    url = 'https://notify-api.line.me/api/notify'
    token = 'PvksZbQ3ERy9Hw12kvMjXEjJ1qgvMQBJmOLVZUmsZkJ'
    headers = {'Authorization':'Bearer '+token} #★Bearer 要加入空格後面在加權證，沒加空格會報錯

    data = {'message':msg}

    r = requests.post(url,headers=headers,data=data)

    print('發送完成')

#列印出資料
def print_data(filename):
            output = tower_line.search_data(filename)
            count = 0
            data = ''

            
            for i in output:
                if len(i) == 1:
                    data += i[0]+'\n'
                else:
                    data += f"★{i[0]} {i[1]}-{i[2]}\n漲幅:{i[3]} 成交量:{i[4]}\n\n"
                    count+=1

                if count == 20:
                    print(data)
                    line_notify(data)
                    data=''
                    count=0
                    
            if len(data):
                line_notify(data)

#比較資料

                

#監控時間
def view_time():
    now = datetime.datetime.now() + datetime.timedelta(hours=8) #歐洲時間+8=台灣時間
    print(now)
    year = int(now.strftime('%Y'))
    month = int(now.strftime('%m'))
    day = int(now.strftime('%d'))
    stock_start = datetime.datetime(year,month,day,9,00)
    stock_end = datetime.datetime(year,month,day,13,30)
    
    after_now = now + datetime.timedelta(minutes=6) #增加啟動時間6分鐘後結束
    after_now = after_now.strftime('%H:%M')
    print(after_now)
    
    hour = int(now.strftime('%H')) 
    minute = int(now.strftime('%M'))+3 #時間變數
    if minute in [1,2,3,4,5,6,7,8,9,0]:
        minute = f'0{minute}'
    if hour in [1,2,3,4,5,6,7,8,9,0]:
        hour = f'0{hour}'
    if hour == 24:
        hour = '00'
    print(f'{hour}:{minute}')
    while 1:
        now = datetime.datetime.now() + datetime.timedelta(hours=8)
        set_time = now.strftime('%H:%M')
        
        if f'{hour}:{minute}' == set_time:
            print('時間到了，',set_time)
            line_notify(f'時間到了，{set_time}')
            minute = int(minute) + 1
            if minute >= 60:
                hour = int(hour) + 1
                minute = minute - 60
            if minute in [1,2,3,4,5,6,7,8,9,0]:
                minute = f'0{minute}'
            if hour in [1,2,3,4,5,6,7,8,9,0]:
                minute = f'0{minute}'
        if not (stock_start <= now <= stock_end):        
            if after_now == set_time: #增加條件
                print('監控結束')
                output = []
                break
        if '13:30' == set_time:
            print('13:30 股市結束')
            line_notify('13:30 股市結束')
            break
            

#Flask_server
app = Flask(__name__)

line_bot_api = LineBotApi(os.environ.get("CHANNEL_ACCESS_TOKEN"))
handler = WebhookHandler(os.environ.get("CHANNEL_SECRET"))
output = []
stock_data = []

@app.route('/',methods=['POST'])
def callback():
    body = request.get_data(as_text=True)
    signature = request.headers['X-Line-Signature']
    try:
        handler.handle(body,signature)
        
    except InvalidSignatureError:
        abort(400)
    return 'ok' #最重要的回傳...都會忘記= ="

@handler.add(MessageEvent,message=TextMessage)
def handler_message(event):
    print(event)
    re_token = event.reply_token
    mtext = event.message.text
    global flag
    
    if '寶塔線' in mtext:
        if '上市' in mtext:
            print_data('上市公司代碼.csv') 
        elif '上櫃' in mtext:
            print_data('上櫃公司代碼.csv') 
        else:
            msg = TextSendMessage(text='請重新輸入正確格式搜尋【寶塔線+上市or寶塔線+上櫃】')
            line_bot_api.reply_message(re_token,msg)

    if '啟動' in mtext:
        msg = TextSendMessage(text='監控系統已啟動')
        line_bot_api.reply_message(re_token,msg)
        view_time()
        

        
   

