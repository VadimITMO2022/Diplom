import pandas as pd
import numpy as np
import pages.settings as st
import sklearn
from sklearn.datasets import fetch_openml
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import StandardScaler, PolynomialFeatures
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
import plotly.graph_objects as go
import plotly.io as pio
import plotly.express as px
import dash
from dash import dcc, html, callback, Output, Input
import dash_bootstrap_components as dbc

dash.register_page(__name__, path='/page-3', name='Стоимость квартиры')


ml = pd.read_csv('data/data.csv')
df = pd.read_csv('data/data.csv')

# преобразуем датасет ml
ml=ml.dropna()
#ml1 = ml.copy()


# функции для замены строковой переменной на число

def room_to_index(x): # функция для замены количества комнат на целое число
   ml_index=np.sort(df['Количество комнат'].unique()) # отсортированный массив
   idx = np.where(ml_index == x) # индекс элемента массива х
   return int(idx[0][0])


def metro_to_index(x): # функция для замены названия станции метро на целое число (индекс)
   ml_index=np.sort(df['Метро'].unique()) # отсортированный массив
   idx = np.where(ml_index == x) # индекс элемента массива х
   return int(idx[0][0])


def type_to_index(x): # функция для замены названия типа недвижимости на целое числа (индекс)
   ml_index=np.sort(df['Вид объекта'].unique()) # отсортированный массив
   idx = np.where(ml_index == x) # индекс элемента массива х
   return int(idx[0][0])
# создаем копию датасета ml
# она будет нужна для фильтров/селекторов
#ml0=ml.copy()

# создаем копию датасета ml
# она будет нужна для функций преобразования строковых переменных в числа
#ml1=ml[['Метро', 'Bид объекта', 'Количество комнат']].copy()


# преобразуем датасет ml
#ml=ml.dropna()
ml=ml[(ml['Срок сдачи']>2020) & (ml['Срок сдачи']<2030)]
ml=ml[(ml['До метро']<5) & (ml['До центра']<24)]
ml=ml[(ml['Площадь'] > 9.99) & (ml['Площадь']<63)]

# ml1 копия датафрейма ml
ml1 = ml.copy()

# заменяем строковые названия на числа
ml['Количество комнат_int']=ml['Количество комнат'].apply(lambda x:  room_to_index(x))
ml['Метро_int']=ml['Метро'].apply(lambda x:  metro_to_index(x))
ml['Вид объекта_int']=ml['Вид объекта'].apply(lambda x:  type_to_index(x))

# удаляем колонки с данными, которые не влияют на образование цены квартиры
ml= ml.drop(['Адрес','lat','lng'], axis=1)
# Удаляем колонки, данные которых коррелируют с данными других колонок
ml= ml.drop(['Этажей в доме'], axis=1)

# удаляем также колонки со строковыми данными (их роль играют колонки с числами)
ml= ml.drop(['Количество комнат','Метро','Вид объекта'], axis=1)




