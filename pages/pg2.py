import pandas as pd
import pages.settings as st
import plotly.graph_objects as go
import plotly.io as pio
import plotly.express as px
import dash
from dash import dcc, html, callback, Output, Input
import dash_bootstrap_components as dbc

dash.register_page(__name__, path='/page-2', name='Квартиры на карте') # '/' is home page

# cортировка словаря, составленного из 2-х списков, по значению
def sort_lists(x1,y1,order):
       dict_price = dict(zip(x1, y1)) #  составляем словарь из двух списков
# сортируем словарь по значению
       sorted_dict_price = {k: v for k, v in sorted(dict_price.items(), key=lambda item: item[1], reverse=order)} 
       x2=list(sorted_dict_price.keys()) # извлекаем ключи
       y2=list(sorted_dict_price.values()) # извлекаем значения
       return x2,y2

# Загрузка данных
#df = pd.read_csv('data/output2.csv')
df = pd.read_csv('data/data.csv')

#создаем в датасете df колонку "Цена кв м" и помещаем в нее цену за 1 кв м квартиры (в тыс руб)
df["Цена кв м"]=df["Цена (млн руб)"]/df["Площадь"]*1000
df["Цена кв м"]=df["Цена кв м"].apply(lambda x: round(x,3))


layout=html.Div([

# Заголовок
  dbc.Row([
           html.H5("Квартиры на карте города", className="header-2-title"),
        ], className="header-2"
        ),

# Фильтры
  dbc.Row([
      dbc.Col([html.Label("Станции метро", className="filter-label"), 
# Фильтр Радиокнопка - "Показывать все станции метро или выбрать станцию(-и) метро" 
              dcc.RadioItems(id='all-stations-filter',                            
              options=[
               {'label': 'Все', 'value': True},
               {'label': 'Выбрать', 'value': False},
               ],
              value=True,              
              inline=True                               )
              ], md=6),

      dbc.Col([html.Label("Метро", className="filter-label"),  
# Фильтр Выпадающее меню  "Выбрать станцию(-и) метро"                   
            dcc.Dropdown(id="district-filter",    
                      options=[{'label': sx, 'value': sx } for sx in df.sort_values(by='Метро', ascending=True)['Метро'].unique() if pd.notna(sx)],                           
                     # value=["Спортивная","Василеостровская","Приморская","Горный институт"], 
                      value="Приморская", 
                      multi=True,    
                      className="filter-dropdown", 
                      )
              ], md=6),
            ]),


  dbc.Row([       
      dbc.Col([html.Label("Число комнат", className="filter-label"), 
# Фильтр Флажок "Выбрать количество комнат в квартире"             
            dcc.Checklist(id='number-rooms-filter', 
                      options=df.sort_values("Количество комнат")["Количество комнат"].unique(), 
                      value=df["Количество комнат"].unique()[:],
                      inline=True,
                      className='my_box_container',           # class of the container (div)
                      style={'display':'flex'},             # style of the container (div)
                      inputClassName='my_box_input',          # class of the <input> checkbox element
                      labelClassName='my_box_label',          # class of the <label> that wraps the checkbox input and the option's label
                      )
                ], md=6),
                     
      dbc.Col([html.Label("Расстояние до метро (км)", className="filter-label"), 
# Фильтр Слайдер "Выбрать расстояние до метро (в км)"                   
            dcc.Slider( id="distance-metro-filter",
                      min=0,
                      max=45,
                      marks={i: '{}'.format(i) for i in range(0,45,5)},
                      value=45,
                      ),
                ], md=6)
          ]),


  dbc.Row([         
     dbc.Col([html.Label("Вид объекта", className="filter-label"), 
# Фильтр Флажок "Выбрать Тип здания"             
           dcc.Checklist(id='type-appartm-filter', 
                      options=df.sort_values("Вид объекта")["Вид объекта"].unique(), 
                      value=df["Вид объекта"].unique()[:],
                      inline=True,
                      className='my_box_container',           # class of the container (div)
                      style={'display':'flex'},             # style of the container (div)
                      inputClassName='my_box_input',          # class of the <input> checkbox element
                      labelClassName='my_box_label',          # class of the <label> that wraps the checkbox input and the option's label
                     )
              ], md=6),
                     
    dbc.Col([html.Label("Расстояние до центра (км)", className="filter-label"), 
# Фильтр Слайдер "Выбрать расстояние до центра города (в км)"                   
          dcc.Slider( id="distance-center-filter",
                      min=0,
                      max=55,
                      marks={i: '{}'.format(i) for i in range(0,55,5)},
                      value=55,
                      ),
             ], md=6)
       ]),


  dbc.Row([
      dbc.Col([html.Label("Максимальная цена (млн руб)", className="filter-label"),  
# Фильтр Слайдер "Выбрать максимальную цену квартиры (в млн руб)"                       
          dcc.Slider( id="price-filter",
                      min=0,
                      max=40,
                      marks={i: '{}'.format(i) for i in range(0,41,5)},
                      value=41,
                    )
            ], md=6),

      dbc.Col([html.Label("Максимальная площадь (кв м)", className="filter-label"), 
# Фильтр Слайдер "Выбрать максимальную площадь квартиры (кв м)"                  
          dcc.Slider( id="area-filter",
                      min=0,
                      max=100,
                      marks={i: '{}'.format(i) for i in range(0,100,20)},
                      value=100,
                    ),
              ], md=6)
        ]),         
                
# Графики

# График "Карта города"
  dbc.Row([dbc.Col([dcc.Graph(id="choropleth-maps-x-graph")], md=12)]),

# График "Распределение по площади"
  dbc.Row([dbc.Col([dcc.Graph(id="fig_area_scatter")], md=12), 
          ]),

  dbc.Row([
      dbc.Col([
# Фильтр Радиокнопка для графика "Распределение по расстоянию"
           dbc.RadioItems(options=[{"label": x, "value": x} for x in ['Расстояние до центра', 'Расстояние до метро']],
                           value='Расстояние до центра',
                           inline=True,
                           id='radio-buttons-dependence-price')], md=6),
        dbc.Col([
# Фильтр Радиокнопка для графика "Распределение по числу комнат"
             dbc.RadioItems(options=[{"label": x, "value": x} for x in ['Число квартир', 'Средняя цена', 'Цена за 1 кв м']],
                            value='Число квартир',
                            inline=True,
                            id='radio-buttons-number-rooms')], md=6)
         ]),


  dbc.Row([
       dbc.Col([
# График "Распределение по расстоянию"
            dcc.Graph(id="fig_scatter")], md=6),

        dbc.Col([
# График "Распределение по числу комнат"
             dcc.Graph(id='body-mass-histogram')], md=6)
          ]),


  dbc.Row([
        dbc.Col([
# Фильтр Радиокнопка для графика "Распределение по станциям метро"
             dbc.RadioItems(options=[{"label": x, "value": x} for x in ['Число квартир', 'Средняя цена', 'Цена за 1 кв м']],
                           value='Число квартир',
                           inline=True,
                           id='radio-buttons-final')], md=6)
           ]),


  dbc.Row([
        dbc.Col([
# График "Распределение по станциям метро"
             dcc.Graph(id='my-first-graph-final')], md=12)
            ]),

#информационная панель

  html.Div(id='stats-panel-2', className="stats-panel")

  ])


