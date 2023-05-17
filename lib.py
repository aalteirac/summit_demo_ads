import configparser
from snowflake.snowpark import Session
import streamlit as st
import pandas as pd

CTR_FACTOR=0.5
GLOBAL_SCALE_FACTOR=9999

@st.cache_resource(ttl=5000)
def getSession():
    print(dict(st.secrets.snow))
    config = configparser.ConfigParser()
    config.read("secrets.toml")
    session = Session.builder.configs(dict(st.secrets.snow)).create() 
    return session

@st.cache_data(show_spinner=False,ttl=5000)
def getDistinctAdvertisers():
    df=getSession().sql(f'''
    select distinct ADVERTISER_NAME from SUMMIT_JIM_DB.RAW_SC."INDUSTRIES" ORDER BY ADVERTISER_NAME;
    ''').collect()
    return df

@st.cache_data(show_spinner=False,ttl=5000)
def getAdvertiserData(adv):
    df=getSession().sql(f'''
    select *,
        1 as IMPRESSIONS_INT,CAST(1 AS DECIMAL(7,2) )  as IMPRESSIONS,
        CAST(1 AS DECIMAL(7,2) ) as IMPDEC,
        to_date(TO_VARCHAR(to_date(to_timestamp(time_ts/1000000)), 'yyyy-MM-01')) as MONTH,
        to_date(to_timestamp(time_ts/1000000)) as DATE_IMP 
        FROM SUMMIT_JIM_DB.RAW_SC.IMPRESSIONS AS im JOIN SUMMIT_JIM_DB.RAW_SC.INDUSTRIES AS i
        USING (advertiser_name)
    WHERE im.ADVERTISER_NAME='{adv}';
    ''').collect()
    return pd.DataFrame(df)

@st.cache_data(show_spinner=False,ttl=5000)
def getClickDataByAdvertiser(adv):
    df=getSession().sql(f'''
    select *, {CTR_FACTOR} as CLICKS,
    to_date(TO_VARCHAR(to_date(to_timestamp(time_ts/1000000)), 'yyyy-MM-01')) as MONTH,
    to_date(to_timestamp(time_ts/1000000)) as DATE_IMP from SUMMIT_JIM_DB.RAW_SC."CLICKS" 
    WHERE ADVERTISER_NAME='{adv}';
    ''').collect()
    return pd.DataFrame(df)         




def getMappingAdvertiser():
    df=getSession().sql(f'''
    select * from SUMMIT_JIM_DB.RAW_SC.MAPPING_TB;
    ''').collect()
    return pd.DataFrame(df)

def getAllAdvertiserData(adv):
    df=getSession().sql(f'''
    select * from SUMMIT_JIM_DB.RAW_SC."GAM_VIZ_CLICKS_UPDATED_DATA";
    ''').collect()
    return pd.DataFrame(df)