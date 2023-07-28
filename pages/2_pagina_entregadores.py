#BIBLIOTECAS
import pandas as pd
import plotly.express as px
import folium

#BIBLIOTECAS IMPORTADAS
from datetime import datetime
from haversine import haversine
import streamlit as st
from PIL import Image
from streamlit_folium import folium_static

#st.set_page_config (page_title="Visão Entregadores", layout='wide')


# ############################################################################################################################
# FUNÇÕES
# ############################################################################################################################

def clean_code (df):
    df['ID'] = df['ID'].str.strip()
    df['Delivery_person_ID'] = df['Delivery_person_ID'].str.strip()
    df['Road_traffic_density'] = df['Road_traffic_density'].str.strip()
    df['Type_of_order'] = df['Type_of_order'].str.strip()
    df['Type_of_vehicle'] = df['Type_of_vehicle'].str.strip()
    df['Festival'] = df['Festival'].str.strip()
    df['City'] = df['City'].str.strip()
    
    linhas_uteis = (df['Delivery_person_Age'] != 'NaN ') & (df['multiple_deliveries'] != 'NaN ') & (df['Road_traffic_density'] != 'NaN') & (df['City'] != 'NaN') & (df['Time_taken(min)'] != 'NaN ')
    df = df.loc[linhas_uteis,:]
    df = df.reset_index(drop=True)
    
    df['Delivery_person_Age'] = df['Delivery_person_Age'].astype(int)
    df['Delivery_person_Ratings'] = df['Delivery_person_Ratings'].astype(float)
    df['Order_Date'] = pd.to_datetime(df['Order_Date'], format = '%d-%m-%Y')
    
    df['Time_taken(min)'] = df['Time_taken(min)'].apply( lambda x: x.split ('(min) ')[1] )
    df['Time_taken(min)'] = df['Time_taken(min)'].astype(int)

    return df

# ############################################################################################################################
# INÍCIO DA ESTRUTURA LÓGICA DO CÓDIGO
# ############################################################################################################################

# DATAFRAME
dframe = pd.read_csv('train.csv')

# LIMPANDO OS DADOS

df = clean_code(dframe)

# ############################################################################################################################
# BARRA LATERAL
# ############################################################################################################################

st.header('Visão Entregadores')

image_pasta = 'icone.png'
image = Image.open(image_pasta)
st.sidebar.image(image, width=300)

st.sidebar.markdown('### Cury Company')
st.sidebar.markdown('''---''')

st.sidebar.markdown('## Selecione uma data limite:')

date_slider = st.sidebar.slider(
    'Até qual valor?',
    value=datetime(2022,3,19 ),
    min_value=datetime(2022, 2, 11),
    max_value=datetime(2022, 4, 6), 
    format='DD-MM-YYY')

st.sidebar.markdown('''---''')

traffic_options = st.sidebar.multiselect(
    'Quais as condições do trânsito',
    ['Low', 'Medium', 'High', 'Jam'],
    default=['Low', 'Medium', 'High', 'Jam'])

st.sidebar.markdown('''---''')
st.sidebar.markdown('### Powered by Diogo Marques')

# Filtro de Datas
linhas_selecionadas = df['Order_Date'] < date_slider
df = df.loc[linhas_selecionadas, :]

# Filtro de trânsito:
linhas = df['Road_traffic_density'].isin(traffic_options)
df = df.loc[linhas, :]


#############################################################################################################################
#LAYOUT NO STREAMLIT
#############################################################################################################################

tab1, tab2, tab3 = st.tabs (['Visão Gerencial', ' ', ' '])

with tab1:
    with st.container():
        st.header('Overal Metrics')
       
        col1, col2, col3, col4 = st.columns(4, gap='large')
        
        with col1:
            maior = df['Delivery_person_Age'].max()
            col1.metric('Maior Idade ', maior)

        with col2:
            menor = df['Delivery_person_Age'].min()
            col2.metric ('Menor Idade', menor)
        
        with col3:
            melhor = df['Vehicle_condition'].max()
            col3.metric('Melhor condição', melhor)
        
        with col4:
            pior = df['Vehicle_condition'].min()
            col4.metric('Pior condição', pior)
            
    st.markdown ('''---''')

    with st.container():
        st.header('Avaliações')

        col1, col2 = st.columns(2)

        with col1:
            
            st.subheader('Avaliação média por entregador')
            media = (df[['Delivery_person_ID', 'Delivery_person_Ratings']]
                     .groupby('Delivery_person_ID')
                     .mean()
                     .reset_index())
            st.dataframe(media)

        with col2:

            st.subheader('Avaliação média por trânsito')
            df_mean_std = (df[['Road_traffic_density', 'Delivery_person_Ratings']]
                           .groupby('Road_traffic_density')
                           .agg( {'Delivery_person_Ratings': ['mean', 'std'] } ))
            df_mean_std.columns = ['media', 'desvio']
            df_mean_std.reset_index()
            st.dataframe(df_mean_std)
            
            st.subheader('Avaliação média por clima')
            df_mean_std = (df[['Weatherconditions', 'Delivery_person_Ratings']]
                           .groupby('Weatherconditions')
                           .agg( {'Delivery_person_Ratings': ['mean', 'std'] } ))
            df_mean_std.columns = ['media', 'desvio']
            df_mean_std.reset_index()
            st.dataframe(df_mean_std)

    with st.container():
        st.header('Velocidades de Entrega')

        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader('TOP entregadores mais rápidos')
            top_rapidos = (df[['City', 'Delivery_person_ID','Time_taken(min)']]
            .groupby(['City', 'Time_taken(min)'])
            .min()
            .sort_values(['City','Time_taken(min)'])
            .reset_index())
            st.dataframe(top_rapidos)
        with col2:
            st.subheader('TOP entregadores mais lentos')
