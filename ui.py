import streamlit as st
import streamlit.components.v1 as components

def setUI():
    hvar='''
        <script>
              

            setTimeout(()=>{
                toHide=window.parent.document.querySelectorAll('iframe[height="0"]')
                for (const iframe of toHide) {
                    if(iframe.hasAttribute("srcdoc"))
                        iframe.parentElement.style.display="none"
                }
            },1000)

            var my_style= window.parent.document.createElement('style');
            my_style.innerHTML=`
                footer{
                    display:none;
                }
                .stApp header{
                display:none;
                }
                @keyframes append-animate {
                    from {
                        transform: scale(0);
                        opacity: 0;
                    }
                    to {
                        transform: scale(1);
                        opacity: 1;	
                    }
                }
                @keyframes rotating {
                    from {
                        transform: rotate(0deg);
                    }
                    to {
                        transform: rotate(360deg);
                    }
                }
                .block-container:has(.big-font){
                    /* overflow:hidden; */
                } 
                div[data-testid="stVerticalBlock"] {
                    gap:0rem;
                }
                .stMarkdown div:has(.big-font){
                    position: absolute;
                    z-index: 5;
                    width: 100%;
                    height: 4000px;
                    background-color: white;
                    opacity: 0.8;
                }
                .stMarkdown {
                    z-index:1000;
                }
                .stMarkdown p {
                    animation: rotating 2s linear infinite;
                }
                iframeOUT{
                    transform-origin: 50% 0;
	                animation: append-animate 1.4s linear;
                }
                .big-font {
                    font-size:35vw !important;
                    color:"darkgrey";
                    opacity: 0.1;
                    text-align:center;
                }
                .streamlit-expanderHeader p{
                    font-size: x-large;
                }
                .main .block-container{
                    max-width: unset;
                    padding-left:1em;
                    padding-right: 1em;
                    padding-top: 0em;
                    padding-bottom: 1em;
                    }
                [data-testid="stMetricDelta"] > div:nth-child(2){
                    justify-content: center;
                }
                        `;
                window.parent.document.head.appendChild(my_style);       
        </script>
        '''
    components.html(hvar, height=0, width=0)
