#Libraries
import pandas as pd
import plotly.express as px
from haversine import haversine
import plotly.graph_objects as go
import streamlit as st
from PIL import Image
import folium
from streamlit_folium import folium_static

st.set_page_config(page_title = 'Visão Empresa', layout = 'wide')

#____________________________________________________________

#Import do dataset
#_____________________________________________________________
df1 = pd.read_csv('dataset/train.csv')

#C:\Users\Admin\Documents\repos\ftc-analisando-dados-python\

# ____________________________

# Funções

#_____________________________
def Clean_Code(df1):
    
    ''' Função criada para realizar limpezas e transformações nas colunas de dados do Dataframe
    
            Tipos de limpeza:
            1. Remoção dos dados NaN
            2. Mudança do tipo da coluna de dados
            3. Formatação da coluna de datas
            4. Limpeza da coluna de tempo
            
            Input: DataFrame
            Output: DataFrame
    
    '''
    
    df1 = df1.loc[(df1['Delivery_person_Age'] != 'NaN ')]
    # Conversao de texto/categoria/string para numeros inteiros
    df1['Delivery_person_Age'] = df1['Delivery_person_Age'].astype( int )

    # Conversao de texto/categoria/strings para numeros decimais
    df1['Delivery_person_Ratings'] = df1['Delivery_person_Ratings'].astype( float )

    # Conversao de texto para data
    df1['Order_Date'] = pd.to_datetime( df1['Order_Date'], format='%d-%m-%Y' )

    # Remove as linhas da culuna multiple_deliveries que tenham o 
    # conteudo igual a 'NaN '
    df1 = df1.loc[(df1['multiple_deliveries'] != 'NaN ')]

    df1['multiple_deliveries'] = df1['multiple_deliveries'].astype( int )

    #Alterando o conteudo da coluna Time_taken(min)

    df1['Time_taken(min)'] = list(map(lambda x: x.replace("(min) ", ""), df1['Time_taken(min)']))

    df1['Time_taken(min)'] = df1['Time_taken(min)'].astype(int)

    #Retirando os valores NaN das colunas Road_traffic_density e City

    df1 = df1.loc[(df1['Road_traffic_density'] != 'NaN ')] 

    df1 = df1.loc[(df1['City'] != 'NaN ')] 

    #Retirando o espaço da coluna Road_traffic_density

    df1['Road_traffic_density'] = list(map(lambda x: x.replace(" ", ""),df1['Road_traffic_density']))

    return df1

def order_metrics(df1): 
    '''
        Função que retorna uma figura com a quantidade de entregas feitas por dia de entrega
    '''
    
    df_aux = pd.DataFrame(df1.groupby(by = ['Order_Date']).count().reset_index()[['Order_Date', 'Delivery_person_ID']])
    fig = px.bar(df_aux, x = 'Order_Date', y = 'Delivery_person_ID')
    return fig

def traffic_order_share(df1):
    
    ''''
        Função que retorna a porcentagem de entregas distribuidas entre os tipos de tráfego    
    '''
    df_aux = pd.DataFrame(df1.loc[(df1['Road_traffic_density'] != 'NaN ' )].groupby(by =['Road_traffic_density']
     ).count().reset_index()[['Road_traffic_density', 'Delivery_person_ID']])
    
    df_aux['Porc_Road_Traffic_Density']= round(100 *( df_aux['Delivery_person_ID'] / df_aux['Delivery_person_ID'].sum()),2)     
    
    df_aux['Porc_Road_Traffic_Density'] = list(map(lambda x: str(x) + " %", df_aux['Porc_Road_Traffic_Density']))
    
    fig = px.pie(df_aux, values = 'Delivery_person_ID', names = 'Road_traffic_density')

    return fig        

def traffic_order_city(df1):
    
    '''
        Função que distribui as quantidades de entregas entre os tipos de 
        tráfego e os tipos de cidade
    
    '''
    df_aux = pd.DataFrame(df1.groupby(by = ['City', 'Road_traffic_density']).count
     ().reset_index()[['City', 'Road_traffic_density', 'Delivery_person_ID']])

    df_aux = df_aux.loc[(df_aux['City'] != 'NaN ')]

    df_aux = df_aux.loc[(df_aux['Road_traffic_density'] != 'NaN ')]

    fig = px.scatter(df_aux, x = 'City', y = 'Road_traffic_density', size = 'Delivery_person_ID', color = 'City')
               
    return fig  


