from flask import Flask,request,abort
from linebot import LineBotApi,WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent,TextMessage,TextSendMessage
import tower_line
import requests,os,datetime
from concurrent.futures import ThreadPoolExecutor
import strong_stock_20ma

#Line_notify模塊
def line_notify(msg):
    url = 'https://notify-api.line.me/api/notify'
    token = 'PvksZbQ3ERy9Hw12kvMjXEjJ1qgvMQBJmOLVZUmsZkJ'
    headers = {'Authorization':'Bearer '+token} #★Bearer 要加入空格後面在加權證，沒加空格會報錯

    data = {'message':msg}

    r = requests.post(url,headers=headers,data=data)

    print('發送完成')

#發送訊息-模塊
def send_message(filename,output):               
    new_filename = filename.split('.')[0] 
    count = 0
    data = ''
    data += new_filename+'\n'  #標題

    
    for i in output:
        data += f"★{output[i][0]} {output[i][1]}-{output[i][2]}\n漲幅:{output[i][3]} 成交量:{output[i][4]}\n\n"
        count+=1

        if count == 20:
            print(data)
            line_notify(data)
            data=''
            count=0
            
    if len(data):
        line_notify(data)

#關鍵字單次發送股票資訊
def send_one_stock_message(filename):
    output = tower_line.search_data(filename)
    send_message('寶塔線+'+filename,output)

#關鍵字單次發送股票資訊---★NEW 飆股
def send_one_stock_message2(filename):
    output = strong_stock_20ma.search_data(filename)
    send_message('飆股+'+filename,output)


#列印出資料(改成字典格式讀取)
def print_data(filename):
    add_data = {}
    del_data = {}
    output = tower_line.search_data(filename)
    if '上市' in filename:
        if not len(stock_data1): #初始化，第一次空dict全部儲存
            stock_data1.update(output) #更新儲存資料
            send_message(filename,output) #發送初次訊息
        else:
            output_set = set(output)
            stock_data1_set = set(stock_data1)
            add_diff = output_set-stock_data1_set #搜尋出來資料-資料庫原有資料=新的資料
            del_diff = stock_data1_set-output_set #原始資料庫-新搜尋的資料=剩下就是又變成未符合項目
            for i in add_diff:
                stock_data1[i] = output[i] #資料庫沒有，新增一筆
                add_data[i]=output[i] #新建字典新增一筆，等等傳送訊息
            for j in del_diff:
                del_data[j] = stock_data1[j] #新增剔除的名單，等等傳送訊息
                stock_data1.pop(j) #資料庫移除

            if len(add_diff):
                send_message('上市公司寶塔線翻紅-即時訊息(新增).app',add_data)
            if len(del_diff):
                send_message('上市公司寶塔線翻黑-即時訊息(移除).app',del_data)

    elif '上櫃' in filename:
        if not len(stock_data2): #初始化，第一次空dict全部儲存
            stock_data2.update(output) #更新儲存資料
            send_message(filename,output) #發送初次訊息
        else:
            output_set = set(output)
            stock_data2_set = set(stock_data2)
            add_diff = output_set-stock_data2_set #搜尋出來資料-資料庫原有資料=新的資料
            del_diff = stock_data2_set-output_set #原始資料庫-新搜尋的資料=剩下就是又變成未符合項目
            for i in add_diff:
                stock_data2[i] = output[i] #資料庫沒有，新增一筆
                add_data[i]=output[i] #新建字典新增一筆，等等傳送訊息
            for j in del_diff:
                del_data[j] = stock_data2[j] #新增剔除的名單，等等傳送訊息
                stock_data2.pop(j) #資料庫移除

            if len(add_diff):
                send_message('上櫃公司寶塔線翻紅-即時訊息(新增).app',add_data)
            if len(del_diff):
                send_message('上櫃公司寶塔線翻黑-即時訊息(移除).app',del_data)
            


                

#監控時間
def view_time():
    now = datetime.datetime.now() + datetime.timedelta(hours=8) #歐洲時間+8=台灣時間
    print(now)
    #年月日參數
    year,month,day = int(now.strftime('%Y')),int(now.strftime('%m')),int(now.strftime('%d'))
    stock_start = datetime.datetime(year,month,day,9,00)
    stock_end = datetime.datetime(year,month,day,13,30)
    
    after_now = now + datetime.timedelta(minutes=6) #增加設定時間6分鐘後結束
    after_now = after_now.strftime('%H:%M')
    print('結束時間:',after_now)

    #小時分鐘參數    
    hour = int(now.strftime('%H')) 
    minute = int(now.strftime('%M')) #啟動開始計數時間變數
    #顯示時間設定
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

        #非股市時間9:00~13:30，設定6分鐘到直接結束
        if not (stock_start <= now <= stock_end):
            if f'{hour}:{minute}' == set_time: 
                print('時間到了，',set_time)
                line_notify(f'時間到了，{set_time}')
            if after_now == set_time: #增加條件
                line_notify('6分鐘，監控結束')
                print('監控結束')
                break
        elif f'{hour}:{minute}' == set_time:
            #偵測股票
            #with ThreadPoolExecutor() as executor:
            #    executor.map(print_data,['上市公司代碼.csv','上櫃公司代碼.csv'])
            print_data('上市公司代碼.csv')
            print_data('上櫃公司代碼.csv')

        #時間計數器
        if f'{hour}:{minute}' == set_time: 
            minute = int(minute) + 3 #間格時間變數-每3分鐘偵測一次      
            
            #時間設定
            if minute >= 60:
                hour = int(hour) + 1
                minute = minute - 60
            if minute in [1,2,3,4,5,6,7,8,9,0]:
                minute = f'0{minute}'
            if hour in [1,2,3,4,5,6,7,8,9,0]:
                minute = f'0{minute}'

            
        #股市結束時間    
        if '13:30' == set_time:
            print('13:30 股市結束')
            line_notify('13:30 股市結束')
            stock_data1 = {}  #清除
            stock_data2 = {}  #清除
            break
            

#Flask_server
app = Flask(__name__)

line_bot_api = LineBotApi(os.environ.get("CHANNEL_ACCESS_TOKEN"))
handler = WebhookHandler(os.environ.get("CHANNEL_SECRET"))


stock_data1 = {} #上市
stock_data2 = {} #上櫃

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
    
    if '寶塔線' in mtext:
        if '上市' in mtext:
            send_one_stock_message('上市公司代碼.csv') 
        elif '上櫃' in mtext:
            send_one_stock_message('上櫃公司代碼.csv') 
        else:
            msg = TextSendMessage(text='請重新輸入正確格式搜尋【寶塔線+上市or寶塔線+上櫃】')
            line_bot_api.reply_message(re_token,msg)

    if '啟動' in mtext:
        msg = TextSendMessage(text='監控系統已啟動')
        line_bot_api.reply_message(re_token,msg)
        view_time()

#----★NEW
    if '飆股' in mtext:
        if '上市' in mtext:
            send_one_stock_message2('上市公司代碼.csv') 
        elif '上櫃' in mtext:
            send_one_stock_message2('上櫃公司代碼.csv') 
        else:
            msg = TextSendMessage(text='請重新輸入正確格式搜尋【飆股+上市or飆股+上櫃】')
            line_bot_api.reply_message(re_token,msg)
        
