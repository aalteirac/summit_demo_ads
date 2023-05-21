import streamlit as st
import pandas as pd
from math import log, floor
from sklearn.cluster import KMeans
import plotly.express as px
import numpy as np
from streamlit_kpi import streamlit_kpi
import numbers
from lib import GLOBAL_SCALE_FACTOR, getAdvertiserData, getClickDataByAdvertiser
import math

session=None


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
    advFilter=st.session_state.get('advFilter')
    rawAdvertData=getAdvertiserData(advFilter)
    rawClicksData=getClickDataByAdvertiser(advFilter)
    data = [rawAdvertData, rawClicksData]
    dt = pd.concat(data)
    dt=dt.reset_index()
    dt['IMPRESSIONS_INT']=dt['IMPRESSIONS_INT']*GLOBAL_SCALE_FACTOR
    dt['CLICKS']=dt['CLICKS']*GLOBAL_SCALE_FACTOR
    dt['COSTS']=round(dt['SELLERRESERVEPRICE']*GLOBAL_SCALE_FACTOR,2)
    orig=dt.copy()
    dt2=orig.copy()
    tab1, tab2 = st.tabs(["Manual","Assisted"])

    with tab1:
        ads=st.session_state.get('ads') 
        if ads is None:
            ads=[]
            costSel=0 
        else:    
            if len(ads)>0:    
                dt=dt[dt["LINE_ITEM"].isin(ads)] 
                costSel=getTotalCost(dt) +1   
            else:
                costSel=0       
        totalcostOrig=getTotalCost(orig) 
        compared=((costSel/totalcostOrig))*100
        st.subheader("Rebalance Budget Manually"  )
        colL,colR=st.columns(2)
        with colL:
            getCard(text="ORIGINAL COST",anim=False,val="{:,}".format(round(totalcostOrig))+'$',icon='fa fa-money-bill',compare=False,key='zero',unit='$',progressColor='transparent')  
        with colR:
            getCard(text='BUDGET BUFFER:',val=int(costSel), icon='fa fa-piggy-bank',compare=True,key='minusone',progressValue=compared,unit='$') 

        getAdsSelectionBox(orig,dt)   

    with tab2:
        clusterSelected=st.session_state.get('clusterstore')
        if st.session_state.get('clusNum') is not None:
            kmeans = KMeans(init="random", n_clusters=st.session_state.get('clusNum'), n_init=10, random_state=1)
        else:
            kmeans = KMeans(init="random", n_clusters=3, n_init=10, random_state=1)
        clusterDF=orig.groupby(['LINE_ITEM']).agg({
                                'IMPRESSIONS_INT':'sum',
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
                size="IMPRESSIONS_INT",
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
                size="IMPRESSIONS_INT",
                x='COSTS',
                color="CLUSTER",
                hover_name="LINE_ITEM",
                size_max=30,
                height=400
            )
        fig.update_layout(xaxis={'visible': True, 'showticklabels': False})    
        st.subheader("Clustering Ads by IMPRESSIONS and CTR"  )      
        st.plotly_chart(fig, theme="streamlit",use_container_width=True)   