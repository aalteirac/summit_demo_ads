import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from st_aggrid import AgGrid, GridOptionsBuilder, JsCode,GridUpdateMode



session=None

@st.cache_data(show_spinner=False,ttl=5000)
def getDistinctAdvertisers():
    df=session.sql(f'''
    select distinct ADVERTISER_NAME from SUMMIT_JIM_DB.RAW_SC."CLICKS";
    ''').collect()
    return df

@st.cache_data(show_spinner=False,ttl=5000)
def getAdvertiserData(adv):
    df=session.sql(f'''
    select *,1 as IMPRESSIONS,
    to_date(TO_VARCHAR(to_date(to_timestamp(time_ts/1000000)), 'yyyy-MM-01')) as MONTH,
    to_date(to_timestamp(time_ts/1000000)) as DATE_IMP from SUMMIT_JIM_DB.RAW_SC."IMPRESSIONS" 
    WHERE ADVERTISER_NAME='{adv}';
    ''').collect()
    return pd.DataFrame(df)

@st.cache_data(show_spinner=False,ttl=5000)
def getClickDataByAdvertiser(adv):
    df=session.sql(f'''
    select *, 1 as CLICKS,
    to_date(TO_VARCHAR(to_date(to_timestamp(time_ts/1000000)), 'yyyy-MM-01')) as MONTH,
    to_date(to_timestamp(time_ts/1000000)) as DATE_IMP from SUMMIT_JIM_DB.RAW_SC."CLICKS" 
    WHERE ADVERTISER_NAME='{adv}';
    ''').collect()
    return pd.DataFrame(df)  

def getCTRByDevice(df):
    mt=df.groupby(['DEVICECATEGORY']).agg({'IMPRESSIONS':'sum',
            'CLICKS':'sum'})
    mt['CTR']=(mt['CLICKS']/mt['IMPRESSIONS'] )*100       
    return mt.reset_index()

def getTopBottomAds(df,bottom=True,n=3):
    mt=df.groupby(['ORDERNAME']).agg({'IMPRESSIONS':'sum',
            'CLICKS':'sum'})
    mt['CTR']=(mt['CLICKS']/mt['IMPRESSIONS'] )*100       
    return mt.sort_values(by=['CTR'],ascending=bottom).reset_index().head(n)

def getChartTopAds(df,asc=True,prefix='Top'):
    df=df.sort_values(by=['CTR'],ascending=asc)
    fig = go.Figure(data=[
        go.Bar(name='IMPRESSIONS', y=df['ORDERNAME'], x=df['CTR'],text=df['CTR']/100, orientation='h')
    ])
    fig.update_xaxes(visible=False, showticklabels=False)
    fig.data[0].marker.color = ('#B6E2A1','#FEBE8C','#F7A4A4')
    if asc==True:
        fig.data[0].marker.color = ('#F7A4A4','#FEBE8C','#B6E2A1')
    fig.update_layout(margin=dict(
            l=0,
            r=0,
            b=0,
            t=90,
            pad=4
        ))
    fig.update_traces(texttemplate='%{text:.2%}', textposition='inside')
    fig.update_layout(height=490,title=prefix+' Performing Campaigns by CTR(%)') #yaxis_range=[1.2,1.25]
    config = {
        "displayModeBar": False
    }
    st.plotly_chart(fig,config=config, theme="streamlit",use_container_width=True)    

def getChartCTRByDevice(df):
    fig = go.Figure(data=[
        go.Bar(name='IMPRESSIONS', x=df['DEVICECATEGORY'], y=df['CTR'],yaxis='y',text=df['CTR']/100)
    ],layout={
        'yaxis': {'title': 'CTR(%)','showgrid':False,'showline':False}
    })
    fig.data[0].marker.color = ('#537188','#8294C4','#BFCCB5','#DDFFBB')
    fig.update_traces(texttemplate='%{text:.2%}', textposition='inside')
    fig.update_layout(height=540,title='CTR(%) by Device Type',yaxis_range=[df['CTR'].min() - (df['CTR'].min()/50),df['CTR'].max()]) #yaxis_range=[1.2,1.25]
    st.plotly_chart(fig, theme="streamlit",use_container_width=True)