layout = html.Div([

# Заголовок    
  dbc.Row([
            html.H5("Оценка стоимости квартиры", className="header-2-title"),
            html.H4("Введите параметры:", className="header-2-description")
          ], className="header-2"
          ),
 
# Фильтры
  dbc.Row([     
     dbc.Col([html.Label("Год постройки", className="filter-label"),  
# Выпадающее меню "Год постройки"             
          dcc.Dropdown(id="year-ml-filter",
                       options=[{'label': sx, 'value': sx } for sx in ml1.sort_values(by='Срок сдачи', ascending=False)['Срок сдачи'].unique() if pd.notna(sx)],
                       value = 2022,
                       multi=False,   
                       className="filter-dropdown", 
                       )
                    ], md=6),

      dbc.Col([html.Label("Метро", className="filter-label"),  
# Фильтр Выпадающее меню  "Выбрать станцию(-и) метро"                      
          dcc.Dropdown(id="district-ml-filter",
                       options=[{'label': sx, 'value': sx } for sx in ml1.sort_values(by='Метро', ascending=True)['Метро'].unique() if pd.notna(sx)],
                       value="Приморская",
                       multi=False,   
                       className="filter-dropdown", 
                       )
              ], md=6),

         ]), 

dbc.Row([   
      dbc.Col([html.Label("Число комнат", className="filter-label"), 
# Фильтр Флажок "Выбрать количество комнат в квартире"             
            dcc.RadioItems(id='number-rooms-ml-filter', 
                      options=df.sort_values("Количество комнат")["Количество комнат"].unique(), 
                      value="Студия",
                      inline=True,
                      className='my_box_container',           # class of the container (div)
                      style={'display':'flex'},             # style of the container (div)
                      inputClassName='my_box_input',          # class of the <input> checkbox element
                      labelClassName='my_box_label',          # class of the <label> that wraps the checkbox input and the option's label
                      )
                ], md=6),


       dbc.Col([html.Label("Расстояние до метро (км)", className="filter-label"),
# Фильтр Слайдер "Выбрать расстояние до метро (в км)"                     
          dcc.Slider(id="distance-metro-ml-filter",
                      min=0,
                      max=5,
                      marks={i: '{}'.format(i) for i in range(0,5,1)},
                      value=3,
                      )
                    ], md=6),
         ]),                 
                
  dbc.Row([            
      dbc.Col([html.Label("Вид объекта", className="filter-label"), 
# Выпадающее меню "Выбрать Тип здания"             
       #   dcc.Dropdown(id="type-ml-filter",
       #                options=[{'label': sx, 'value': sx } for sx in ml1.sort_values(by='Вид объекта', ascending=True)['Вид объекта'].unique() if pd.notna(sx)],
       #                value="Вторичка",
       #                multi=False,   
       #                className="filter-dropdown", 
       #                )
       #       ], md=6),

#  Фильтр Флажок "Выбрать количество комнат в квартире"             
            dcc.RadioItems(id='type-ml-filter', 
                      options=df.sort_values("Вид объекта")["Вид объекта"].unique(), 
                      value="Новостройка",
                      inline=True,
                      className='my_box_container',           # class of the container (div)
                      style={'display':'flex'},             # style of the container (div)
                      inputClassName='my_box_input',          # class of the <input> checkbox element
                      labelClassName='my_box_label',          # class of the <label> that wraps the checkbox input and the option's label
                      )
                ], md=6),

       dbc.Col([html.Label("Расстояние до центра (км)", className="filter-label"),
# Фильтр Слайдер "Выбрать расстояние до центра города (в км)"                     
          dcc.Slider(id="distance-center-ml-filter",
                      min=0,
                      max=10,
                      marks={i: '{}'.format(i) for i in range(0,24,1)},
                      value=5,
                      )
                    ], md=6),

          ]),

  dbc.Row([             
      dbc.Col([html.Label("Этаж", className="filter-label"), 
# Выпадающее меню "Этаж"            
          dcc.Dropdown(id="floor-ml-filter",
                       options=[{'label': sx, 'value': sx } for sx in ml1.sort_values(by='Этаж', ascending=True)['Этаж'].unique() if pd.notna(sx)],    
                        value=2,
                        multi=False,   
                        className="filter-dropdown", 
                        )
              ], md=6),

       dbc.Col([html.Label("Площадь (кв м)", className="filter-label"),  
# Фильтр Слайдер "Выбрать площадь квартиры (кв м)"             
           dcc.Slider(id="area-ml-filter",
                      min=10,
                      max=65,
                      marks={i: '{}'.format(i) for i in range(10,63,10)},
                      value=40,
                      )
                ], md=6),
         ]),


#информационная панель
        html.Div(id='stats-panel', className="stats-panel")

    ])



# установка кастомной палетки цветов для всех графиков plotly
pio.templates['custom'] = pio.templates['plotly'].update(
    layout=dict(colorway=st.MY_PALETTE)
)
pio.templates.default = "custom"


# Коллбэки

@callback(
    Output('stats-panel', 'children'),
    Input("district-ml-filter", "value"),
    Input("distance-metro-ml-filter", "value"),
    Input("type-ml-filter", "value"),
    Input("year-ml-filter", "value"),
    Input("floor-ml-filter", "value"),
    Input("area-ml-filter", "value"),
    Input("distance-center-ml-filter","value"),
    Input("number-rooms-ml-filter","value"),
#    Input("my_input","value")
 )

