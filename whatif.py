import streamlit as st
import pandas as pd
from math import log, floor
from sklearn.cluster import KMeans
import plotly.express as px
import numpy as np
from streamlit_kpi import streamlit_kpi
import numbers
from lib import getDistinctAdvertisers

CTR_FACTOR=0.5

session=None


def getAdvertiserData(adv):
    df=session.sql(f'''
    select *,1 as IMPRESSIONS,CAST(1 AS DECIMAL(7,2) ) as IMPDEC,
    to_date(TO_VARCHAR(to_date(to_timestamp(time_ts/1000000)), 'yyyy-MM-01')) as MONTH,
    to_date(to_timestamp(time_ts/1000000)) as DATE_IMP from SUMMIT_JIM_DB.RAW_SC."IMPRESSIONS" 
    WHERE ADVERTISER_NAME='{adv}';
    ''').collect()
    return pd.DataFrame(df)

def getClickDataByAdvertiser(adv):
    df=session.sql(f'''
    select *, {CTR_FACTOR} as CLICKS,
    to_date(TO_VARCHAR(to_date(to_timestamp(time_ts/1000000)), 'yyyy-MM-01')) as MONTH,
    to_date(to_timestamp(time_ts/1000000)) as DATE_IMP from SUMMIT_JIM_DB.RAW_SC."CLICKS" 
    WHERE ADVERTISER_NAME='{adv}';
    ''').collect()
    return pd.DataFrame(df)  

def getCard(text,val,icon, key,compare=False,anim=True,titleTextSize="16vw",content_text_size="10vw",unit="%",height='200',iconLeft=90,iconTop=80,backgroundColor='white',progressValue=100,progressColor='green'):
    if compare==False:
        streamlit_kpi(key=key+"_n",height=height,animate=anim,title=text,value=val,icon=icon,progressValue=progressValue,unit=unit,progressColor=progressColor,iconLeft=iconLeft,showProgress=True,iconTop=iconTop,backgroundColor=backgroundColor)
    else:
        streamlit_kpi(key=key+"_n",height=height,animate=anim,title=text,value=val,icon=icon,progressValue=progressValue,unit=unit,iconLeft=iconLeft,showProgress=True,progressColor=progressColor,iconTop=iconTop,backgroundColor=backgroundColor)  

def getTotalCost(df):
    if 'COSTS' in df:
        return df['COSTS'].sum()  
    if 'COSTS_x' in df:
        return df['COSTS_x'].sum()      

def getCampaignSelectionBox(raw,selec):
    raw=raw.sort_values(['ORDERNAME'])
    return st.multiselect(
        'Remove Campaign:',
    raw['ORDERNAME'].unique(),default=[],key="campaign")

def getAdsSelectionBox(map,selec):
    return st.multiselect(
        'Remove Ads:',
    map['LINE_ITEM'].unique(),default=[],key='ads')

def setShape (x):
    if x == True:
        return "circle-open"
    else:
        return "open"
    
