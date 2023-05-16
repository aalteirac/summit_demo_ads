import configparser
from snowflake.snowpark import Session
import streamlit as st



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
    select distinct ADVERTISER_NAME from SUMMIT_JIM_DB.RAW_SC."CLICKS";
    ''').collect()
    return df