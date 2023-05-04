from streamlit_option_menu import option_menu
import campaign, ads,whatif
from ui import setUI
import streamlit.components.v1 as components
import snowflake.connector as sf
import streamlit as st
import gc
import configparser




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

page = option_menu("Adverity-Piano-Snowflake-MarketPlace", ["Campaigns Overview","Ads Performance","Budget Allocation"],
                   icons=['binoculars-fill', "list-task",'question-circle'],
                   menu_icon="window", default_index=0, orientation="horizontal",
                   styles={
                       "container": {"max-width": "100%!important","--primary-color":"#4a4d4f","--text-color":"#30333f"},
                       "nav-link": {"font-weight": "600"},
                       "menu-title" :{"font-weight": "600"},
                       "nav-link": {"font-size": "1.1vw","font-weight": "600"}
                       # "margin":"0px", "--hover-color": "#eee"}
                       # "container": {"padding": "0!important", "background-color": "#fafafa"}, "icon": {"color":
                       # "orange", "font-size": "25px"}, "nav-link": {"font-size": "25px", "text-align": "left",
                       # "margin":"0px", "--hover-color": "#eee"}, "nav-link-selected": {"background-color": "green"},
                   }
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


# menu_data = [
#     {'id':'Home','icon':"🐙",'label':"Home"},
#     {'id':'Campaigns','icon': "💀", 'label':"Campaigns"},
# ]
# over_theme = {'txc_inactive': '#FFFFFF'}
# menu_id = hc.nav_bar(
#     menu_definition=menu_data,
#     override_theme=over_theme,
#     hide_streamlit_markers=False, #will show the st hamburger as well as the navbar now!
#     sticky_nav=True, #at the top or not
#     sticky_mode='pinned', #jumpy or not-jumpy, but sticky or pinned
# )
# if menu_id=='Home':
#     main.getPage(getSession())
# if menu_id=='Campaigns':
#     campaign.getPage(getSession())     