# установка кастомной палетки цветов для всех графиков plotly
pio.templates['custom'] = pio.templates['plotly'].update(
    layout=dict(colorway=st.MY_PALETTE)
)
pio.templates.default = "custom"


# Колбэки

@callback(
    Output("choropleth-maps-x-graph", "figure"),
    Output("fig_area_scatter", "figure"),
    Output("fig_scatter", "figure"),
    Output("body-mass-histogram", "figure"),
    Output('my-first-graph-final', 'figure'),
    Output('stats-panel-2', 'children'),
    Input("all-stations-filter", "value"),
    Input("number-rooms-filter", "value"),
    Input("district-filter", "value"),
    Input("price-filter", "value"),
    Input("area-filter", "value"),
    Input("distance-metro-filter", "value"),
    Input('radio-buttons-dependence-price', 'value'),
    Input('radio-buttons-number-rooms', 'value'),
    Input('radio-buttons-final', 'value'),
    Input('type-appartm-filter','value'),
    Input("distance-center-filter",'value')
 )
def update_graphs(stations,number_rooms,district,price,area,distance_metro,col_dep_price,col_num_rooms,col_chosen,type_apt,distance_center):

# Создание датасета df1 согласно выбору фильтров
       df1 = df[(df["Количество комнат"].isin(number_rooms)) & (df["Цена (млн руб)"] < price)]
       df1= df1[(df1["Площадь"] < area) & (df1["До метро"] < distance_metro)]
       df1= df1[(df1["Вид объекта"].isin(type_apt)) & (df1["До центра"] < distance_center)]

       if stations == True:
