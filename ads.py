import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from st_aggrid import AgGrid, GridOptionsBuilder, JsCode,GridUpdateMode



session=None

@st.cache_data(show_spinner=False,ttl=5000)
def getRawCampaign():
    queryAll=f'''
    SELECT *,to_date(TO_VARCHAR(DAY, 'yyyy-MM-01')) as MONTH,coalesce((clicks/NULLIF(impressions,0))*100,0) as CTR,coalesce(((clicks + likes + shares)/NULLIF(impressions,0))*100,0) as ER from adverity.adverity."Marketing_Data";
    '''
    df = pd.read_sql(queryAll, session)
    return df

    return df.groupby(['MONTH']).agg({'IMPRESSIONS':'sum',
                                      'CLICKS':'sum',
                                      'CTR':"mean"}).reset_index()

def getCTRByGenderByAge(df):
    return df.groupby(['GENDER','AGE_RANGE']).agg({'CTR':'mean'}).reset_index()

def getKPIByCampaignAds(df):
    df=df.groupby(['COUNTRY_NAME', 'CAMPAIGN','AD_TYPE', 'AD_NAME']).agg({
                        'VIDEO_COMPLETIONS':'sum',
                        'VIEWS':'sum',
                        'COSTS':'sum',
                        'CTR':"mean",
                        'IMPRESSIONS':"sum",
                        'CLICKS':"sum"
                        }).reset_index()
    df['CPVMANUAL']=0
    df['CPCVMANUAL']=0
    return df[['CAMPAIGN','AD_TYPE','AD_NAME','IMPRESSIONS', 'CLICKS','CTR','CPVMANUAL','CPCVMANUAL','COSTS','VIDEO_COMPLETIONS','VIEWS']].sort_values(['CAMPAIGN'])

def getCTRByDevice(df):
    return df.groupby(['DEVICE_TYPE']).agg({'CTR':'mean'}).reset_index()

def getTopBottomAds(df,bottom=False,n=3):
    return df.groupby(['AD_NAME']).agg({'ER':'mean'}).sort_values(by=['ER'],ascending=bottom).reset_index().head(n)

def getPercentRenderer():

    rd = JsCode('''
        function(params) {return '<span>' + parseFloat(params.value).toFixed(2) + '%</span>'}
    ''') 
    return rd   

def getChartCTRByDevice(df):
    fig = go.Figure(data=[
        go.Bar(name='IMPRESSIONS', x=df['DEVICE_TYPE'], y=df['CTR'],yaxis='y',text=df['CTR']/100)
    ],layout={
        'yaxis': {'title': 'CTR(%)','showgrid':False,'showline':False}
    })
    fig.data[0].marker.color = ('blue','green','darkgrey')
    fig.update_traces(texttemplate='%{text:.2%}', textposition='inside')
    fig.update_layout(margin=dict(
            l=0,
            r=0,
            b=0,
            t=30,
            pad=4
        ))
    fig.update_layout(height=490,title='CTR(%) by Device Type',yaxis_range=[df['CTR'].min() - (df['CTR'].min()/50),df['CTR'].max()]) #yaxis_range=[1.2,1.25]
    st.plotly_chart(fig, theme="streamlit",use_container_width=True)

def getChartTopAds(df,asc=True,prefix='Top'):
    df=df.sort_values(['ER'], ascending=[asc])
    fig = go.Figure(data=[
        go.Bar(name='IMPRESSIONS', y=df['AD_NAME'], x=df['ER'],text=df['ER']/100, orientation='h')
    ])
    fig.update_xaxes(visible=False, showticklabels=False)
    fig.data[0].marker.color = ('blue','green','darkgrey')
    fig.update_layout(margin=dict(
            l=0,
            r=0,
            b=0,
            t=30,
            pad=4
        ))
    fig.update_traces(texttemplate='%{text:.2%}', textposition='inside')
    fig.update_layout(height=490,title=prefix+' Performing Ads by ER(%)',xaxis_range=[df['ER'].min() - (df['ER'].min()/50),df['ER'].max()]) #yaxis_range=[1.2,1.25]
    config = {
        "displayModeBar": False
    }
    st.plotly_chart(fig,config=config, theme="streamlit",use_container_width=True)    

