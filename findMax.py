import csv
import time
from datetime import timedelta, datetime
import sys
import numpy as np

from graph_drawing import *
import pandas as pd


class Trade:    
    
    high = ''
    def __init__(self):
        self.max_value = 0 
        self.min_value = 0
        self.prev_max = 0
        self.prev_min = 0
        self.changed = 0
        self.prev_value = 0
        self.current_value = 0
        self.delta = 0
        #Создано для хранения топовой свечи
        self.high_candle = Candle([0 for i in range(0, 7)])
        self.low_candle = Candle([0 for i in range(0, 7)])
        #Сохраняем свечу, которая вернула True
        self.second_high_candle = Candle([0 for i in range(0, 7)])
        self.target_candle = Candle([0 for i in range(0, 7)])


class Candle:
    result = False
    def __init__(self,data):
        self.date = str(data[0])
        self.time = str(data[1])
        self.open = data[2]
        self.high = data[3]
        self.low = data[4]
        self.close = data[5]
        self.vol = data[6]
        self.result = False

class Trader:
    def __init__(self):
        self.profit = 0

def from_file_to_candle(path):
    """Получаем из файла список объектов-свеч"""
    file_data = []
    result = []
    with open(path, "r") as file_obj:
        reader = csv.reader(file_obj)
        for row in reader:
            str_row = "".join(row)
            file_data.append(str_row.split(';'))
    for number in range(1, len(file_data)):
        candle = Candle(file_data[number])
        result.append(candle)
    return result

def split_for_days(candles_list):
    """Делим список свечей по дням"""    
    day_list = []
    res_list = []
    for candle in candles_list:
        if candle.time!='10:00':
            day_list.append(candle)
        else:
            day_list = []
            day_list.append(candle)
            res_list.append(day_list)
    return res_list

def is_waning(candle):
    """Проверяет, является ли свеча убывающей"""    
    if candle.open > candle.close: return True
    #Что делать, если они равны? Пока считаем, что False
    else: return False

def to_timestamp(candle_time):
    """Перевод времени в timestamp, чтобы сравнивать времена"""    
    d = datetime.strptime(candle_time, "%H:%M")
    ts = time.mktime(d.timetuple())
    return ts

def day_high(candle_list, candle_time):
    """Ищем максимум за день до какого-то времени"""    
    max_high = float(candle_list[0].high)
    for candle in candle_list:
        while to_timestamp(candle.time) < to_timestamp(candle_time):
            candle_high = float(candle.high)
            if  candle_high > max_high:
                max_high = candle_high
    return max_high


def second_max(candle_cur, trade, candle_list, minutes):
    """Поиск второго максимума в промежутке от предыдущей свечки до текущей"""
    from_index = candle_list.index(trade.high_candle)+1 #Первый максимум
    to_index = candle_list.index(candle_cur)
    #Ищем подмножество, в котором нужно искать максимум
    searched_list = candle_list[from_index: to_index + 1]  
    candle_count = minutes//5
    if len(searched_list)>candle_count:
        #Ищем самую высокую вершинку на отрезке
        max_candle = searched_list[0]
        for candle in searched_list:
            if float(candle.high)>float(max_candle.high):
                max_candle = candle
        return max_candle
    else: 
        return trade.second_high_candle
        


def current_amplitude(trade, candle, parametr):
    """Проверяем 'высоту' амплтуды""" 
    max_high = trade.max_value
    if max_high - float(candle.low) == parametr:
        return True
    else: return False

def check_new_trade_max(trade, candle):
    """Обновляет максимум дня, если высота свечи больше"""
    if float(trade.max_value) < float(candle.high):
        trade.max_value = float(candle.high)

def check_new_trade_low(trade, candle):
    """Обновляет минимум дня, если значение нижней границы свечи меньше"""
    if float(trade.low_candle.close) < float(candle.low):
        trade.low_candle = candle

def average_price(candle_list):
    """Средняя цена за день"""
    price = 0
    for candle in candle_list:
        price+=float(candle.close)
    return price/len(candle_list)

def max_and_low_of_day_distance(candle_day, percent):
    """Расстоние по цене между мин и макс дня"""
    max_day = candle_day[0].high
    min_day = candle_day[0].low
    for candle in candle_day:
        if float(candle.high) > float(max_day):
            max_day = float(candle.high)
        elif float(candle.low) < float(min_day):
            min_day = float(candle.low)
        
    distance = (float(max_day) - float(min_day))/ ((float(max_day)+float(min_day))/2)
    if distance >= percent:
        return True
    else:
        return False




def is_our_candle(candle, trade, candle_list):
    if trade.second_high_candle.low!= 0:
        if trade.second_high_candle in candle_list:
            from_index = candle_list.index(trade.second_high_candle) #Первый максимум
            to_index = candle_list.index(candle)
            #Ищем подмножество, в котором нужно искать максимум
            if to_index - from_index<2:
                return True
            else:
                return False
        else:
            return False
    else:
        return False

def caluclate_stop(trade):
    first_max = float(trade.high_candle.high)
    second_max = float(trade.second_high_candle.high)
    stop = max(first_max, second_max) + 3
    return stop

def calculate_take(trade, candle_day):
    """Расстоние по цене между мин и макс дня"""
    max_day = 0
    min_day = trade.target_candle.low
    candle1 = None
    for candle in candle_day:
        if to_timestamp(candle.time)<to_timestamp(trade.target_candle.time):
            if float(candle.high) > float(max_day):
                max_day = float(candle.high)
                candle1 = candle
            elif float(candle.low) < float(min_day):
                min_day = float(candle.low)
        
    distance = (float(max_day) - float(min_day))
    
    take = float(trade.target_candle.close) - distance*0.4  #100 #(float(caluclate_stop(trade)) - float(trade.target_candle.close))*2.5
    return take



