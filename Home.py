import streamlit as st
from PIL import Image

st.set_page_config(page_title="Home", layout='wide')

image = Image.open('icone.png')
st.sidebar.image (image, width=120)

st.sidebar.markdown('### Cury Company')
st.sidebar.markdown('''---''')

st.write ("# Curry Company Growth Dashboard")