def genSankey(df,cat_cols=[],value_cols='',title='Sankey Diagram'):
    colorPalette = ['red','#646464','#306998','#FFE873','#FFD43B']
    labelList = []
    colorNumList = []
    for catCol in cat_cols:
        labelListTemp =  list(set(df[catCol].values))
        colorNumList.append(len(labelListTemp))
        labelList = labelList + labelListTemp
        
    labelList = list(dict.fromkeys(labelList))
    
    colorList = []
    for idx, colorNum in enumerate(colorNumList):
        colorList = colorList + [colorPalette[idx]]*colorNum
        
    for i in range(len(cat_cols)-1):
        if i==0:
            sourceTargetDf = df[[cat_cols[i],cat_cols[i+1],value_cols]]
            sourceTargetDf.columns = ['source','target','count']
        else:
            tempDf = df[[cat_cols[i],cat_cols[i+1],value_cols]]
            tempDf.columns = ['source','target','count']
            sourceTargetDf = pd.concat([sourceTargetDf,tempDf])
        sourceTargetDf = sourceTargetDf.groupby(['source','target']).agg({'count':'sum'}).reset_index()
        
    sourceTargetDf['sourceID'] = sourceTargetDf['source'].apply(lambda x: labelList.index(x))
    sourceTargetDf['targetID'] = sourceTargetDf['target'].apply(lambda x: labelList.index(x))
    #OVERRIDE COLOR AS I DON'T HAVE TIME :-)
    colorList=['darkgrey','#7ce670','blue','#ebf0a8','#e3ed58','#cad622','#acd622','#7cd622','#22d69d']
    data = dict(
        type='sankey',
        node = dict(
          pad = 15,
          thickness = 20,
          line = dict(
            color = "black",
            width = 0.5
          ),
          label = labelList,
          color = colorList
        ),
        link = dict(
          source = sourceTargetDf['sourceID'],
          target = sourceTargetDf['targetID'],
          value = sourceTargetDf['count'],
        )
      )
    
    layout =  dict(
        height= 470,
        title = title,
        font = dict(
          size = 10
        ),
        margin=dict(
            l=0,
            r=0,
            b=0,
            t=30,
            pad=4
        )
    )
       
    fig = dict(data=[data], layout=layout)
    st.plotly_chart(fig, theme="streamlit",use_container_width=True)

def getEuroRendererCPV():
    rd = JsCode('''
        function(params) { 
            return '<span>' + parseFloat(params.value).toFixed(2) + '€</span>'}
    ''') 
    return rd  

def customAggCPV():
    rd=JsCode('''
    function(params) {
                if (params.node.data){
                    return params.node.data.COSTS/params.node.data.VIEWS;
                }
                return params.node.aggData.COSTS/params.node.aggData.VIEWS;
            }
    ''')
    return rd

def customAggCPCV():
    rd=JsCode('''
    function(params) {
                if (params.node.data){
                    return params.node.data.COSTS/params.node.data.VIDEO_COMPLETIONS;
                }
                return params.node.aggData.COSTS/params.node.aggData.VIDEO_COMPLETIONS;
            }
    ''')
    return rd

def getTableCampaignPerf(df):
    ob = GridOptionsBuilder.from_dataframe(df)
    ob.configure_column('CAMPAIGN', rowGroup=True,hide= True)
    ob.configure_column('AD_TYPE', rowGroup=True,hide= True)
    ob.configure_column('AD_NAME', rowGroup=True,hide= True)
    ob.configure_column('IMPRESSIONS', aggFunc='sum',header_name='IMPRESSIONS')
    ob.configure_column('CLICKS', aggFunc='sum', header_name='CLICKS')
    ob.configure_column('COSTS', aggFunc='sum', hide=True)
    ob.configure_column('VIEWS', aggFunc='sum', hide=True)
    ob.configure_column('VIDEO_COMPLETIONS', aggFunc='sum', hide=True)
    ob.configure_column('CTR', aggFunc='avg',header_name='CTR',cellRenderer= getPercentRenderer())
    ob.configure_column('CPVMANUAL', valueGetter=customAggCPV(),header_name='COST PER VIDEO VIEW',cellRenderer= getEuroRendererCPV())
    ob.configure_column('CPCVMANUAL',valueGetter=customAggCPCV(),header_name='COST PER VIDEO COMPLETED',cellRenderer= getEuroRendererCPV())
    
    ob.configure_grid_options(suppressAggFuncInHeader = True)
    custom_css = {
        ".ag-row-level-2 .ag-group-expanded, .ag-row-level-2 .ag-group-contracted":{
            "display":"none!important",
        },
        ".ag-watermark":{
            "display":"none!important"
        },
        ".ag-root-wrapper":{
             "margin-top":"28px",
             "border-bottom": "2px",
             "border-bottom-color": "#b9b5b5",
             "border-bottom-style": "double"
             }
        }
    gripOption=ob.build()
    gripOption["autoGroupColumnDef"]= {
    "headerName": 'CAMPAIGN/AD_TYPE',
    "cellRendererParams": {
        "suppressDoubleClickExpand": True,  
        "suppressCount": True,
    },
    }
    AgGrid(df,gripOption, enable_enterprise_modules=True,fit_columns_on_grid_load=True,height=342,custom_css=custom_css,allow_unsafe_jscode=True, update_mode=GridUpdateMode.NO_UPDATE )

def getPage(sess):
    global session 
    session = sess
    # st.subheader("Ads Performance Deep Dive")
    colL,colR,colRR=st.columns([2,1,1])
    with colL:
        getChartCTRByDevice(getCTRByDevice(getRawCampaign()))
    with colR:  
        getChartTopAds(getTopBottomAds(getRawCampaign()))   
    with colRR:
        getChartTopAds(getTopBottomAds(getRawCampaign(),bottom=True),asc=False,prefix='Bottom')   
    getTableCampaignPerf(getKPIByCampaignAds(getRawCampaign()))        
    