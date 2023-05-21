from streamlit_kpi import streamlit_kpi
import streamlit as st
import pandas as pd
from streamlit_kpi import streamlit_kpi
from lib import GLOBAL_SCALE_FACTOR, getAdvertiserData, getClickDataByAdvertiser,getIndustryData,getClickDataByIndustry,getDistinctIndustry,getDistinctAds,getDistinctCountries


def getCard(text,val,icon, key,compare=False,anim=True,titleTextSize="16vw",content_text_size="10vw",unit="%",height='200',iconLeft=90,iconTop=80,backgroundColor='white',progressValue=100,progressColor='green',showProgress=True):
    if compare==False:
        streamlit_kpi(showProgress=showProgress,key=key+"_n",height=height,animate=anim,title=text,value=val,icon=icon,progressValue=progressValue,unit=unit,progressColor=progressColor,iconLeft=iconLeft,iconTop=iconTop,backgroundColor=backgroundColor)
    else:
        streamlit_kpi(showProgress=showProgress,key=key+"_n",height=height,animate=anim,title=text,value=val,icon=icon,progressValue=progressValue,unit=unit,iconLeft=iconLeft,progressColor=progressColor,iconTop=iconTop,backgroundColor=backgroundColor)  

def generateCheck(lst,col):
    lst=pd.DataFrame(lst, columns=[col])
    for index, row in lst.iterrows():
        st.checkbox(row[col],key=col+"_"+str(index),value=True)

def getPage(sess):
    colL,colR=st.columns([1,4])

    with colL:
        with st.expander('INDUSTRY:', expanded=True):
            ind=st.selectbox("INDUSTRY:", getDistinctIndustry(),index=0,key='indusFilter')
        with st.expander('ADS TYPE', expanded=True):
            generateCheck(getDistinctAds(), "LINE_ITEM")
        with st.expander('COUNTRY', expanded=False):    
            generateCheck(getDistinctCountries(), "COUNTRY")
    
    
    industry_impressions=getIndustryData(ind)
    industry_clicks=getClickDataByIndustry(ind)
    data = [industry_impressions, industry_clicks]
    all_industry = pd.concat(data)

    advFilter=st.session_state.get('advFilter')
    currrent_impressions=getAdvertiserData(advFilter)
    current_clicks=getClickDataByAdvertiser(advFilter)
    dtc = [currrent_impressions, current_clicks]
    all_current = pd.concat(dtc)

    

    hg = "643"
    totalClicks_industry=int(industry_clicks[["CLICKS"]].sum().iloc[0])
    totalClicks_current=int(current_clicks[["CLICKS"]].sum().iloc[0])

    with colR:
        colInd,colYou=st.columns([3,3])
        with colInd:
            getCard(ind.upper()+" CTR(%)",str(round((totalClicks_industry/len(industry_impressions))*100,2))+'%' ,'fa fa-money-bill',key='indust_card_bench',unit="",height=hg,showProgress=False)
        with colYou:
            getCard("YOUR CTR (%)",str(round((totalClicks_current/len(currrent_impressions))*100,2))+'%' ,'fa fa-money-bill',key='current_card_bench',unit="",height=hg)

    # st.dataframe(countries)