# Все станции Метро
            pass
       else:
# Учитываем фильтр со станциями Метро
            df1 = df1[df1['Метро'].isin(district)] 

# Подсчет статистики
       total_flats = len(df1)
       price_min = df1["Цена (млн руб)"].min()
       price_max = df1["Цена (млн руб)"].max()
       price_avr = df1["Цена (млн руб)"].mean()


# График "Географическая карта"
       fig = go.Figure(go.Scattermap(
       lat = df1['lat'].tolist(),
       lon = df1['lng'].tolist(),

          
       hovertemplate= (
           #df1["Дата"].apply(lambda x: "Дата: " + str(x)  + "<br>") +
          df1["Адрес"].apply(lambda x: "Адрес: "+str(x)+ "<br>") +
          df1["Площадь"].apply(lambda x: "Площадь (кв м): " + str(x)  + "<br>") +
          df1["Количество комнат"].apply(lambda x: "Количество комнат: "+ str(x) + "<br>") +
          df1["Этаж"].apply(lambda x: "Этаж: "+ str(x) + "<br>") +
          df1["Этажей в доме"].apply(lambda x: "Этажей в доме: "+str(x)+ "<br>") +
          df1["Цена (млн руб)"].apply(lambda x: "Цена (млн руб): "+ str(x))        
          ).tolist(),
          

       marker = {'size': 10, 'color': "blue"},
       name=""  # Stops 'trace0' from showing up on popup annotation
      ))
     
       fig.update_layout(
         showlegend=False,
         xaxis={"range": [0, 100]},
         height=500,
         margin=dict(l=10, r=10, t=10, b=20),
         )

       fig.update_layout(
           map = {
           'style': "open-street-map",
           'center': {'lat': 59.93, 'lon': 30.33 },
           'zoom': 8},    
            showlegend = False)
       

# График "Распределение по площади"
       fig_area_scatter = go.Figure(go.Scatter(
           y = df1['Цена (млн руб)'].tolist(),
           x = df1['Площадь'].tolist(),

          hovertemplate= (
              #df1["Дата"].apply(lambda x: "Дата: " + str(x)  + "<br>") +
          df1["Адрес"].apply(lambda x: "Адрес: "+str(x)+ "<br>") +
          df1["Площадь"].apply(lambda x: "Площадь (кв м): " + str(x)  + "<br>") +
          df1["Количество комнат"].apply(lambda x: "Количество комнат: "+ str(x) + "<br>") +
          df1["Этаж"].apply(lambda x: "Этаж: "+ str(x) + "<br>") +
          df1["Этажей в доме"].apply(lambda x: "Этажей в доме: "+str(x)+ "<br>") +
          df1["Цена (млн руб)"].apply(lambda x: "Цена (млн руб): "+ str(x))        
          ).tolist(),

           mode='markers',
           name="",
           marker=dict(
                size=10,
                opacity=0.7,
                line=dict(width=1, color='DarkSlateGrey')
                )
        ))

       fig_area_scatter.update_layout(
            title="Распределение по площади",
            title_font_size=st.GRAPH_TITLE_FONT_SIZE,
            title_x=st.GRAPH_TITLE_ALIGN,
            title_font_weight=st.GRAPH_TITLE_WEIGHT,
            yaxis_title="Цена (млн руб)",
            xaxis_title="Площадь (кв м)",
            font=dict(family="Roboto, sans-serif"),
            xaxis=dict(title_font_size=st.GRAPH_FONT_SIZE, tickfont=dict(size=st.GRAPH_FONT_SIZE)),
            yaxis=dict(title_font_size=st.GRAPH_FONT_SIZE, tickfont=dict(size=st.GRAPH_FONT_SIZE)),
            legend=dict(font=dict(size=st.GRAPH_FONT_SIZE)),
            plot_bgcolor=st.PLOT_BACKGROUND,
            paper_bgcolor=st.PAPER_BACKGROUND,
        )

