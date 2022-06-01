import streamlit as st
import pandas_ta as ta
import streamlit.components.v1 as components
import pandas as pd
import numpy as np
import plotly.express as px
from plotly.subplots import make_subplots
import plotly.graph_objects as go
import yfinance as yf
#Setting page config
st.set_page_config(layout='wide')
st.markdown("<h1 style='text-align: center;'>AD Crypto Price Platform</h1>", unsafe_allow_html=True)


#Creating sidebar
with st.sidebar:
    st.title("Team AD")
    st.write("Haitham (20210625)")
    st.write("Leo de Figueiredo (20210667)")
    st.write("Nick (20210648)")
    st.write("Roeland (20200759)")
    st.write("A simple to use dashboard for analysing various cryptocurrencies.")
    st.header("Crypto Currency")

    coin = st.sidebar.selectbox('Select Coin:', ["ADA-USD", "ATOM-USD", "AVAX-USD", "AXS-USD", "BTC-USD", "ETH-USD","LINK-USD","LUNA1-USD","MATIC-USD","SOL-USD"])
    indicator = st.sidebar.selectbox('Select Financial Indicator:', ["Historical Price", "MACD"])
    date_range = st.sidebar.select_slider("Select Date Range:", ["1d","1mo","3mo","6mo","1yr"])

#Fetching live financial info
live_coin_data = yf.Ticker(coin)
coin_data = pd.read_csv("coin_data/" + coin + ".csv")
live_price = round(float(live_coin_data.history(period= "1m")["Close"]),2)

#defining MACD
# get ticker data
df = live_coin_data.history(period=date_range)[map(str.title, ['open', 'close', 'low', 'high', 'volume'])]
# calculate MACD values
df.ta.macd(close='close', fast=12, slow=26, append=True)
# Force lowercase (optional)
df.columns = [x.lower() for x in df.columns]
# Construct a 2 x 1 Plotly figure
fig_macd = make_subplots(rows=2, cols=1)
# price Line
fig_macd.append_trace(
    go.Scatter(
        x=df.index,
        y=df['open'],
        line=dict(color='#ff9900', width=1),
        name='open',
        # showlegend=False,
        legendgroup='1',
    ), row=1, col=1
)
# Candlestick chart for pricing
fig_macd.append_trace(
    go.Candlestick(
        x=df.index,
        open=df['open'],
        high=df['high'],
        low=df['low'],
        close=df['close'],
        increasing_line_color='green',
        decreasing_line_color='black',
        showlegend=False
    ), row=1, col=1
)
# Fast Signal (%k)
fig_macd.append_trace(
    go.Scatter(
        x=df.index,
        y=df[df.columns[-3]],
        line=dict(color='orange', width=2),
        name='macd',
        # showlegend=False,
        legendgroup='2',
    ), row=2, col=1
)
# Slow signal (%d)
fig_macd.append_trace(
    go.Scatter(
        x=df.index,
        y=df[df.columns[-1]],
        line=dict(color='green', width=2),
        # showlegend=False,
        legendgroup='2',
        name='signal'
    ), row=2, col=1
)
# Colorize the histogram values
colors = np.where(df[df.columns[-2]] < 0, '#000', '#ff9900')
# Plot the histogram
fig_macd.append_trace(
    go.Bar(
        x=df.index,
        y=df[df.columns[-2]],
        name='histogram',
        marker_color=colors,
    ), row=2, col=1
)

#Creating columns
col1, col2 = st.columns(2)

#Layout for col1
col1.subheader("Live Price")
col1.metric(label=coin, value=round(live_price,4))

prediction = round(pd.read_csv("Preds/" + coin + ".csv")["0"].iloc[-1],2)
delta = ((prediction - live_price)/live_price)*100

col1.metric(label=coin + " Predicted Value for Tomorrow", value=prediction, delta=str(round(delta,2)) + "%")


if indicator == "Historical Price":
    if date_range == "1d":
        date_range = "1mo"
    fig = px.line(live_coin_data.history(period=date_range), y = "Close", title = "Historical Price " + "of " + coin + "(" + date_range + ")")
    col1.plotly_chart(fig, use_container_width=True)
elif indicator == "MACD":
    col1.subheader(indicator + " of " + coin)
    col1.plotly_chart(fig_macd, use_container_width=True)
#Layout for col2
#col2.subheader("Trend Goes Here")


col2.subheader("RSI")

fig_rsi = go.Figure()
rsi_date_picker = col2.select_slider("Pick a length of days:", [1,3,5,15,30])
fig_rsi.add_trace(go.Indicator(
    domain = {'x': [0, 1], 'y': [0, 1]},
    value = int(coin_data.iloc[-rsi_date_picker]['rsi']),
    mode = "gauge+number+delta",
    title = {'text': "RSI"},
    delta = {'reference': int(coin_data.iloc[-rsi_date_picker]['rsi'])},
    gauge = {'axis': {'range': [None, 100]},
             'bar': {'color': "blue"},
             'steps' : [
                 {'range': [0, 30], 'color': "lightgreen"},
                 {'range': [70, 100], 'color': "crimson"}],
             'threshold' : {'line': {'color': "red", 'width': 4}, 'thickness': 0.75, 'value': 490}}))
col2.plotly_chart(fig_rsi)