def strategy(trade, candle, candle_day):

    # trade = Trade()
    signal = False
    trade.high_candle = candle_day[0]
    check_new_trade_low(trade, candle)
    #Проверяем критерии
    if is_waning(candle):
        #Считаем всякие параметры
        p0 = float(candle.open) >= float(trade.min_value)
        # p1 = price_distance_between_peaks(candle, trade) <= 0.01
        p2 = is_our_candle(candle, trade, candle_day)
        # p2 = float(candle.close) >= float(trade.low_candle.low)
        # p3 = current_amplitude(trade, candle, 300)

        second_max_candle = second_max(candle, trade, candle_day, 60)

        if abs(float(second_max_candle.high) - float(trade.high_candle.high)) <=3:
            trade.second_high_candle = second_max_candle
        
        if p0 and p2:
            trade.target_candle = second_max_candle
            signal = True
            new_candle_day = candle_day[candle_day.index(candle):]
            strategy(trade, candle, new_candle_day)
    else:
        if float(trade.second_high_candle.high) >= float(trade.high_candle.high): 
            trade.high_candle = trade.second_high_candle #Обновляем максимум за день
            
    return signal

def main(path):
    """Обход данных""" 
    result = False
    candles_list = from_file_to_candle(path)
    candles_days = split_for_days(candles_list)
    profit = []
    traiangels_to_draw = []
    for i in range(len(candles_days)):
        k = 0
        trade = Trade()
        candle_day = candles_days[i] # i-ый день
        trade.high_candle = candle_day[0]  # берем за максимум
        p0 = max_and_low_of_day_distance(candle_day, 0.01)
        data = data_to_draw(candles_days[i])
        dataframe = pd.DataFrame(data)
        if i > 0:
            prev_data = data_to_draw(candles_days[i-1])
            prev_dataframe = pd.DataFrame(prev_data)
        else:
            prev_dataframe = pd.DataFrame({'A' : []})
            

        if p0:
            for candle in candle_day:
                # result = strategy(trade, candle, candle_day)
                i = 0
                while k < len(candle_day):
                    # print('теперь мы тут')
                    result = strategy(trade, candle_day[k], candle_day[i:])
                    if result:
                        take = calculate_take(trade, candle_day[k:])
                        stop = caluclate_stop(trade) 
                        
                        while i < len(candle_day[k:]):     
                            print(trade)
                            # traiangels_to_draw(take)                           
                            if float(candle_day[k].high) >= stop:
                                draw_buy(dataframe, trade, candle_day[k], stop, prev_dataframe)
                                profit.append(float(candle_day[k].open) - float(stop))
                                trade.high_candle = candle_day[i+1]
                                trade.second_high_candle = candle_day[i+1]
                                break
                            elif float(candle_day[k].low) <= take:
                                draw_buy(dataframe, trade, candle_day[k], take)
                                profit.append(float(candle_day[k].open) - float(take))
                                break
                            elif k == len(candle_day) - 1:
                                draw_buy(dataframe, trade, candle_day[k], float(candle_day[-1].close))
                                break
                            i += 1
                    k += 1
                break
    to_func = accumulative(profit)
    draw_result(to_func)
    return result

def time_distance_between_tops(first_top:Candle, second_top:Candle):
    """Расстояние по времени междудвумя вершинками

    Arguments:
        first_top {Candle} -- Первая вершина
        second_top {Candle} -- Вторая вершина
    """    

    first_top_time = first_top.time.split(':')
    second_top_time = second_top.time.split(':')

    time_distance = timedelta(hours=int(second_top_time[0]), minutes=int(second_top_time[1])) - \
                    timedelta(hours=int(first_top_time[0]), minutes= int(first_top_time[1])) 
    return time_distance

def price_distance_between_peaks(candle:Candle, trade:Trade):
    """Расстояние по цене от оцениваемой вершинки до прежденго максимума

    Arguments:
        candle {Candle} -- свеча
    """    
    distance = float(trade.high_candle.high) - float(candle.high)
    return distance

def price_distance_high_low_of_day(trade):
    """Расстояние между максимальным и минимальным значением за день"""
    price_distance = trade.max_value - trade.min_value
    return price_distance
    


def data_to_draw(candle_list):
    """Приводим список свечей к виду датафрейма, чтобы было легче отрисовать"""
    dataframe = []
    for candle in candle_list:
        # Приводим дату к нормальному формату
        time = candle.time.split(':')
        date = candle.date.split('/')
        time_value = datetime(year=int('20'+date[2]), month=int(date[1]), day=int(date[0]), hour=int(time[0]), minute=int(time[1]))
        candle_dict = {'date':time_value, 'open':candle.open,'high':candle.high, 'low':candle.low, 'close':candle.close, 'result':candle.result}
        dataframe.append(candle_dict)
    return dataframe

    
def accumulative(profit):
    prev_value = profit[0]
    result={}
    for i in range(len(profit)):
        if i == 0:
            result[str(i)] = profit[0]
        else:
            prev_value+=profit[i]
            result[str(i)] = prev_value
    return result



if __name__ == "__main__":
    #b = split_for_days(a)
    result = main('SBRF.csv')
    # graph_drawinggraph_drawing('/home/arcsinx/Рабочий стол/финансы/first_strategy/SBRF.csv')