def getKPIByCampaignAds(df):
    df=df.groupby(['ORDERNAME','LINE_ITEM']).agg({
                        'IMPRESSIONS':"sum",
                        'CLICKS':"sum",
                        'SELLERRESERVEPRICE':'sum'
                        }).reset_index()
    df['CTR']=(df['CLICKS']/df['IMPRESSIONS'] )*100                     
    return df[['ORDERNAME','LINE_ITEM','IMPRESSIONS', 'CLICKS','CTR','SELLERRESERVEPRICE']].sort_values(['ORDERNAME'])

def getDollarRenderer():
    rd = JsCode('''
        function(params) { 
            return '<span>$' + parseFloat(params.value).toFixed(2) + '</span>'}
    ''') 
    return rd  

def getNbenderer():
    rd = JsCode('''
        function(params) { 
            return '<span>' + parseFloat(params.value).toLocaleString('en-US', {maximumFractionDigits:2}) + '</span>'}
    ''') 
    return rd  

def getPercentRenderer():

    rd = JsCode('''
        function(params) {return '<span>' + parseFloat(params.value).toFixed(2) + '%</span>'}
    ''') 
    return rd   

def customAggCPC():
    rd=JsCode('''
    function(params) {
                 if ((params.node.data && params.node.data.CLICKS==0) || (params.node.aggData && params.node.aggData.CLICKS==0)){
                    return 0;
                }
                if (params.node.data){
                    return params.node.data.SELLERRESERVEPRICE/params.node.data.CLICKS;
                }
                return params.node.aggData.SELLERRESERVEPRICE/params.node.aggData.CLICKS;
            }
    ''')
    return rd

def getTableCampaignPerf(df):
    ob = GridOptionsBuilder.from_dataframe(df)
    ob.configure_column('ORDERNAME', rowGroup=True,hide= True)
    ob.configure_column('LINE_ITEM', rowGroup=True,hide=True)
    ob.configure_column('IMPRESSIONS', aggFunc='sum',header_name='IMPRESSIONS',cellRenderer=getNbenderer())
    ob.configure_column('CLICKS', aggFunc='sum', header_name='CLICKS',cellRenderer=getNbenderer())
    ob.configure_column('SELLERRESERVEPRICE', aggFunc='sum',cellRenderer=getDollarRenderer(),hide=True)
    ob.configure_column('CTR', aggFunc='avg',header_name='CTR',cellRenderer= getPercentRenderer())
    ob.configure_column('CPC', valueGetter=customAggCPC(),header_name='COST PER CLICK',cellRenderer= getDollarRenderer())    
    ob.configure_grid_options(suppressAggFuncInHeader = True)
    custom_css = {
        ".ag-row-level-2 .ag-group-expanded, .ag-row-level-2 .ag-group-contracted":{
            "display":"none!important",
        },
        ".ag-watermark":{
            "display":"none!important"
        },
        ".ag-root-wrapper":{
             "margin-top":"2px",
             "border-bottom": "2px",
             "border-bottom-color": "#b9b5b5",
             "border-bottom-style": "double"
             }
        }
    gripOption=ob.build()
    gripOption["autoGroupColumnDef"]= {
    "headerName": 'CAMPAIGN - AD TYPE',
    "cellRendererParams": {
        "suppressDoubleClickExpand": True,  
        "suppressCount": True,
    },
    }
    AgGrid(df,gripOption, enable_enterprise_modules=True,fit_columns_on_grid_load=True,height=210,custom_css=custom_css,allow_unsafe_jscode=True, update_mode=GridUpdateMode.NO_UPDATE )

def getPage(sess):
    global session 
    session = sess
    advFilter=st.session_state.get('advFilter')
    rawAdvertData=getAdvertiserData(advFilter)
    rawClicksData=getClickDataByAdvertiser(advFilter)
    data = [rawAdvertData, rawClicksData]
    all = pd.concat(data)
    all['IMPRESSIONS']=all['IMPRESSIONS']*9999
    all['CLICKS']=all['CLICKS']*9999
    all['SELLERRESERVEPRICE']=round(all['SELLERRESERVEPRICE']*9999,2)
    colL,colR,colRR=st.columns([2,1,1])
    with colL:
        getChartCTRByDevice(getCTRByDevice(all))
    with colR:  
        getChartTopAds(getTopBottomAds(all,bottom=False),asc=True)  
    with colRR:
        getChartTopAds(getTopBottomAds(all,bottom=True),prefix='Bottom',asc=False)   
    getTableCampaignPerf(getKPIByCampaignAds(all))        
    