def order_by_week(df1):
    
    '''
        Função que distribui a quantidade de entregas nas diferentes semanas do ano
    '''
    df1['Week_of_the_year'] = df1['Order_Date'].dt.strftime('%U')

    df_aux = pd.DataFrame(df1.groupby(by = ['Week_of_the_year']).count().reset_index()[['Week_of_the_year','Delivery_person_ID']])

    fig = px.line(df_aux, x = 'Week_of_the_year', y = 'Delivery_person_ID')

    return fig

def order_share_by_week(df1):
    '''
        Função que distribui a quantidade de entregadores unicos nas diferentes semanas do ano
    '''
    df_aux01 = df1.loc[:, ['ID','Week_of_the_year']].groupby(by = ['Week_of_the_year']).count().reset_index()

    df_aux02 = df1.loc[:, ['Delivery_person_ID', 'Week_of_the_year']].groupby(by = ['Week_of_the_year']).nunique().reset_index()

    df_aux = pd.merge(df_aux01, df_aux02, how = 'inner', on = 'Week_of_the_year')

    df_aux['order_by_deliver'] = df_aux['ID']/ df_aux['Delivery_person_ID']

    fig = px.line(df_aux, x = 'Week_of_the_year', y = 'order_by_deliver')

    return fig


def country_maps(df1):
    '''
    Função que desenha o mapa
    
    '''
    
    df_aux = df1.loc[:, ['City','Road_traffic_density','Delivery_location_latitude','Delivery_location_longitude']].groupby(by = 
        ['City','Road_traffic_density']).median().reset_index()

    df_aux = df_aux.loc[(df_aux['City'] != 'NaN ')]

    df_aux = df_aux.loc[(df_aux['Road_traffic_density'] != 'NaN ')]

    map = folium.Map()

    for index, location_info in df_aux.iterrows(): 
        folium.Marker([location_info['Delivery_location_latitude'],
                  location_info['Delivery_location_longitude']],
                  popup = location_info[['City','Road_traffic_density']]).add_to(map)                 
    folium_static(map, width = 600 , height = 1024)  







  

# _________ Inicio da Estrutura logica do codigo______________
#


#Limpeza dos dados
#_____________________________________________________________
df1 = Clean_Code(df1)

#Visão Empresa

#A quantidade de pedidos por dia


st.header('Marketplace - Visão Cliente')

#Barra Lateral

image_path = 'image/delivery.jpg'

image = Image.open(image_path)

st.sidebar.image(image, width = 180)


st.sidebar.markdown('# Cury Company')
st.sidebar.markdown('## Fastest Delivery in Town')
st.sidebar.markdown("""___""")

st.sidebar.markdown('## Selecione uma data limite')
          
date_slider = st.sidebar.slider(
 'Até qual valor?',
  value = pd.to_datetime(2022,4,13),
  min_value = pd.to_datetime(2022,2,11),
  max_value = pd.to_datetime(2022,4,6),
  format = 'DD-MM-YYYY'
    
)

st.sidebar.markdown("""___""")
          
traffic_options = st.sidebar.multiselect(
'Quais as condições do transito', 
['Low', 'Medium', 'High', 'Jam'],
default = ['Low', 'Medium', 'High', 'Jam']
)          

st.sidebar.markdown("Powered by Alessandro Kaloupis")

#Indicando para que o filtro de data pegue todas as datas anteriores às que eu filtrei

linhas_selecionadas = df1['Order_Date'] < date_slider

df1 = df1.loc[linhas_selecionadas, :]

linhas_selecionadas = df1['Road_traffic_density'].isin(traffic_options)

df1 = df1.loc[linhas_selecionadas, :]

#---------------------------
#layout do Streamlit
#--------------------------

tab1, tab2, tab3 = st.tabs(['Visão Gerencial', 'Visão Tática', 'Visão Geográfica'])

with tab1:
    
    with st.container():
        
        st.markdown('# Orders by Day')                   
        fig = order_metrics(df1)
        st.plotly_chart(fig, use_containter_width = True)
        
    with st.container(): 
        
        col1, col2 = st.columns(2, gap = 'large')
        
        with col1: 
            
            st.markdown("## Traffic Order Share")   
            fig = traffic_order_share(df1)
            st.plotly_chart(fig, use_containter_width = True)
                
        with col2: 
            st.markdown("## Traffic Order City")
            fig =  traffic_order_city(df1)                 
            st.plotly_chart(fig, use_containter_width=True)
with tab2:
    
    with st.container():
        
        st.markdown("# Order by week")
        fig = order_by_week(df1)      
        st.plotly_chart(fig, use_containter_width=True)

    with st.container(): 
        st.markdown("# Order Share by Week")
        fig = order_share_by_week(df1)        
        st.plotly_chart(fig, use_containter_width=True)
        
with tab3: 
    st.markdown("# Country Maps")
    country_maps(df1)
                 
    
