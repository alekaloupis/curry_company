#Libraries
import pandas as pd
import plotly.express as px
from haversine import haversine
import plotly.graph_objects as go
import streamlit as st
from PIL import Image
import folium
from streamlit_folium import folium_static
from datetime import datetime

#Importar o dataset
df1 = pd.read_csv('dataset/train.csv')
st.set_page_config(page_title = 'Visão Entregadores', layout = 'wide')

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

def Top_Delivers(df1, top_asc):
    
    '''
        Função que retorna os 10 entregadores 
        mais lentos ou mais rápidos de cada tipo de cidade
        
        O parâmetro top_asc - True/False indica
            True: Para retornar os entregadores mais rapidos
            False: Para retornar os entregadores mais lentos
        
        
        Input: DataFrame
        Output: DataFrame
        
    '''
            
    least_fast_metr = df1.loc[(df1['City'] == 'Metropolitian ')].groupby(by =
    ['Delivery_person_ID']).mean().sort_values(by = 'Time_taken(min)', 
    ascending=top_asc).reset_index().head(10)[['Delivery_person_ID', 'Time_taken(min)']]

    least_fast_metr['City'] = 'Metropolitian'

    least_fast_urban = df1.loc[(df1['City'] == 'Urban ')].groupby(by =
    ['Delivery_person_ID']).mean().sort_values(by = 'Time_taken(min)', 
    ascending=top_asc).reset_index().head(10)[['Delivery_person_ID', 'Time_taken(min)']]

    least_fast_urban['City'] = 'Urban'

    least_fast_semi_urban = df1.loc[(df1['City'] == 'Semi-Urban ')].groupby(by =
    ['Delivery_person_ID']).mean().sort_values(by = 'Time_taken(min)', 
    ascending=top_asc).reset_index().head(10)[['Delivery_person_ID', 'Time_taken(min)']]

    least_fast_semi_urban['City'] = 'Semi-Urban'

    least_most_fast_delivery = pd.concat([least_fast_metr, least_fast_urban, least_fast_semi_urban])
                
    return least_most_fast_delivery  
                                       
def Avg_Ratings_Road_Traffic(df1):
    '''
        Função que retorna a média e do desbio padrao das avaliações
        por tipo de transito
    
    '''
    
            
    df_avg_ratings_road_traffic = pd.DataFrame(df1.groupby(by =  ['Road_traffic_density']).agg(
                    {'Delivery_person_Ratings': ['mean', 'std']}))

    return df_avg_ratings_road_traffic
    

def Avg_Ratings_per_deliver(df1):
    '''
        Função que retorna a média das avaliações
        
        por entregador
    '''
    
    df_avg_ratings_per_deliver = pd.DataFrame(df1.groupby(by = ['Delivery_person_ID']).mean
     ().reset_index()[['Delivery_person_ID', 'Delivery_person_Ratings']])
            
    return df_avg_ratings_per_deliver    

def Avg_Ratings_Weather(df1):
    '''
        Função que retorna a média e o desvio padrao das
        
        avaliações por condições climáticas
    
    '''
    
    df_avg_ratings_weather = pd.DataFrame(df1.groupby(by = ['Weatherconditions']).agg({'Delivery_person_Ratings': ['mean', 'std']}))
    
    return df_avg_ratings_weather
    
    
#Dataset limpo

df1 = Clean_Code(df1)
   


#Titulo do dashboards

st.header("Marketplace - Visão Entregadores")

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
  value = datetime(2022,4,13),
  min_value = datetime(2022,2,11),
  max_value = datetime(2022,4,6),
  format = 'DD-MM-YYYY'
    
)

st.sidebar.markdown("""___""")
          
traffic_options = st.sidebar.multiselect(
'Quais as condições do transito?', 
['Low', 'Medium', 'High', 'Jam'],
default = ['Low', 'Medium', 'High', 'Jam']
)          

weather_options = st.sidebar.multiselect(
'Quais as condições climáticas?', 
 ['conditions Fog','conditions Stormy','conditions Cloudy', 'conditions Windy','conditions Sandstorms','conditions Sunny'], 
 default = ['conditions Fog','conditions Stormy','conditions Cloudy', 'conditions Windy','conditions Sandstorms','conditions Sunny']     
)


st.sidebar.markdown("Powered by Alessandro Kaloupis")

#Indicando para que o filtro de data pegue todas as datas anteriores às que eu filtrei

linhas_selecionadas = df1['Order_Date'] < date_slider

df1 = df1.loc[linhas_selecionadas, :]

linhas_selecionadas = df1['Road_traffic_density'].isin(traffic_options)

df1 = df1.loc[linhas_selecionadas, :]

linhas_selecionadas = df1['Weatherconditions'].isin(weather_options)

df1 = df1.loc[linhas_selecionadas, :]

#---------------------------
#layout do Streamlit
#--------------------------

tab1, tab2, tab3 = st.tabs(['Visão Gerencial', '_', '_'])

with tab1: 
    
    with st.container(): 
        
        st.title("Overall Metrics")
        col1, col2, col3, col4 = st.columns(4, gap = 'large')
        
        with col1: 
            maior_idade = df1['Delivery_person_Age'].max()
            col1.metric('Maior de idade', maior_idade )
            
        with col2: 
            menor_idade = df1['Delivery_person_Age'].min()
            col2.metric('Menor de idade', menor_idade )


        with col3: 
            melhor_veiculo =  df1['Vehicle_condition'].max()
            col3.metric("Melhor veiculo", melhor_veiculo)
            
        with col4: 
            pior_veiculo = df1['Vehicle_condition'].min()
            col4.metric("Pior veiculo", pior_veiculo)
    with st.container():
        
        st.markdown("___")
        st.title("Avaliações")
        col1, col2 = st.columns(2, gap = 'large')
        
        with col1: 
            st.markdown("###### Avaliação média por Entregador")
            df_avg_ratings_per_deliver= Avg_Ratings_per_deliver(df1)
            st.dataframe(df_avg_ratings_per_deliver)
            
        with col2: 
            st.markdown("###### Avaliação média por Trânsito")                     
            df_avg_ratings_road_traffic = Avg_Ratings_Road_Traffic(df1)
            st.dataframe(df_avg_ratings_road_traffic)


            st.markdown("###### Avalição média por clima")
            df_avg_ratings_weather = Avg_Ratings_Weather(df1)            
            st.dataframe(df_avg_ratings_weather)
     
    with st.container():
        
        st.markdown("""___""")
        st.title("Velocidade de Entrega")
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("##### Top Entregadores mais rápidos")
            least_most_fast_delivery = Top_Delivers(df1, True)
            st.dataframe(least_most_fast_delivery)

            
        with col2: 
            st.markdown("##### Top Entregadores mais lentos")
            least_most_fast_delivery = Top_Delivers(df1, False)
            st.dataframe(least_most_fast_delivery)
            
        
            
            