# Два графика "Распределение по расстоянию"     
       if col_dep_price == "Расстояние до метро":

# График "Расстояние до метро" 
        fig_scatter = go.Figure(go.Scatter(
           y = df1['Цена (млн руб)'].tolist(),
           x = df1['До метро'].tolist(),

          hovertemplate= (
              #df1["Дата"].apply(lambda x: "Дата: " + str(x)  + "<br>") +
          df1["Адрес"].apply(lambda x: "Адрес: "+str(x)+ "<br>") +
          df1["Площадь"].apply(lambda x: "Площадь (кв м): " + str(x)  + "<br>") +
          df1["Количество комнат"].apply(lambda x: "Количество комнат: "+ str(x) + "<br>") +
          df1["Этаж"].apply(lambda x: "Этаж: "+ str(x) + "<br>") +
          df1["Этажей в доме"].apply(lambda x: "Этажей в доме: "+str(x)+ "<br>") +
          df1["Цена (млн руб)"].apply(lambda x: "Цена (млн руб): "+ str(x))        
          ).tolist(),

           mode='markers',
           name="",
           marker=dict(
                size=10,
                opacity=0.7,
                line=dict(width=1, color='DarkSlateGrey')
                )
        ))

        fig_scatter.update_layout(
            title="Распределение по расстоянию",
            title_font_size=st.GRAPH_TITLE_FONT_SIZE,
            title_x=st.GRAPH_TITLE_ALIGN,
            title_font_weight=st.GRAPH_TITLE_WEIGHT,
            yaxis_title="Цена (млн руб)",
            xaxis_title="Расстояние до метро (км)",
            font=dict(family="Roboto, sans-serif"),
            xaxis=dict(title_font_size=st.GRAPH_FONT_SIZE, tickfont=dict(size=st.GRAPH_FONT_SIZE)),
            yaxis=dict(title_font_size=st.GRAPH_FONT_SIZE, tickfont=dict(size=st.GRAPH_FONT_SIZE)),
            legend=dict(font=dict(size=st.GRAPH_FONT_SIZE)),
            plot_bgcolor=st.PLOT_BACKGROUND,
            paper_bgcolor=st.PAPER_BACKGROUND,

        )

       else:

