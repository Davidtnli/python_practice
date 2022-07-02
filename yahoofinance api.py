import requests
import time

url = "https://yfapi.net/v8/finance/spark"

querystring = {"symbols": "AAPL,TSLA",
              "interval": "1d",
              "range": "1mo"
              }

headers = {
   'x-api-key': "JH2qZNmlxu85M8Lsr8Vr774LY6pLusyu2jrP9mR0"
}

res = requests.request("GET", url, headers=headers, params=querystring).json()

if __name__ == '__main__':

   time_stamp_AAPL = res['AAPL']['timestamp']
   time_stamp_TSLA = res['TSLA']['timestamp']
   timeString_AAPL = []
   timeString_TSLA = []
   for i, j in zip(time_stamp_AAPL, time_stamp_TSLA):
       struct_time_AAPL = time.localtime(i)
       struct_time_TSLA = time.localtime(j)
       timeString_AAPL.append(time.strftime("%Y-%m-%d", struct_time_AAPL))
       timeString_TSLA.append(time.strftime("%Y-%m-%d", struct_time_TSLA))
   close_TSLA = res['TSLA']['close']
   close_AAPL = res['AAPL']['close']
   result_AAPL = {}
   result_TSLA = {}
   result = {}
   for i in range(len(timeString_AAPL)):
       result_AAPL[f'{timeString_AAPL[i]}'] = close_AAPL[i]
       result_TSLA[f'{timeString_TSLA[i]}'] = close_TSLA[i]

   result['AAPL'] = result_AAPL
   result['TSLA'] = result_TSLA
   print(result)


#比較api

url = "https://yfapi.net/v8/finance/chart/AAPL?"

querystring = {
              "interval": "1d",
              "range": "5d",
               "comparisons": "MSFT,TSLA"
              }

headers = {
   'x-api-key': "JH2qZNmlxu85M8Lsr8Vr774LY6pLusyu2jrP9mR0"
}

res = requests.request("GET", url, headers=headers, params=querystring).json()


if __name__ == '__main__':

   time_stamp = res['chart']['result'][0]['timestamp']
   timeString = []
   for i in time_stamp:
       struct_time = time.localtime(i)
       timeString.append(time.strftime("%Y-%m-%d", struct_time))
   MSFT = res['chart']['result'][0]['comparisons'][0]
   TSLA = res['chart']['result'][0]['comparisons'][1]
   AAPL = res['chart']['result'][0]['indicators']['quote'][0]
   result = {}

   for i in range(len(timeString)):
       AAPL_dic = {'open':round(AAPL['open'][i],0), 'close':round(AAPL['close'][i],0),'high':round(AAPL['high'][i],0),'low':round(AAPL['low'][i],0)}
       TSLA_dic = {'open':round(TSLA['open'][i],0), 'close':round(TSLA['close'][i],0),'high':round(TSLA['high'][i],0),'low':round(TSLA['low'][i],0)}
       MSFT_dic = {'open':round(MSFT['open'][i],0), 'close':round(MSFT['close'][i],0),'high':round(MSFT['high'][i],0),'low':round(MSFT['low'][i],0)}
       name = {'AAPL': AAPL_dic,'TSLA':TSLA_dic,'MSFT':MSFT_dic}
       result[f'{timeString[i]}'] = name

   print(result)