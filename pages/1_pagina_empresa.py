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

#st.set_page_config (page_title="Visão Empresa", layout='wide')

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


def order_metric (df):
    aux = df[['ID', 'Order_Date']].groupby('Order_Date').count().reset_index()
    # Gráfico de linhas
    graf = px.bar(aux, x = 'Order_Date', y = 'ID')

    return graf

def traffic_order_share(df):
    aux = df[['ID', 'Road_traffic_density']].groupby('Road_traffic_density').count().reset_index()

    #Calculando em porcentagem:
    porcentagem = aux['ID']/aux['ID'].sum()
    
    #Criando a coluna de porcentagem:
    aux['Entregas_Porcentagem'] = porcentagem
    
    graf = px.pie(aux, values = 'Entregas_Porcentagem', names = 'Road_traffic_density')

    return graf

def traffic_order_city (df):
    aux = df[['ID', 'City', 'Road_traffic_density']].groupby(['City', 'Road_traffic_density']).count().reset_index()
    graf = px.scatter( aux, x = 'City', y = 'Road_traffic_density', size = 'ID' )

    return graf

def order_by_week (df):
    df['Week_Date'] = df['Order_Date'].dt.strftime( '%U' )
    aux = df[['ID', 'Week_Date']].groupby('Week_Date').count().reset_index()
    graf = px.line(aux, x = 'Week_Date', y = 'ID')

    return graf
    
def order_deliver (df):
    # A quantidade de pedidos por entregador por semana.
    ped_semana = df[['ID', 'Week_Date']].groupby('Week_Date').count().reset_index()
    ped_entreg = df[['Delivery_person_ID', 'Week_Date']].groupby('Week_Date').nunique().reset_index()  
    aux = pd.merge(ped_semana, ped_entreg, how='inner')
    aux['Order_deliver'] = aux['ID']/aux['Delivery_person_ID'] 
    graf = px.line(aux, x ='Week_Date', y = 'Order_deliver')

    return graf

def country_map(df):
    localiza = (df[['City','Delivery_location_latitude','Delivery_location_longitude','Road_traffic_density']]
                .groupby(['City','Road_traffic_density'])
                .median()
                .reset_index())
    map = folium.Map()
    
    for index, location in localiza.iterrows():
        folium.Marker ([ location['Delivery_location_latitude'], location ['Delivery_location_longitude'] ]).add_to(map)
        
    folium_static( map, width=900, height=600)

    return None

    
# ############################################################################################################################
# INÍCIO DA ESTRUTURA LÓGICA DO CÓDIGO
# ############################################################################################################################
    
# DATAFRAME
dframe = pd.read_csv('train.csv')

# LIMPANDO OS DADOS:
df = clean_code(dframe)

    
# ############################################################################################################################
# BARRA LATERAL
# ############################################################################################################################

st.header('Visão da Empresa')

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

tab1, tab2, tab3 = st.tabs (['Visão Gerencial', 'Visão Tática', 'Visão Geográfica'])

with tab1:
    with st.container():
        
        st.markdown('# Orders by Day')
        fig = order_metric(df)
        st.plotly_chart(fig, use_container_width=True)
        
    with st.container():
        
        # Criando colunas:
        col1, col2 = st.columns (2)
        
        with col1:
            st.header('Traffic Order Share')
            graf = traffic_order_share(df)
            st.plotly_chart(graf, use_container_width=True)
                   
        with col2:
            
            #Comparação do volume de pedidos por cidade e tipo de tráfego.
            st.header('Traffic Order City')
            graf = traffic_order_city(df)
            st.plotly_chart(graf, use_container_width=True)
            
    
with tab2:
    
    with st.container():
        
        st.header('Order by Week')
        graf = order_by_week(df)
        st.plotly_chart(graf, use_container_width=True)
        
    with st.container():
        st.header('Order Share by Week')
        graf = order_deliver(df)
        st.plotly_chart(graf, use_container_width=True)   

with tab3:
    
    # A localização central de cada cidade por tipo de tráfego
    st.header('Country Map')
    country_map(df)