# График "Расстояние до центра"
        fig_scatter = go.Figure(go.Scatter(
           y = df1['Цена (млн руб)'].tolist(),
           x = df1['До центра'].tolist(),

          hovertemplate= (
              #df1["Дата"].apply(lambda x: "Дата: " + str(x)  + "<br>") +
          df1["Адрес"].apply(lambda x: "Адрес: "+str(x)+ "<br>") +
          df1["Площадь"].apply(lambda x: "Площадь (кв м): " + str(x)  + "<br>") +
          df1["Количество комнат"].apply(lambda x: "Количество комнат: "+ str(x) + "<br>") +
          df1["Этаж"].apply(lambda x: "Этаж: "+ str(x) + "<br>") +
          df1["Этажей в доме"].apply(lambda x: "Этажей в доме: "+str(x)+ "<br>") +
          df1["Цена (млн руб)"].apply(lambda x: "Цена (млн руб): "+ str(x))        
          ).tolist(),

           mode='markers',
           name="",
           marker=dict(
                size=10,
                opacity=0.7,
                line=dict(width=1, color='DarkSlateGrey')
                )
        ))

        fig_scatter.update_layout(
            title="Распределение по расстоянию",
            title_font_size=st.GRAPH_TITLE_FONT_SIZE,
            title_x=st.GRAPH_TITLE_ALIGN,
            title_font_weight=st.GRAPH_TITLE_WEIGHT,
            yaxis_title="Цена (млн руб)",
            xaxis_title="Расстояние до центра (км)",
            font=dict(family="Roboto, sans-serif"),
            xaxis=dict(title_font_size=st.GRAPH_FONT_SIZE, tickfont=dict(size=st.GRAPH_FONT_SIZE)),
            yaxis=dict(title_font_size=st.GRAPH_FONT_SIZE, tickfont=dict(size=st.GRAPH_FONT_SIZE)),
            legend=dict(font=dict(size=st.GRAPH_FONT_SIZE)),
            plot_bgcolor=st.PLOT_BACKGROUND,
            paper_bgcolor=st.PAPER_BACKGROUND,

        )

# Три графика "Распределение по числу комнат"

       hist_fig = go.Figure()

# Список Количество комнат
       x1=df1['Количество комнат'].unique().tolist()

       if col_num_rooms == "Число квартир":
            
# График "Распределение числа квартир по числу комнат"

            y2=[] # Число каждого количества комнат 
            for number_rooms in df1['Количество комнат'].unique():
               name2=int(df1[df1['Количество комнат'] == number_rooms]['Количество комнат'].count()),
               y2.append(name2[0])
            x6, y6 = sort_lists(x1,y2,True) # сортировка по убыванию числа количества комнат

            hist_fig = go.Figure(data=[go.Bar(x=x6, y=y6,
            text=y6,
            textposition="outside",
            textfont=dict(color="black"),
            cliponaxis=False
            )])                           

            hist_fig.update_layout(
            title="Распределение по числу комнат",
            title_font_size=st.GRAPH_TITLE_FONT_SIZE,
            title_x=st.GRAPH_TITLE_ALIGN,
            title_font_weight=st.GRAPH_TITLE_WEIGHT,
            yaxis_title="Число квартир",
            xaxis_title="Число комнат",
            xaxis=dict(title_font_size=st.GRAPH_FONT_SIZE, tickfont=dict(size=st.GRAPH_FONT_SIZE)),
            yaxis=dict(title_font_size=st.GRAPH_FONT_SIZE, tickfont=dict(size=st.GRAPH_FONT_SIZE)),
            legend=dict(font=dict(size=st.GRAPH_FONT_SIZE)),
            plot_bgcolor=st.PLOT_BACKGROUND,
            paper_bgcolor=st.PAPER_BACKGROUND,
            font=dict(family="Roboto, sans-serif"),
            barmode='overlay',
        )
      
       elif col_num_rooms == "Средняя цена":
            
# График "Распределение средней цены квартир по числу комнат"

            y1=[] # Средняя цена каждого количества комнат   
            for number_rooms in df1['Количество комнат'].unique():  
              name1=float(round(df1[df1['Количество комнат'] == number_rooms]['Цена (млн руб)'].mean(),3)),
              y1.append(name1[0])
            x5, y5 = sort_lists(x1,y1,True) # сортировка по убыванию цены
             
            hist_fig = go.Figure(data=[go.Bar(x=x5, y=y5,
            text=y5,
            textposition="outside",
            textfont=dict(color="black"),
            cliponaxis=False
            )])
                           

            hist_fig.update_layout(
            title="Распределение по числу комнат",
            title_font_size=st.GRAPH_TITLE_FONT_SIZE,
            title_x=st.GRAPH_TITLE_ALIGN,
            title_font_weight=st.GRAPH_TITLE_WEIGHT,
            yaxis_title="Средняя цена (млн руб)",
            xaxis_title="Число комнат",
            xaxis=dict(title_font_size=st.GRAPH_FONT_SIZE, tickfont=dict(size=st.GRAPH_FONT_SIZE)),
            yaxis=dict(title_font_size=st.GRAPH_FONT_SIZE, tickfont=dict(size=st.GRAPH_FONT_SIZE)),
            legend=dict(font=dict(size=st.GRAPH_FONT_SIZE)),
            plot_bgcolor=st.PLOT_BACKGROUND,
            paper_bgcolor=st.PAPER_BACKGROUND,
            font=dict(family="Roboto, sans-serif"),
            barmode='overlay',
        )
            
       else:
            
