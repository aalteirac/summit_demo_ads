import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from st_aggrid import AgGrid
import numpy as np
from streamlit_kpi import streamlit_kpi
import numbers
import numpy as np
from datetime import datetime
from lib import GLOBAL_SCALE_FACTOR, getAdvertiserData, getClickDataByAdvertiser


session=None

def alpha3code(column):
    CODE=[]
    for country in column:
        try:
            code=pycountry.countries.get(name=country).alpha_3
           # .alpha_3 means 3-letter country code 
           # .alpha_2 means 2-letter country code
            CODE.append(code)
        except:
            if country=='Bolivia':
                CODE.append('BOL')
            if country=='Venezuela':
                CODE.append('VEN')    
    return CODE

def getCard(text,val,icon, key,compare=False,titleTextSize="11vw",content_text_size="7vw",unit="%",height='150',iconLeft=85,iconTop=50,backgroundColor='#f0f2f6', animate=True):
    pgcol='green'
    if isinstance(val, numbers.Number):
        if val<0:
            pgcol='red'
    if compare==False:
        pgcol='darkgrey'
    if compare==False:
        streamlit_kpi(key=key+"_n",height=height,title=text,value=val,icon=icon,unit=unit,iconLeft=iconLeft,showProgress=False,iconTop=iconTop,backgroundColor=backgroundColor, animate=animate, borderSize='1px')
    else:
        streamlit_kpi(key=key+"_n",height=height,title=text,value=val,icon=icon,progressValue=100,unit=unit,iconLeft=iconLeft,showProgress=True,progressColor=pgcol,iconTop=iconTop,backgroundColor=backgroundColor, animate=animate, borderSize='1px')  

def getChartClickCTR(df):
    # col=['#B6E2A1','#FEBE8C','#F7A4A4']
    col=['#B6E2A1','#FEBE8C','#FF7171']
    fig = go.Figure(data=[
        go.Bar(name='IMPRESSIONS', x=df['MONTH'], y=df['IMPRESSIONS'],yaxis='y',offsetgroup=1,marker={'color':col[0]}),
        go.Bar(name='CLICKS', x=df['MONTH'], y=df['CLICKS'],yaxis='y2',offsetgroup=2,marker={'color':col[1]}),
        go.Line(name='CTR(%)',x=df['MONTH'], y=df['CTR'],yaxis='y3',offsetgroup=3,marker={'color':col[2]})
    ],layout={
        'yaxis': {'title': 'IMPRESSIONS','showgrid':False,'showline':False},
        'yaxis2': {'title': 'CLICKS', 'overlaying': 'y', 'side': 'right','showgrid':False,'showline':False},
        'yaxis3': {'title': 'CTR(%)', 'overlaying': 'y', 'side': 'left','position':0.05,"anchor":"free",'showgrid':False,'showline':False,'visible':False}
    })
    fig.update_layout(barmode='group',height=700, title='Impressions, Clicks & CTR(%)')
    st.plotly_chart(fig, theme="streamlit",use_container_width=True)

def getKPIByMonth(df):
    mt=df.groupby(['MONTH']).agg({'IMPRESSIONS':'sum',
            'CLICKS':'sum'})
    mt['CTR']=(mt['CLICKS']/mt['IMPRESSIONS'] )*100       
    # st.dataframe(mt)    
    return mt.reset_index()

def random_dates(start, end, n=10):
    start_u = start.value//10**9
    end_u = end.value//10**9
    return pd.to_datetime(np.random.randint(start_u, end_u, n), unit='s')

def getPage(sess):
    advFilter=st.session_state.get('advFilter')

    rawAdvertData=getAdvertiserData(advFilter)
    rawClicksData=getClickDataByAdvertiser(advFilter)
    uniqueAdds=np.sort(rawAdvertData['ORDERNAME'].unique())
    uniqueAddsType=rawAdvertData['LINE_ITEM'].unique()

    colCt,colCg= st.columns(2)
    campaignFilter=colCt.multiselect("Select Campaigns:", uniqueAdds,default=[])
    addTypeFilter=colCg.multiselect("Select Ads:", uniqueAddsType,default=[])

    if len(addTypeFilter)!=0 or len(campaignFilter)!=0: 
        if len(campaignFilter)!=0:
            rawAdvertData=rawAdvertData[rawAdvertData['ORDERNAME'].isin(campaignFilter)]
            rawClicksData=rawClicksData[rawClicksData['ORDERNAME'].isin(campaignFilter)]
        if len(addTypeFilter)!=0:
            rawAdvertData=rawAdvertData[rawAdvertData['LINE_ITEM'].isin(addTypeFilter)]  
            rawClicksData=rawClicksData[rawClicksData['LINE_ITEM'].isin(addTypeFilter)]  

    col1, col2 = st.columns([1,5])
    hg = "203"
    totalClicks=int(rawClicksData[["CLICKS"]].sum().iloc[0])
    with col1:
        getCard("IMPRESSIONS",int(len(rawAdvertData))*GLOBAL_SCALE_FACTOR,'fa fa-desktop',key='five',height=hg,unit='')
        getCard("CLICKS",totalClicks*GLOBAL_SCALE_FACTOR,'fa fa-hand-pointer',key='six',height=hg,unit='')
        getCard("CTR (%)",str(round((totalClicks/len(rawAdvertData))*100,2))+'%' ,'fa fa-money-bill',key='seven',unit="",height=hg)

    data = [rawAdvertData, rawClicksData]
    all = pd.concat(data)
    with col2:
        getChartClickCTR(getKPIByMonth(all))



# @st.cache_data(show_spinner=False,ttl=5000)
# def getDistinctAdvertisers():
#     df=session.sql(f'''
#     select distinct ADVERTISER_NAME from SUMMIT_JIM_DB.RAW_SC."CLICKS";
#     ''').collect()
#     return df
# ar=["Social media ads","Programmatic display ads","Influencer marketing campaigns","Native advertising","Search engine marketing (SEM)","Audio ads","Geofencing ads","Interactive ads","Connected TV ads","Over-the-top ads"]
# mp=getMappingAdvertiser()
# allMP=mp

# mp=mp[mp["ID"]==advFilter] 

# mp=mp.drop_duplicates(subset=['ID'])
# mp.rename(columns = {'ID':'ADVERTISERID'}, inplace = True)

# df_outer = pd.merge(rawAdvertData, mp, on='ADVERTISERID')
# df_outer = df_outer.drop('AD_SLOGAN', axis=1)
# result = []
# dateF = []
# start = pd.to_datetime('2022-04-01')
# end = pd.to_datetime('2023-05-01')
# ts=random_dates(start, end,len(df_outer))
# for index, row in df_outer.iterrows():
#     fl=allMP[allMP["ADVERTISER_NAME"]==row["ADVERTISER_NAME"]] 
#     dd=fl.sample()
#     result.append(dd['AD_SLOGAN'].iloc[0]) 

# df_outer["ORDERNAME"] = result 
# df_outer["TIME_TS"] = ts
# df_outer["LINE_ITEM"]=np.random.choice(list(ar), len(df_outer))
# st.dataframe(df_outer.sample(2000))

# session.write_pandas(df_outer,"CLICKS", auto_create_table=True, database='SUMMIT_JIM_DB',schema='RAW_SC')
