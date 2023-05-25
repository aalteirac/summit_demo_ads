from streamlit_kpi import streamlit_kpi
import streamlit as st
import pandas as pd
from streamlit_kpi import streamlit_kpi
from lib import GLOBAL_SCALE_FACTOR, getAdvertiserData, getClickDataByAdvertiser,getIndustryData,getClickDataByIndustry,getDistinctIndustry,getDistinctAds,getDistinctCountries,getAdvertiserIndustry


def getCard(text,val,icon, key,compare=False,anim=True,titleTextSize="16vw",content_text_size="10vw",unit="%",height='200',iconLeft=90,iconTop=40,backgroundColor='white',progressValue=100,progressColor='green',showProgress=True):
    if compare==False:
        streamlit_kpi(showProgress=showProgress,key=key+"_n",height=height,animate=anim,title=text,value=val,icon=icon,progressValue=progressValue,unit=unit,progressColor=progressColor,iconLeft=iconLeft,iconTop=iconTop,backgroundColor=backgroundColor)
    else:
        streamlit_kpi(showProgress=showProgress,key=key+"_n",height=height,animate=anim,title=text,value=val,icon=icon,progressValue=progressValue,unit=unit,iconLeft=iconLeft,progressColor=progressColor,iconTop=iconTop,backgroundColor=backgroundColor)  

def generateCheck(lst,col):
    lst=pd.DataFrame(lst, columns=[col])
    for index, row in lst.iterrows():
        st.checkbox(row[col],key=col+"_"+row[col],value=True)  

def getCheckBoxesState(col):
    sel=[]
    for key in st.session_state.keys():
        if key.startswith(col+'_'):
            if st.session_state[key]==True:
                sel.append(key.replace(col+'_',''))
    return sel            

def getPage(sess):
    advFilter=st.session_state.get('advFilter')
    indust_current=pd.DataFrame(getAdvertiserIndustry(advFilter)).iloc[0]['INDUSTRY']
    distinct_industries=pd.DataFrame(getDistinctIndustry())
    indust_current_idx=pd.DataFrame(distinct_industries.index[distinct_industries['INDUSTRY'] == indust_current]).iloc[0,0]
    colL,colR=st.columns([1,4])
    with colL:
        with st.expander('INDUSTRY:', expanded=True):
            ind=st.selectbox("INDUSTRY:", distinct_industries,index=int(indust_current_idx),key='indusFilter')
        with st.expander('ADS TYPE', expanded=True):
            generateCheck(getDistinctAds(), "LINE_ITEM")
        with st.expander('COUNTRY', expanded=False):    
            generateCheck(getDistinctCountries(), "COUNTRY")
    
    
    industry_impressions=getIndustryData(ind)
    industry_clicks=getClickDataByIndustry(ind)
    data = [industry_impressions, industry_clicks]
    all_industry = pd.concat(data)

    currrent_impressions=getAdvertiserData(advFilter)
    current_clicks=getClickDataByAdvertiser(advFilter)
    dtc = [currrent_impressions, current_clicks]
    all_current = pd.concat(dtc)

    
    # filterhere
    industry_clicks=industry_clicks[industry_clicks["COUNTRY"].isin(getCheckBoxesState("COUNTRY"))]
    industry_impressions=industry_impressions[industry_impressions["COUNTRY"].isin(getCheckBoxesState("COUNTRY"))]
    industry_clicks=industry_clicks[industry_clicks["LINE_ITEM"].isin(getCheckBoxesState("LINE_ITEM"))]
    industry_impressions=industry_impressions[industry_impressions["LINE_ITEM"].isin(getCheckBoxesState("LINE_ITEM"))]

    current_clicks=current_clicks[current_clicks["COUNTRY"].isin(getCheckBoxesState("COUNTRY"))]
    currrent_impressions=currrent_impressions[currrent_impressions["COUNTRY"].isin(getCheckBoxesState("COUNTRY"))]
    current_clicks=current_clicks[current_clicks["LINE_ITEM"].isin(getCheckBoxesState("LINE_ITEM"))]
    currrent_impressions=currrent_impressions[currrent_impressions["LINE_ITEM"].isin(getCheckBoxesState("LINE_ITEM"))]

    # st.dataframe(current_clicks)
    # st.dataframe(currrent_impressions)


    hg = "561"
    totalClicks_industry=int(industry_clicks[["CLICKS"]].sum().iloc[0])
    totalClicks_current=int(current_clicks[["CLICKS"]].sum().iloc[0])
    if len(industry_impressions)==0:
        colR.title(ind.upper()+ ' INDUSTRY vs YOUR PERFORMANCE:')
        colR.text('No Data...')
        return
    industry_ctr=round((totalClicks_industry/len(industry_impressions))*100,3)
    if len(currrent_impressions)==0:
        current_ctr='No Data...'
    else:
        current_ctr=round((totalClicks_current/len(currrent_impressions))*100,3)

    color='lightgrey'
    if type(current_ctr) is not str: 
        if(industry_ctr>current_ctr):
            color='red'
        else:
            color='green'
        current_ctr= str(current_ctr)+'%'    

    with colR:
        st.title(ind.upper()+ ' INDUSTRY vs YOUR PERFORMANCE:')
        colInd,colYou=st.columns([3,3])
        with colInd:
            getCard("CTR",str(industry_ctr)+'%' ,'fas fa-industry',key='indust_card_bench',unit="",height=hg,progressColor='lightgrey')
        with colYou:
            getCard("YOUR CTR",current_ctr ,'fa fa-hand-pointer',key='current_card_bench',unit="",height=hg,progressColor=color)

    # st.dataframe(countries)