# График "Распределение цены 1 кв м по числу комнат"

            y2a=[]  # Средняя цена 1 кв метра для каждого количества комнат 
            for number_rooms in df1['Количество комнат'].unique():
              name2a=float(round(df1[df1['Количество комнат'] == number_rooms]['Цена кв м'].mean(),3)),
              y2a.append(name2a[0])
            x7, y7 = sort_lists(x1,y2a,True) # сортировка по убыванию средней цены 1 кв метра

             
            hist_fig = go.Figure(data=[go.Bar(x=x7, y=y7,
            text=y7,
            textposition="outside",
            textfont=dict(color="black"),
            cliponaxis=False
            )])
                           

            hist_fig.update_layout(
            title="Распределение по числу комнат",
            title_font_size=st.GRAPH_TITLE_FONT_SIZE,
            title_x=st.GRAPH_TITLE_ALIGN,
            title_font_weight=st.GRAPH_TITLE_WEIGHT,
            yaxis_title="Средняя цена за 1 кв м (тыс руб)",
            xaxis_title="Число комнат",
            xaxis=dict(title_font_size=st.GRAPH_FONT_SIZE, tickfont=dict(size=st.GRAPH_FONT_SIZE)),
            yaxis=dict(title_font_size=st.GRAPH_FONT_SIZE, tickfont=dict(size=st.GRAPH_FONT_SIZE)),
            legend=dict(font=dict(size=st.GRAPH_FONT_SIZE)),
            plot_bgcolor=st.PLOT_BACKGROUND,
            paper_bgcolor=st.PAPER_BACKGROUND,
            font=dict(family="Roboto, sans-serif"),
            barmode='overlay',
        )


# станции метро

 # Три графика "Распределение по станциям метро" 
       fig_metro = go.Figure()

# Список Все станции Метро
       x2=df1['Метро'].unique().tolist()       

       if col_chosen == "Число квартир":
            
