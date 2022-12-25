#飆股(大於5日成交量)+20ma
import yfinance as yf
from concurrent.futures import ThreadPoolExecutor
import csv
import time


def ema(list_close,ema_num,stock_name,up_down_rate,volume):   #1參數:收盤列表,2參數:設定均線數值,3參數:股票代碼,4參數:漲跌幅,5參數:成交量
  
    sum_num = 0
    for i in range(0,5): #5->當日5跟K棒跟前一個K棒比較
        ma1 = round(sum(list_close[-(ema_num+1)-i:-1-i])/ema_num,2)
        ma2 = round(sum(list_close[-(ema_num+1)-i-1:-1-i-1])/ema_num,2) #往後移一個

        #print(ema_num,'日均線數值:',ma)

        #比較判斷有無站上均線
        #print(list_close[-2-i],'>=',ma1, 'AND',list_close[-3-i],'<=',ma2  )
        if list_close[-2-i] >= ma1 and list_close[-3-i] <= ma2:
            #print(stock_name,'站上20日均線')
            #output.append([stock_name[0],stock_name[1],stock_name[2],up_down_rate,volume])
            output[stock_name[0]]=[stock_name[0],stock_name[1],stock_name[2],up_down_rate,volume]
            # ↑存到字典-new★
            break #只要搜尋到一個就加入清單跳出

#抓取資料儲存在output        
def search_data(open_filename):
    output.clear()
    #output.append([open_filename.split('.')[0]])
    with open(open_filename,'r') as f:   #★媽媽電腦:多加解碼encoding='UTF-8'，不然會報錯cp950
        rows = list(csv.reader(f))[1:]

    with ThreadPoolExecutor(max_workers=200) as executor: #★增加多線程數量
        executor.map(main,rows)
    return output

def main(codes):
    global output
    
    
    #stock_name = input('請輸入要搜尋的股票代碼:')
    try:
        stock_no = yf.Ticker(codes[0]+'.TW')
        stock_close = stock_no.history(period='10d',interval='60m')['Close']
        
        #stock = yf.download(stock_name,start='2022-10-20',end='2022-11-08',interval='60m')['Close']
        #end->當天不會被列入
        if stock_close.size == 0:
            stock_no = yf.Ticker(codes[0]+'.TWO')
            stock_close = stock_no.history(period='10d',interval='60m')['Close']


    except IndexError:
        print(stock_no,'有問題')


    volume = stock_no.history(period='1d')['Volume'][-1]//1000   #成交量
    volume_5day = sum(stock_no.history(period='6d')['Volume'][:5])//1000//5 #★增加_當天前5日平均交易量
    
    
    if volume >= 1000 and volume >= volume_5day*2: #★測試當日有沒有比前5日爆2倍大量
        
        close_data = []
        for i in stock_close:
            close_data.append(round(i,2))  #把收盤價儲存到列表
        #print(close) #測試收盤輸出列表
        close_data.append(999999) #添加最後一個數字，才不會有誤


        close_price = stock_no.history(period='2d')['Close'] #2天收盤價
        up_down_rate = str(round(((close_price[-1]-close_price[-2])/close_price[-2])*100,2)) + '%'
        #↑漲跌幅
        ema(close_data,20,codes,up_down_rate,volume) #加入漲跌幅、成交量


output = {}














    
