import hydralit_components as hc
import campaign, ads,whatif
from ui import setUI
import streamlit.components.v1 as components
import snowflake.connector as sf
import streamlit as st
import gc
import configparser
from PIL import Image


st.set_page_config(layout='wide',initial_sidebar_state='collapsed',)

@st.cache_resource(ttl=5000)
def getSession():
    try:
        config = configparser.ConfigParser()
        config.read("secrets.toml")
        print(dict(config.items("snow")))
        session=sf.connect(**dict(config.items("snow")))
        
    except :
        session = sf.connect(**st.secrets.snow)
    return session

menu_data = [
    {'id':'Campaigns Overview','icon':"fas fa-map-signs",'label':"Campaigns Overview"},
    {'id':'Ads Performance','icon':"fab fa-buysellads",'label':"Ads Performance"},
    {'id':'Budget Allocation','icon':"fas fa-donate",'label':"Budget Allocation"},

]

over_theme = {'txc_active':'#5d5d5d','txc_inactive': '#adadad', 'menu_background':'#f0f2f6'}

image = Image.open('summit_logo.png')


st.image(image)

page = hc.nav_bar(
    menu_definition=menu_data,
    override_theme=over_theme,
    hide_streamlit_markers=False, #will show the st hamburger as well as the navbar now!
    sticky_nav=True, #at the top or not
    sticky_mode='pinned', #jumpy or not-jumpy, but sticky or pinned
)


emp=st.empty()
gc.collect()
setUI()
emp.markdown('<p class="big-font">⏳</p>', unsafe_allow_html=True)

if page == 'Campaigns Overview':
    campaign.getPage(getSession())    
if page == 'Ads Performance':
    ads.getPage(getSession()) 
if page == "Budget Allocation":
    whatif.getPage(getSession())          
emp.empty()

