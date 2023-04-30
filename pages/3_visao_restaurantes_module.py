#Libraries
import pandas as pd
import plotly.express as px
from haversine import haversine
import plotly.graph_objects as go
import streamlit as st
from PIL import Image
import folium
from streamlit_folium import folium_static
import numpy as np

#Importar o dataset

df1 = pd.read_csv('dataset/train.csv')
st.set_page_config(page_title = 'Visão Restaurantes', layout = 'wide')


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
 
def Distance(df1):
    '''
        Retorna a distancia media entre o restaurante e o local de entrega
        
        Input: DataFrame
        
        Output: variavel contendo o valor da distancia media
    
    '''
    
    
    
    cols = ['Restaurant_latitude', 'Restaurant_longitude', 'Delivery_location_latitude','Delivery_location_longitude' ]
    
    df1['distance'] = df1.loc[:, cols].apply(lambda x: 
    haversine((x['Restaurant_latitude'], x['Restaurant_longitude']),
    (x['Delivery_location_latitude'], x['Delivery_location_longitude'])), axis = 1)
            
    mean_distance = round(df1['distance'].mean(),2)
            
    return mean_distance    

def Avg_Time_Delivery_Festival(df1):
    
    '''
        Função que retorna o tempo médio de entrega durante o Festival
        Input: DataFrame
        Output: Variável que contem o tempo medio de entrega durante o Festival
    
    '''
        
                
    df_aux = pd.DataFrame(df1.loc[(df1['Festival'] == 'Yes ')].groupby
                      (by = ['Festival']).agg({'Time_taken(min)': 'mean'}))
            
    festival_time_taken = round(df_aux['Time_taken(min)'],2)
            
    return festival_time_taken

def Std_Time_Delivery_Festival(df1):    
    '''
        Função que retorna o desvio padrão de entrega durante o Festival
        Input: DataFrame
        Output: Variavel que contem o desvio padrao de entrega durante o Festival
    
    '''

    df_aux = pd.DataFrame(df1.loc[(df1['Festival'] == 'Yes ')].groupby
                      (by = ['Festival']).agg({'Time_taken(min)': 'std'}))
        
    festival_time_taken = round(df_aux['Time_taken(min)'],2)
            
    return festival_time_taken

def Avg_Time_Delivery_No_Festival(df1):
    
    '''
        Função que retorna o tempo médio de entrega sem o Festival
        Input: DataFrame
        Output: Variável que contem o tempo medio de entrega durante o Festival
    
    '''
        
                
    df_aux = pd.DataFrame(df1.loc[(df1['Festival'] == 'No ')].groupby
                      (by = ['Festival']).agg({'Time_taken(min)': 'mean'}))
            
    not_festival_time_taken = round(df_aux['Time_taken(min)'],2)
            
    return not_festival_time_taken

def Std_Time_Delivery_No_Festival(df1):    
    
    '''
        Função que retorna o desvio padrão de entrega sem o Festival
        Input: DataFrame
        Output: Variavel que contem o desvio padrao de entrega durante o Festival
    
    '''

    df_aux = pd.DataFrame(df1.loc[(df1['Festival'] == 'No ')].groupby
                      (by = ['Festival']).agg({'Time_taken(min)': 'std'}))
        
    not_festival_time_taken = round(df_aux['Time_taken(min)'],2)
            
    return not_festival_time_taken

def Mean_Time_Delivery_City(df1):
    '''
        Função que retorna uma figura com o tempo medio e o desvio padrao 
        das entregas por cidade
        Input: DataFrame
        Outpur: Plot de gráfico de barras
    
    '''
    df_aux = df1.loc[:, ['City', 'Time_taken(min)']].groupby( 'City' ).agg( {'Time_taken(min)': ['mean', 'std']} )
    
    df_aux.columns = ['avg_time', 'std_time']
    df_aux = df_aux.reset_index()
    fig = go.Figure() 
    
    fig = fig.add_trace( go.Bar( name='Control', x=df_aux['City'], y=df_aux['avg_time'], error_y=dict(type='data', array=df_aux['std_time'])))
    fig = fig.update_layout(barmode='group', autosize = False, width = 500, height = 400)
    
    return fig

