import yfinance as yf
from concurrent.futures import ThreadPoolExecutor
import csv,time

def main(codes):
    time.sleep(0.5)
    global output
    
    try:
        stock = yf.Ticker(codes[0]+'.TW')
        close = stock.history(period='30d')['Close']
        if close.size == 0:
            stock = yf.Ticker(codes[0]+'.TWO')
            close = stock.history(period='30d')['Close']
    except IndexError:
        print(stock,'有問題')
 
    data=[]
    for i in close:
        data.append(round(i,2))

    #寶塔線
    num = 1
    base = 3

    def check_green(data,base,num):
        while 1:
            close = data[-num]
            tmp=data[-num-base-1:-num]  #多加-1，多比較前一天收盤，這樣可以比較最高最低點較準確
            tmp.sort()
            Max,Min=tmp[-1],tmp[0]
            if close > Max:
                return True
            elif close < Min:
                return False
            else:
                num +=1
                


    close = data[-num]
    tmp=data[-num-base-1:-num]      #多加-1
    tmp.sort()
    Max,Min=tmp[-1],tmp[0]
    if close > Max:
        falg = 1
        num += 1
        
        if not check_green(data,base,num):
            up_down = round((data[-1]-data[-2])/data[-2]*100,2) #加入漲跌幅
            volume = stock.history(period='1d')['Volume'][-1]//1000   #成交量
            output[codes[0]]=[codes[0],codes[1],codes[2],str(up_down)+'%',volume] #增加字典key,value
            #stock_data.append([codes[0],codes[1],codes[2]])
            
            
#抓取資料儲存在output        
def search_data(open_filename):
    output.clear()
    with open(open_filename,'r') as f:
        rows = list(csv.reader(f))[1:]

    with ThreadPoolExecutor(max_workers=200) as executor:
        executor.map(main,rows)
    return output
    
output = {}
#search_data(output,'上市公司代碼.csv')
#search_data(output,'上櫃公司代碼.csv')

#print(output)

'''
#儲存CSV檔
with open('寶塔線翻紅.csv','w',newline='') as f:
    writer = csv.writer(f)
    #writer.writerow([open_filename.split('.')[0]])
    writer.writerows(output)
    print('儲存完成!!!')
'''

