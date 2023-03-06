#跌深反彈，10個天期突破10日均線
import yfinance as yf
from concurrent.futures import ThreadPoolExecutor
import csv
import time


def ema(list_close,ema_num,stock_name,up_down_rate,volume):   #1參數:收盤列表,2參數:設定均線數值,3參數:股票代碼,4參數:漲跌幅,5參數:成交量

    global stock_data
    count = 0   
    
    ma10 = round(sum(list_close[-(ema_num+1):-1])/ema_num,2)
    if list_close[-2] >= ma10:
        
        for i in range(0,10): #★★10 設定天期=10天，測試有無站上10日均線，10天以前不能站上ma10
            ma10 = round(sum(list_close[-(ema_num+1)-i-1:-1-i-1])/ema_num,2)
            #ma2 = round(sum(list_close[-(ema_num+1)-i-1:-1-i-1])/ema_num,2) #往後移一個

            if list_close[-3-i] < ma10 :
                #print(stock_name,'站上20日均線')
                count+=1
            else:
                break #如果沒有直接跳出                

        if count == 10 and volume >= 1000: #★★當日站上10日均線，前面連續10次未站上ma10輸出資料
            #成交量>1000
            #output.append([stock_name[0],stock_name[1],stock_name[2],up_down_rate,volume])
            output[stock_name[0]]=[stock_name[0],stock_name[1],stock_name[2],up_down_rate,volume]
            # ↑存到字典-new★
            stock_data += stock_name[0] + ','#★增加代碼列表     

#抓取資料儲存在output        
def search_data(open_filename):
    output.clear()
    stock_data = '' #清除字串
    with open(open_filename,'r') as f:   #★媽媽電腦:多加解碼encoding='UTF-8'，不然會報錯cp950
        rows = list(csv.reader(f))

    with ThreadPoolExecutor(max_workers=200) as executor: #★增加多線程數量
        executor.map(main,rows)
    return output,stock_data[:-1]

def main(codes):
    global output
    
    
    #stock_name = input('請輸入要搜尋的股票代碼:')
    try:
        stock_no = yf.Ticker(codes[0]+'.TW')
        stock_close = stock_no.history(period='20d')['Close']
        
        #stock = yf.download(stock_name,start='2022-10-20',end='2022-11-08',interval='60m')['Close']
        #end->當天不會被列入
        if stock_close.size == 0:
            stock_no = yf.Ticker(codes[0]+'.TWO')
            stock_close = stock_no.history(period='20d')['Close']


    except IndexError:
        print(stock_no,'有問題')


    volume = stock_no.history(period='1d')['Volume'][-1]//1000   #成交量
    volume_5day = sum(stock_no.history(period='6d')['Volume'][:5])//1000//5 #★增加_當天前5日平均交易量
    close_price = stock_no.history(period='2d')['Close'] #2天收盤價
    up_down_rate = str(round(((close_price[-1]-close_price[-2])/close_price[-2])*100,2)) + '%'
    #↑漲跌幅
    
    #####
    close_data = []
    for i in stock_close:
        close_data.append(round(i,2))  #把收盤價儲存到列表
    #print(close) #測試收盤輸出列表
    close_data.append(999999) #添加最後一個數字，才不會有誤

    ema(close_data,10,codes,up_down_rate,volume) #加入漲跌幅、成交量


output = {}
stock_data = '' #★代碼列表













    
