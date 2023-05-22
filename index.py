import hydralit_components as hc
import campaign, ads,whatif,bench
from ui import setUI
import streamlit.components.v1 as components
import streamlit as st
import gc
import lib as lib

from PIL import Image


st.set_page_config(layout='wide',initial_sidebar_state='collapsed',)



menu_data = [
    {'id':'Campaigns Overview','icon':"fas fa-map-signs",'label':"Campaigns Overview"},
    {'id':'Ads Performance','icon':"fab fa-buysellads",'label':"Ads Performance"},
    {'id':'Budget Allocation','icon':"fas fa-donate",'label':"Budget Allocation"},
    {'id':'Benchmark','icon':"fab fa-battle-net",'label':"Benchmark"}

]

over_theme = {'txc_active':'#5d5d5d','txc_inactive': '#adadad', 'menu_background':'#f0f2f6'}

image = Image.open('summit_logo.png')

col1,col2=st.columns([1,5])
col1.image(image)
advFilter=col2.selectbox("ADVERTISER:", lib.getDistinctAdvertisers(),index=0,key='advFilter')

page = hc.nav_bar(
    menu_definition=menu_data,
    override_theme=over_theme,
    hide_streamlit_markers=False, 
    sticky_nav=True, 
    sticky_mode='pinned', 
)


emp=st.empty()
gc.collect()
setUI()
# emp.markdown('<p class="big-font">⏳</p>', unsafe_allow_html=True)

if page == 'Campaigns Overview':
    campaign.getPage(lib.getSession())    
if page == 'Ads Performance':
    ads.getPage(lib.getSession()) 
if page == "Budget Allocation":
    whatif.getPage(lib.getSession()) 
if page == "Benchmark":
    bench.getPage(lib.getSession())           
emp.empty()

# TODO
# DONE Color coding in the table based on treshold fro CTR
# DONE Suppress 0 clicks line on table ads
# DONE Select current advertiser industry by default
# Show possible countries for selected Advertiser in benchmark