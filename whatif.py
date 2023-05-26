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
from streamlit_toggle import st_toggle_switch

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

def getAvgCTR(dt):
    if 'CLICKS_x' in dt:
        return (dt['CLICKS_x'].sum()/dt['IMPRESSIONS'].sum())/100  
    return (dt['CLICKS'].sum()/dt['IMPRESSIONS'].sum())/100     

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
    # colTop,colTop2=st.columns([1,6])
    # with colTop:
    advFilter=st.session_state.get('advFilter')
    auto=st.session_state.get('switch_1')
    st_toggle_switch(
        label="Assistance",
        key="switch_1",
        default_value=False,
        label_after=False,
        inactive_color="#D3D3D3",  
        active_color="#8b8b8b", 
        track_color="#716f6f", 
    )
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
    # tab1, tab2 = st.tabs(["Manual","Assisted"])


    if auto==False or auto is None:
        ads=st.session_state.get('ads') 
        if ads is None:
            ads=[]
            costSel=0 
        else:    
            if len(ads)>0:    
                dt=dt[~dt["LINE_ITEM"].isin(ads)] 
                costSel=getTotalCost(dt) +1   
            else:
                costSel=0   


        avgCTRT1=getAvgCTR(dt)
        avgCTROrigT1=getAvgCTR(orig)

        totalcostOrig=getTotalCost(orig) 
        compared=((costSel/totalcostOrig))*100
        comparedCTR=abs(float(((avgCTRT1-avgCTROrigT1)/avgCTROrigT1)*100))
        pgcolor='green'
        if(avgCTRT1<avgCTROrigT1):
            pgcolor='red'
        st.subheader("Simulate CTR"  )
        colL1,colR1=st.columns(2)
        with colL1:
            getCard(text="ORIGINAL CTR(%)",anim=False,val=str(round(avgCTROrigT1,3))+'%',icon='fa fa-map-marker-alt',compare=False,key='ctrorig',unit='$',progressColor='transparent')  
        with colR1:
            getCard(text='NEW CTR(%):',val=str(round(avgCTRT1,3))+'%', icon='fa fa-hand-pointer',compare=True,key='ctropt',progressValue=comparedCTR,unit='$',progressColor=pgcolor) 
        
        getAdsSelectionBox(orig,dt)  

        with st.expander("Budget Impact",expanded=False):
            colL,colR=st.columns(2)
            with colL:
                getCard(text="ORIGINAL COST",anim=False,val="{:,}".format(round(totalcostOrig))+'$',icon='fa fa-money-bill',compare=False,key='zero',unit='$',progressColor='transparent')  
            with colR:
                getCard(text='BUDGET BUFFER:',val=int(costSel), icon='fa fa-piggy-bank',compare=True,key='minusone',progressValue=compared,unit='$') 


    else:
        clusterSelected=st.session_state.get('clusterstore')
        if st.session_state.get('clusNum') is not None:
            kmeans = KMeans(init="random", n_clusters=st.session_state.get('clusNum'), n_init=10, random_state=1)
        else:
            kmeans = KMeans(init="random", n_clusters=5, n_init=10, random_state=1)
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
    
        minCTR=clusterDF['CTR'].min()
        suggestedCluster=clusterDF.loc[clusterDF['CTR']==minCTR]['CLUSTER'].iloc[0]
        avgCTR=getAvgCTR(dt2)
        avgCTROrig=getAvgCTR(orig)  
        comparedCTR=abs(float(((avgCTR-avgCTROrig)/avgCTROrig)*100))   
        totalcost=getTotalCost(dt2)
        totalcostOrig=getTotalCost(orig)
        compared=(1-((totalcost/totalcostOrig)))*100
        pgcolor='green'
        if(avgCTR<avgCTROrig):
            pgcolor='red'
        st.subheader("Simulate CTR Scientifically"  )

        colL1,colR1=st.columns(2)
        with colL1:
            getCard(text="ORIGINAL CTR(%)",anim=False,val=str(round(avgCTROrig,3))+'%',icon='fa fa-map-marker-alt',compare=False,key='ctrorigScience',unit='$',progressColor='transparent')  
        with colR1:
            getCard(text='NEW CTR(%):',val=str(round(avgCTR,3))+'%', icon='fa fa-hand-pointer',compare=True,key='ctroptScience',progressValue=comparedCTR,unit='$',progressColor=pgcolor) 

        colL,colR=st.columns(2)  
        st.info(f'''Based on an advanced analysis, the system suggests excluding cluster {suggestedCluster} first. ''', icon="ℹ️") 
        with colL: 
            st.slider('Cluster Number',2,10,value=5,key='clusNum')
        with colR:
            st.multiselect('Exclude Cluster:',np.unique(kmeans.labels_),key='clusterstore')

        with st.expander("Budget Impact",expanded=False):
            colo,cols=st.columns(2) 
            with colo:
                getCard(text="ORIGINAL COST",anim=False,val="{:,}".format(round(totalcostOrig))+'$',icon='fa fa-money-bill',compare= True,progressColor='transparent',key='one',unit='$')  
            with cols:
                getCard(text='BUDGET BUFFER: ',val=int(totalcostOrig - totalcost), icon='fa fa-piggy-bank',compare= True,key='two',unit='$',progressValue=(int(totalcostOrig - totalcost)/int(totalcostOrig))*100)  
    
        if clusterSelected is not None and  len(clusterSelected)>0:     
            fig = px.scatter(
                clusterDF,
                x="CTR",
                size="IMPRESSIONS_INT",
                y='COSTS',
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
                x="CTR",
                size="IMPRESSIONS_INT",
                y='COSTS',
                color="CLUSTER",
                hover_name="LINE_ITEM",
                size_max=30,
                height=400
            )
        fig.update_layout(xaxis={'visible': True, 'showticklabels': False},yaxis={'visible': True, 'showticklabels': False})    
        st.subheader("Clustering Ads by IMPRESSIONS and CTR"  )      
        st.plotly_chart(fig, theme="streamlit",use_container_width=True) 