# График "Распределение числа квартир по станциям метро" 

            y4=[] # Число квартир для каждой станции метро
            for station in df1['Метро'].unique():
               name4=int(df1[df1['Метро'] == station]['Метро'].count()),
               y4.append(name4[0]) 
            x4, y4 = sort_lists(x2,y4,False) # сортировка по убыванию числа количества комнат
 
            fig_metro = go.Figure(data=[go.Bar(y=x4, x=y4, orientation='h',
            text=y4,
            textposition="outside",
            textfont=dict(color="black"),                            
                                  )])
            fig_metro.update_layout(
            title="Распределение по станциям метро",
            title_font_size=st.GRAPH_TITLE_FONT_SIZE,
            title_x=st.GRAPH_TITLE_ALIGN,
            title_font_weight=st.GRAPH_TITLE_WEIGHT,
            yaxis_title="Метро",
            xaxis_title="Число квартир",
            xaxis=dict(title_font_size=st.GRAPH_FONT_SIZE, tickfont=dict(size=st.GRAPH_FONT_SIZE)),
            yaxis=dict(title_font_size=st.GRAPH_FONT_SIZE, tickfont=dict(size=st.GRAPH_FONT_SIZE)),
            legend=dict(font=dict(size=st.GRAPH_FONT_SIZE)),
            plot_bgcolor=st.PLOT_BACKGROUND,
            paper_bgcolor=st.PAPER_BACKGROUND,
            font=dict(family="Roboto, sans-serif"),
            barmode='overlay',
            height=23 * len(x2) + 200,
        )
           
       elif col_chosen == "Средняя цена":
            
 # График "Распределение средней цены квартиры по станциям метро" 
 # 
 #  
            y4=[] # Средняя цена для каждой станции метро 
            for station in df1['Метро'].unique():
              name3=float(round(df1[df1['Метро'] == station]['Цена (млн руб)'].mean(),3)),
              y4.append(name3[0]) 
            x3, y3 = sort_lists(x2,y4,False)  # сортировка по убыванию цены

 
            fig_metro = go.Figure(data=[go.Bar(y=x3, x=y3, orientation='h', 
            text=y3,
            textposition="outside",
            textfont=dict(color="black"),
            )
            ])

            fig_metro.update_layout(
            title="Распределение по станциям метро",
            title_font_size=st.GRAPH_TITLE_FONT_SIZE,
            title_x=st.GRAPH_TITLE_ALIGN,
            title_font_weight=st.GRAPH_TITLE_WEIGHT,
            xaxis_title="Средняя цена (млн руб)",
            yaxis_title="Метро",
            xaxis=dict(title_font_size=st.GRAPH_FONT_SIZE, tickfont=dict(size=st.GRAPH_FONT_SIZE)),
            yaxis=dict(title_font_size=st.GRAPH_FONT_SIZE, tickfont=dict(size=st.GRAPH_FONT_SIZE)),
            legend=dict(font=dict(size=st.GRAPH_FONT_SIZE)),
            plot_bgcolor=st.PLOT_BACKGROUND,
            paper_bgcolor=st.PAPER_BACKGROUND,
            font=dict(family="Roboto, sans-serif"),
            barmode='overlay',
            height= 23 * len(x2) + 200
        )
            
       else :
 # График "Распределение цены 1 кв м квартиры по станциям метро" 

            y4a=[] # Средняя цена 1 кв м для каждой станции метро 
            for station in df1['Метро'].unique():
               name4a=float(round(df1[df1['Метро'] == station]['Цена кв м'].mean(),3)),
               y4a.append(name4a[0]) 
            x8, y8 = sort_lists(x2,y4a,False)  # сортировка по убыванию средней цены 1 кв метра  

            fig_metro = go.Figure(data=[go.Bar(y=x8, x=y8, orientation='h', 
            text=y8,
            textposition="outside",
            textfont=dict(color="black"),
            )
            ])

            fig_metro.update_layout(
            title="Распределение по станциям метро",
            title_font_size=st.GRAPH_TITLE_FONT_SIZE,
            title_x=st.GRAPH_TITLE_ALIGN,
            title_font_weight=st.GRAPH_TITLE_WEIGHT,
            xaxis_title="Средняя цена за 1 кв м(тыс руб)",
            yaxis_title="Метро",
            xaxis=dict(title_font_size=st.GRAPH_FONT_SIZE, tickfont=dict(size=st.GRAPH_FONT_SIZE)),
            yaxis=dict(title_font_size=st.GRAPH_FONT_SIZE, tickfont=dict(size=st.GRAPH_FONT_SIZE)),
            legend=dict(font=dict(size=st.GRAPH_FONT_SIZE)),
            plot_bgcolor=st.PLOT_BACKGROUND,
            paper_bgcolor=st.PAPER_BACKGROUND,
            font=dict(family="Roboto, sans-serif"),
            barmode='overlay',
            height= 23 * len(x2) + 200
        )

# информационная панель
       stats_panel_2 = dbc.Card([
            dbc.CardHeader("Статистика выборки", className="stats-header"),
            dbc.CardBody([
                html.P(f"Всего квартир: {total_flats}"),
                html.P(f"Минимальная цена: {price_min:.3f} (млн руб)"),
                html.P(f"Максимальная цена: {price_max:.3f} (млн руб)"),
                html.P(f"Средняя цена: {price_avr:.3f} (млн руб)"),
            ])

        ])


       return fig, fig_area_scatter, fig_scatter, hist_fig, fig_metro, stats_panel_2
 
    



    