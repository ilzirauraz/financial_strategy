import plotly.graph_objects as go
import plotly.offline as py
import numpy as np
from datetime import timedelta, datetime
import plotly.express as px


import pandas as pd

def draw_buy(df, trade, take, take_value, prev_data = pd.DataFrame({'A' : []})):

        #Для целефой свечи 
        time = trade.target_candle.time.split(':')
        date = trade.target_candle.date.split('/')

        #Для take
        take_time = take.time.split(':')
        take_date = take.date.split('/')

    # try:
        time_value = datetime(year=int('20'+date[2]), month=int(date[1]), day=int(date[0]), hour=int(time[0]), minute=int(time[1]))

        take_time_value = datetime(year=int('20'+take_date[2]), month=int(take_date[1]), day=int(take_date[0]), hour=int(take_time[0]), minute=int(take_time[1]))
        df["Marker"] = np.where(df['date']==time_value, pd.to_numeric(df["close"]), None)
        df["Symbol"] = np.where(df["result"]==True, "triangle-down", "triangle-down")
        df["Color"] = np.where(df["open"]<df["close"], "red", "red")

        df["Marker_take"] = np.where(df['date']==take_time_value, take_value, None)
        df["Symbol_take"] = np.where(df["result"]==True, "triangle-up", "triangle-up")
        df["Color_take"] = np.where(df["open"]<df["close"], "green", "green")


        Candle = go.Candlestick(x=df['date'],
                    open=df['open'],
                    high=df['high'],
                    low=df['low'],
                    close=df['close'],
                            )

        Trace = go.Scatter(x=df['date'],
                        y=df.Marker,
                        mode='markers',
                        name ='markers',
                        marker=go.Marker(size=20,
                                            symbol=df["Symbol"],
                                            color=df["Color"]), 
                                            connectgaps = True )
        Take = go.Scatter(x=df['date'],
                y=df.Marker_take,
                mode='markers',
                name ='markers',
                marker=go.Marker(size=20,
                                    symbol=df["Symbol_take"],
                                    color=df["Color_take"]
                                    ),
                connectgaps = True
                )

        if not prev_data.empty:
            prev_Candle = go.Candlestick(x=prev_data['date'],
                    open=prev_data['open'],
                    high=prev_data['high'],
                    low=prev_data['low'],
                    close=prev_data['close'],
                            )
            data = [prev_Candle, Candle, Trace, Take ]

        else:
            data = [Candle, Trace, Take]
            

        

        layout1 = go.Layout(
        xaxis=dict(
            autorange=True,
            type = "category"
        ))

        fig = go.Figure(data=data, layout=layout1)
        fig.show()
    
    # except:
    #     print('Похоже, не сработало')

def draw_graph(df, trade, candle):
    time = candle.time.split(':')
    date = candle.date.split('/')

    time_value = datetime(year=int('20'+date[2]), month=int(date[1]), day=int(date[0]), hour=int(time[0]), minute=int(time[1]))
    
    df["Marker"] = np.where(df['date']==time_value, pd.to_numeric(df["close"]), np.nan)
    df["Symbol"] = np.where(df["result"]==True, "triangle-down", "triangle-down")
    df["Color"] = np.where(df["open"]<df["close"], "red", "red")
    
    Candle = go.Candlestick(x=df['date'],
                open=df['open'],
                high=df['high'],
                low=df['low'],
                close=df['close']
                        )

    Trace = go.Scatter(x=df['date'],
                    y=df.Marker,
                    mode='markers',
                    name ='markers',
                    marker=go.Marker(size=20,
                                        symbol=df["Symbol"],
                                        color=df["Color"]),
                                        connectgaps = True
                    )

    py.plot([Candle, Trace])

    fig = go.Figure(data=[go.Candlestick(x=df['date'],
                open=df['open'],
                high=df['high'],
                low=df['low'],
                close=df['close'])])


    # py.plot([Candle])
    # fig.show()
    fig.update_layout(xaxis_type='category')
        # figure.update(dict(layout=dict(xaxis_type='category'), data=dict(marker=dict(color='blue'))))
    py.iplot(fig, show_link=False)

    print('Похоже, не сработало')

def draw_result(data_draw):
    # data = pd.DataFrame(data_draw)
    # fig = px.bar(x=list(data_draw.keys()), y=list(data_draw.values()))
    # fig.show()

    fig = go.Figure(data=go.Scatter(x=list(data_draw.keys()), y=list(data_draw.values())))
    fig.show()