def update_graphs(district, distance, type, year, floor, area, center,room):


       X = ml.drop("Цена (млн руб)", axis=1) # наблюдения по признакам
       y = ml["Цена (млн руб)"] # метки


# выборка X_test1 нужна для последующего нахождения результата согласно данным, введенным пользователем
       X_train1, X_test1, y_train1, y_test1 = train_test_split(X, y, test_size=0.2, random_state=3) # разбиение на выборки тестовую и трейновую

       print("X_test1")
       print(X_test1)

       scaler = StandardScaler() # нормализация (приводим к единому масштабу значения)
       X = scaler.fit_transform(X)

       X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=3) # разбиение на выборки тестовую и трейновую

       poly = PolynomialFeatures(degree=3) # кодируем признаки с нелинейными связями
       X_train = poly.fit_transform(X_train)
       X_test = poly.transform(X_test)

       from sklearn.linear_model import Lasso, Ridge

       #model = LinearRegression()
       #model = Lasso(alpha=0.1)
       model = Ridge(alpha=0.7) # строим модель с L2-регуляризацией

       model.fit(X_train, y_train) # учим

       y_pred_train = model.predict(X_train) # предсказываем
       y_pred_test = model.predict(X_test)

       r2_train = r2_score(y_train, y_pred_train) # считаем метрики
       r2_test = r2_score(y_test, y_pred_test)
       mse_train = mean_squared_error(y_train, y_pred_train)
       mse_test = mean_squared_error(y_test, y_pred_test)
       rmse_train = np.sqrt(mse_train)
       rmse_test = np.sqrt(mse_test)
       mae_train = mean_absolute_error(y_train, y_pred_train)
       mae_test = mean_absolute_error(y_test, y_pred_test)

       print(f'R2 train: {r2_train}')
       print(f'R2 test: {r2_test}')
       print(f'MSE train: {mse_train}')
       print(f'MSE test: {mse_test}')
       print(f'RMSE train: {rmse_train}')
       print(f'RMSE test: {rmse_test}')
       print(f'MAE train: {mae_train}')
       print(f'MAE test: {mae_test}')

#      print(X_test1)
#       print("1 ",district)
#       print("2 ",distance) 
#       print("3 ",type)
#       print("4 ",year) 
#       print("5 ",floor) 
#       print("6 ",area)
#       print("7 ",center)
#       print("")
#       print("8 ",int(type_to_index(type)))

       
       example = {
                'Срок сдачи': [int(year)],
                'Этаж': [int(floor)],
                'Площадь': [float(area)],
                'До метро': [float(distance)],
                'До центра': [float(center)],
                'Количество комнат_int': room_to_index(room),
                'Метро_int': int(metro_to_index(district)),
                'Вид объекта_int': [int(type_to_index(type))]               
                }
       
    #   print(example)
    #   print("11 ",int(metro_to_index(district)))
    #   print("14 ",int(year)) 
    #   print("12 ",float(distance)) 
    #   print("13 ",int(type_to_index(type)))
    #   print("14 ",int(year)) 
   #    print("15 ",int(floor)) 
   #    print("16 ",float(area))
   #    print("17 ",float(center))

       print("example:")
       print(example)
       print(pd.DataFrame.from_dict(example))
       print(X_test1)

# добавляем список examle в датафрейм X_test1
       X_test1 = pd.concat([X_test1, pd.DataFrame(example)], ignore_index=True)
       X_test2 = scaler.fit_transform(X_test1)
       X_test2 = poly.transform(X_test2)
       result=model.predict(X_test2)[-1]
       result=float(result)

#       X_test1 =  X_test1.iloc[:-1]

# Панель с результатом

       stats_panel = dbc.Card([
            dbc.CardHeader("Стоимость квартиры:", className="stats-header"),
            dbc.CardBody([
                html.P(f"{result:.3f} (млн руб)")
            ])
      ])


       return stats_panel



    