def City_Order_Mean_STD(df1):
    '''
        Função que retorna o tempo medio e o desvio padrao por
        tipo de cidade e tipo de pedido
        
        Input: DataFrame
        Output: DataFrame
    '''
    
    
    df_aux = ( df1.loc[:, ['City', 'Time_taken(min)', 'Type_of_order']]
                          .groupby( ['City', 'Type_of_order'] )
                          .agg( {'Time_taken(min)': ['mean', 'std']} ) )

    df_aux.columns = ['avg_time', 'std_time']
    
    df_aux = df_aux.reset_index()
    
    return df_aux

def New_Distance(df1):
    '''
        Função que retorna a porcentagem de entregas por Cidade
        que excedeu o tempo medio de entrega
        
        Input: DataFrame
        Output:Plot

    '''

        
    cols = ['Delivery_location_latitude', 'Delivery_location_longitude', 'Restaurant_latitude','Restaurant_longitude']     
    
    df1['distance'] = df1.loc[:, cols].apply( lambda x: 
                                        haversine(  (x['Restaurant_latitude'], x['Restaurant_longitude']), 
                                                    (x['Delivery_location_latitude'], x['Delivery_location_longitude']) ), axis=1 )

    avg_distance = df1.loc[:, ['City', 'distance']].groupby( 'City' ).mean().reset_index()
    
    fig = go.Figure( data=[ go.Pie( labels=avg_distance['City'], values=avg_distance['distance'], pull=[0, 0.1, 0])])
    
    return fig

        
def Avg_Std_Time_or_Traffic(df1):
    '''
        Função que retorna o tempo medio e o desvio padrão
        por tempo e tipo de tráfego
        
        Input: DataFrame
        Output: Figura
    
    '''
    
    
    df_aux = ( df1.loc[:, ['City', 'Time_taken(min)', 'Road_traffic_density']]
                          .groupby( ['City', 'Road_traffic_density'] )
                          .agg( {'Time_taken(min)': ['mean', 'std']} ) )

    df_aux.columns = ['avg_time', 'std_time']
    df_aux = df_aux.reset_index()

    fig = px.sunburst(df_aux, path=['City', 'Road_traffic_density'], values='avg_time',
                              color='std_time', color_continuous_scale='RdBu',
                              color_continuous_midpoint=np.average(df_aux['std_time'] ) )
    
    return fig


    
#Df recebendo os valores e as colunas limpas    
df1 = Clean_Code(df1)    
    

#Titulo do dashboards

st.header("Marketplace - Visão Restaurantes")

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
  value = pd.datetime(2022,4,13),
  min_value = pd.datetime(2022,2,11),
  max_value = pd.datetime(2022,4,6),
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
        col1, col2, col3, col4, col5, col6 = st.columns(6)
        
        with col1: 
            delivery_unique = len(df1.loc[:, 'Delivery_person_ID'].unique())
            col1.metric("Entregadores únicos", value =  delivery_unique)
        
        with col2: 
            
            mean_distance = Distance(df1)
            col2.metric("Distância média dos restaurantes e dos locais de entrega", value = mean_distance )
            
        with col3: 
            
            festival_time_taken =  Avg_Time_Delivery_Festival(df1)                    
            col3.metric("Tempo médio", value = festival_time_taken )
                       
        with col4:
             
            festival_time_taken =  Std_Time_Delivery_Festival(df1)
            col4.metric("STD", value = festival_time_taken )
            
        with col5:
            
            not_festival_time_taken = Avg_Time_Delivery_No_Festival(df1)           
            col5.metric("Tempo médio", value = not_festival_time_taken )    
            
        with col6:
            
            not_festival_time_taken = Std_Time_Delivery_No_Festival(df1)
            col6.metric("STD", value = not_festival_time_taken )
            
            
            
  
    with st.container():
        st.markdown( """---""" )
        col1, col2 = st.columns( 2 )
        
        with col1:
            st.subheader("Tempo médio/STD: Por cidade")
            fig = Mean_Time_Delivery_City(df1)                   
            st.plotly_chart( fig )
            
        with col2:
            st.subheader("Cidade/Tipo de Pedido: Tempo Medio/STD")
            df_aux = City_Order_Mean_STD(df1)
            st.dataframe( df_aux, use_container_width = True )
        

        
    with st.container():
        
        st.markdown( """---""" )
        st.title( "Distribuição do Tempo" )
        col1, col2 = st.columns( 2 )
        
        with col1:
            fig = New_Distance(df1)   
            st.plotly_chart( fig )

            
        with col2:
            fig = Avg_Std_Time_or_Traffic(df1)
            st.plotly_chart( fig )
        