def getPage(sess):
    global session 
    session = sess
    advFilter=st.session_state.get('advFilter')
    rawAdvertData=getAdvertiserData(advFilter)
    rawClicksData=getClickDataByAdvertiser(advFilter)
    data = [rawAdvertData, rawClicksData]
    dt = pd.concat(data)
    dt=dt.reset_index()
    dt['IMPRESSIONS']=dt['IMPRESSIONS']*9999
    dt['CLICKS']=dt['CLICKS']*9999
    dt['COSTS']=round(dt['SELLERRESERVEPRICE']*9999,2)
    orig=dt.copy()
    dt2=orig.copy()
    tab1, tab2 = st.tabs(["Manual","Assisted"])

    with tab1:
        campaings=st.session_state.get('campaign') 
        ads=st.session_state.get('ads') 
        if campaings is None:
            campaings=[]
            ads=[]
        else:   
            if len(campaings)>0: 
                dt=dt[dt["ORDERNAME"].isin(campaings)]
            if ads is not None:    
                if len(ads)>0:    
                    dt=dt[dt["LINE_ITEM"].isin(ads)] 
        totalcostOrig=getTotalCost(orig)
        if len(campaings)>0:
            costSel=getTotalCost(dt)
        else:
            costSel=0    
        compared=((costSel/totalcostOrig))*100
        st.subheader("Rebalance Budget Manually"  )
        colL,colR=st.columns(2)
        with colL:
            getCard(text="ORIGINAL COST",anim=False,val="{:,}".format(round(totalcostOrig))+'$',icon='fa fa-money-bill',compare=False,key='zero',unit='$',progressColor='transparent')  
        with colR:
            getCard(text='BUDGET BUFFER:',val=int(costSel), icon='fa fa-piggy-bank',compare=True,key='minusone',progressValue=compared,unit='$') 
        getCampaignSelectionBox(orig,dt) 
        if len(campaings)>0:
            getAdsSelectionBox(orig,dt)   

    with tab2:
        clusterSelected=st.session_state.get('clusterstore')
        if st.session_state.get('clusNum') is not None:
            kmeans = KMeans(init="random", n_clusters=st.session_state.get('clusNum'), n_init=10, random_state=1)
        else:
            kmeans = KMeans(init="random", n_clusters=3, n_init=10, random_state=1)
        clusterDF=orig.groupby(['LINE_ITEM']).agg({
                                'IMPRESSIONS':'sum',
                                'IMPDEC':'sum',
                                'CLICKS':'sum',
                                'COSTS':'mean'}).reset_index()
        clusterDF['CTR']=(clusterDF['CLICKS']/clusterDF['IMPDEC'] )*100                                  
        kmeans.fit(clusterDF[['CTR','COSTS']])  
        clusterDF['CLUSTER'] = kmeans.labels_ 
        clusterDF['CLUSTER']  = clusterDF['CLUSTER'].astype(str)
        clusterDF=clusterDF.sort_values(['CLUSTER'])
        if clusterSelected is not None and  len(clusterSelected)>0:
            dt2=pd.merge(dt2, clusterDF[~clusterDF['CLUSTER'].isin(list(map(str, clusterSelected)))],on=["LINE_ITEM"])
            clusterDF['EXCLUDED']= clusterDF['CLUSTER'].isin(list(map(str, clusterSelected)))  
        totalcost=getTotalCost(dt2)
        totalcostOrig=getTotalCost(orig)
        compared=(1-((totalcost/totalcostOrig)))*100
        st.subheader("Rebalance Budget Scientifically"  )
        colL,colR=st.columns(2)
        with colL:
            getCard(text="ORIGINAL COST",anim=False,val="{:,}".format(round(totalcostOrig))+'$',icon='fa fa-money-bill',compare= True,progressColor='transparent',key='one',unit='$')  
        with colR:
            getCard(text='BUDGET BUFFER: ',val=int(totalcostOrig - totalcost), icon='fa fa-piggy-bank',compare= True,key='two',unit='$',progressValue=(int(totalcostOrig - totalcost)/int(totalcostOrig))*100) 
        colL,colR=st.columns(2)   
        with colL: 
            st.slider('Cluster Number',2,10,value=3,key='clusNum')
        with colR:
            st.multiselect('Exclude Cluster:',np.unique(kmeans.labels_),key='clusterstore')
    
        if clusterSelected is not None and  len(clusterSelected)>0:     
            fig = px.scatter(
                clusterDF,
                y="CTR",
                size="IMPRESSIONS",
                x='COSTS',
                color="CLUSTER",
                symbol = 'EXCLUDED',
                symbol_map={True:'circle-open',False:'circle'},
                # symbol = 'EXCLUDED',
                # symbol_sequence= [ 'circle-open','circle'],
                hover_name="LINE_ITEM",
                size_max=30,
                height=430
            ) 
        else:
            fig = px.scatter(
                clusterDF,
                y="CTR",
                size="IMPRESSIONS",
                x='COSTS',
                color="CLUSTER",
                hover_name="LINE_ITEM",
                size_max=30,
                height=400
            )
        fig.update_layout(xaxis={'visible': True, 'showticklabels': False})    
        st.subheader("Clustering Ads by IMPRESSIONS and CTR"  )      
        st.plotly_chart(fig, theme="streamlit",use_container_width=True)   