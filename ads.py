import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from st_aggrid import AgGrid, GridOptionsBuilder, JsCode,GridUpdateMode
from lib import GLOBAL_SCALE_FACTOR, getAdvertiserData, getClickDataByAdvertiser

session=None


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

def getColorRenderer():
    rd = JsCode('''
        function(params) { 
            var color='red';
            if(params.value<=0.15)
                color="green";
            if(params.value>0.15 && params.value<0.20)
                color="#ffc700";  
            return '<span style="color:'+color + '">' + parseFloat(params.value).toFixed(2) + '€</span>'}
    ''') 
    return rd  

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
            var color='red';
            if(params.value<=0.11)
                color="green";
            if(params.value>0.11 && params.value<0.14)
                color="#ffc700";  
            return '<span style="color:'+color + '">$' + parseFloat(params.value).toFixed(2) + '</span>'}
    ''') 
    return rd  

def getNbRenderer(prefix="",suffix="", black='yes',arr=0):
    rd = f'''
    class TotalValueRenderer {{
        init(params) {{
            var black="{black}";
            var color='red';
            if(params.value<=0.11)
                color="green";
            if(params.value>0.11 && params.value<0.14)
                color="#ffc700";  
            if (black=="yes"){{
                color="black"
            }}    
            this.eGui = document.createElement('div');
            this.eGui.innerHTML = `
                <span>
                    <span style="color:${{color}}" class="my-value"></span>
                </span>`;

            this.eValue = this.eGui.querySelector('.my-value');
            this.cellValue = this.getValueToDisplay(params);
            this.eValue.innerHTML = this.cellValue;
        }}

        getGui() {{
            return this.eGui;
        }}

        refresh(params) {{
            this.cellValue = this.getValueToDisplay(params);
            this.eValue.innerHTML = this.cellValue;
            return true;
        }}
        destroy() {{
            if (this.eButton) {{
                this.eButton.removeEventListener('click', this.eventListener);
            }}
        }}

        getValueToDisplay(params) {{
            var v=parseFloat(params.value).toFixed({arr});
            if({arr}>0){{
                return "{prefix}" + parseFloat(v).toFixed({arr}).toLocaleString('en-US', {{maximumFractionDigits:2}})+"{suffix}"
            }}
            return "{prefix}" + parseFloat(v).toLocaleString('en-US', {{maximumFractionDigits:2}})+"{suffix}"
        }}
    }}'''
    print(rd)
    return JsCode(rd)  

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
    df=df[df['CTR']>0]
    ob = GridOptionsBuilder.from_dataframe(df)
    ob.configure_column('ORDERNAME', rowGroup=True,hide= True)
    ob.configure_column('LINE_ITEM', rowGroup=True,hide=True)
    ob.configure_column('IMPRESSIONS', aggFunc='sum',header_name='IMPRESSIONS',cellRenderer=getNbRenderer('',''))
    ob.configure_column('CLICKS', aggFunc='sum', header_name='CLICKS',cellRenderer=getNbRenderer('',''))
    ob.configure_column('SELLERRESERVEPRICE', aggFunc='sum',hide=True)
    ob.configure_column('CTR', aggFunc='avg',header_name='CTR',cellRenderer=getNbRenderer('','%',arr=2))
    ob.configure_column('CPC', valueGetter=customAggCPC(),header_name='COST PER CLICK',cellRenderer= getNbRenderer(black='no',prefix='$',arr=3))    
    ob.configure_grid_options(suppressAggFuncInHeader = True)
    custom_css = {
        '.ag-header-cell-label': {
            "justify-content": "center",
            'text-align': 'center!important'
        },
        '.ag-cell-value:not([col-id="ag-Grid-AutoColumn"])' :{
            'text-align': 'center!important'
        },
        ".ag-row-level-1 .ag-group-expanded, .ag-row-level-1 .ag-group-contracted":{
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
    all['IMPRESSIONS']=all['IMPRESSIONS']*GLOBAL_SCALE_FACTOR
    all['CLICKS']=all['CLICKS']*GLOBAL_SCALE_FACTOR
    all['SELLERRESERVEPRICE']=round(all['SELLERRESERVEPRICE']*GLOBAL_SCALE_FACTOR,2)
    colL,colR,colRR=st.columns([2,1,1])
    with colL:
        getChartCTRByDevice(getCTRByDevice(all))
    with colR:  
        getChartTopAds(getTopBottomAds(all,bottom=False),asc=True)  
    with colRR:
        getChartTopAds(getTopBottomAds(all,bottom=True),prefix='Bottom',asc=False)   
    getTableCampaignPerf(getKPIByCampaignAds(all))        
    