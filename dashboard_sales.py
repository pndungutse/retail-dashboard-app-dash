# -*- coding: utf-8 -*-
"""
Created on Fri Jan  6 10:35:18 2023

@author: Patrick NDUNGUTSE
"""

import dash
import pandas as pd
import dash_html_components as html
import plotly.graph_objects as go
import dash_core_components as dcc
from dash.dependencies import Output, Input
import dash_bootstrap_components as dbc
import numpy as np

# read file
pd_2 = pd.read_csv("C:\\Users\\Patrick NDUNGUTSE\\Desktop\\Graduate Courses\\Certifications\\Planning\\Dash course\\Sales_dashboard\\retail.csv")
pd_2['Date'] = pd.to_datetime(pd_2['Date'], format='%Y-%m-%d')

# Total sales monthly level
monthly_sales_df = pd_2.groupby(['month', 'Month']).agg({'Weekly_Sales':'sum'}).reset_index()

################################ holiday sales month lvl #####################################
holiday_sales = pd_2[pd_2['IsHoliday'] == 1].groupby(['month'])['Weekly_Sales'].sum().reset_index().rename(columns={'Weekly_Sales':'Holiday_Sales'})

############################# combined #########################
monthly_sales_df  = pd.merge(holiday_sales,monthly_sales_df,on = 'month', how = 'right').fillna(0)

############################## rounding sales to 1 decimal but that is how they are, means is not necessary #############################
monthly_sales_df['Weekly_Sales'] = monthly_sales_df['Weekly_Sales'].round(1)
monthly_sales_df['Holiday_Sales'] = monthly_sales_df['Holiday_Sales'].round(1)

###################### weekly sales #########################
weekly_sale = pd_2.groupby(['month','Month','Date']).agg({'Weekly_Sales':'sum'}).reset_index()
weekly_sale['week_no'] = weekly_sale.groupby(['Month'])['Date'].rank(method='min')

########################### store level sales #######################
store_df=pd_2.groupby(['month','Month','Store']).agg({'Weekly_Sales':'sum'}).reset_index()
store_df['Store'] = store_df['Store'].apply(lambda x: 'Store'+" "+str(x))
store_df['Weekly_Sales'] = store_df['Weekly_Sales'].round(1)

######################## dept level sales #########################
dept_df=pd_2.groupby(['month','Month','Dept']).agg({'Weekly_Sales':'sum'}).reset_index()
dept_df['Dept'] = dept_df['Dept'].apply(lambda x: 'Dept'+" "+str(x))
dept_df['Weekly_Sales'] = dept_df['Weekly_Sales'].round(1)

app = dash.Dash(external_stylesheets=[dbc.themes.BOOTSTRAP])

app.title = 'Retail dashboard dash'
server = app.server

PLOTLY_LOGO = "https://images.plot.ly/logo/new-branding/plotly-logomark.png"

navbar = dbc.Navbar(id = 'navbar', children = [
    dbc.Container(
        [
            html.A(
                # Use row and col to control vertical alignment of logo / brand
                dbc.Row(
                    [
                        dbc.Col(html.Img(src=PLOTLY_LOGO, height="50px", className='mr-5', style={'marginRight':'25px'})),
                        dbc.Col(dbc.NavbarBrand("Retail Sales Dashboard", className="ms-2 ml-5", style={'color':'white', 'fontSize':'25px', 'fontWeight':'Times New Roman'})),
                    ],
                    align="center",
                    className="g-0",
                ),
                href="https://plotly.com",
                style={"textDecoration": "none"},
            ),
            dbc.NavbarToggler(id="navbar-toggler", n_clicks=0),
        ], fluid=True
    )],
    color="#090059",
    #dark=True,
)

card_content_dropdwn = [
    dbc.CardBody(
        [
            html.H6('Select Months', style = {'textAlign':'center'}),
            
            dbc.Row([
                
                dbc.Col([
                    
                    html.H6('Current Period'),
                    
                    dcc.Dropdown( id = 'dropdown_base',
        options = [
            {'label':i, 'value':i } for i in monthly_sales_df.sort_values('month')['Month']
        
            ],
        value = 'Feb',
        
        )
                    
                    
                    ]),
                
                dbc.Col([
                    
                    html.H6('Reference Period'),
                    
                    dcc.Dropdown( id = 'dropdown_comp',
        options = [
            {'label':i, 'value':i } for i in monthly_sales_df.sort_values('month')['Month']
        
            ],
        value = 'Jan',
        
        )
                    
                    
                    ]),
                
                
                
                
                ])
            
            ]
        )
    
    
    
    ]


body_app = dbc.Container([
    dbc.Row(id = 'row1', children=[navbar]),
    
    html.Br(),
    html.Br(),
    
    dbc.Row([
        dbc.Col([
            dbc.Card(card_content_dropdwn, style={'height':'150px'})
            ], width=4),
        
        dbc.Col([
            dbc.Card(id = 'card-num1', style={'height':'150px'})
            ]),
        
        dbc.Col([
            dbc.Card(id = 'card-num2', style={'height':'150px'})
            ]),
        
        dbc.Col([
            dbc.Card(id = 'card-num3', style={'height':'150px'})
            ]),
        ]),
    
    html.Br(),
    html.Br(),
    
    dbc.Row([        
        dbc.Col([
            dbc.Card(id = 'card-num-4', children = [
                dbc.CardBody(
                    [
                        html.H6('Weekly Sales Comparision', style={'fontWeight':'bold', 'textAlign':'center'}),
                        dcc.Graph(id='line-chart', figure = {}, style={'height':'250px'})
                        ]
                    )
                ], style={'height':'300px'})
            ]),
        
        dbc.Col([
            dbc.Card(id = 'bar-charts', style={'height':'300px'})
            ]),
        
        dbc.Col([
            dbc.Card(id = 'last-bar-charts', style={'height':'300px'})
            ]),
        ]),
    html.Br(),
    html.Br(),
    
    ], fluid=True)

app.layout = html.Div(id = 'parent', children = [body_app])

@app.callback([Output(component_id='card-num1', component_property='children'),
               Output(component_id='card-num2', component_property='children'),
               Output(component_id='card-num3', component_property='children'),
               Output(component_id='line-chart', component_property='figure'),
               Output(component_id='bar-charts', component_property='children'),
               Output(component_id='last-bar-charts', component_property='children'),
               ],
              [Input(component_id='dropdown_base', component_property='value'),
               Input(component_id='dropdown_comp', component_property='value')]
              )

def update_cards(base, comp):
    
    sales_base = monthly_sales_df.loc[monthly_sales_df['Month']==base].reset_index()['Weekly_Sales'][0]
    sales_comp = monthly_sales_df.loc[monthly_sales_df['Month']==comp].reset_index()['Weekly_Sales'][0]
    
    diff_sales = np.round(sales_base - sales_comp, 1)
    
    holiday_sales_base = monthly_sales_df.loc[monthly_sales_df['Month']==base].reset_index()['Holiday_Sales'][0]
    holiday_sales_comp = monthly_sales_df.loc[monthly_sales_df['Month']==comp].reset_index()['Holiday_Sales'][0]
    
    diff_holiday_sales = np.round(holiday_sales_base - holiday_sales_comp, 1)
    
    store_base_count = len(pd_2.loc[pd_2['Month']==base, 'Store'].unique())
    store_comp_count = len(pd_2.loc[pd_2['Month']==comp, 'Store'].unique())
    
    diff_store = np.round(store_base_count - store_comp_count, 1)
    
    if diff_sales>=0:
        sign = '+'
    else:
        sign = '-'
        
    if diff_holiday_sales>=0:
        sign = '+'
    else:
        sign = '-'
        
    if diff_store>=0:
        sign = '+'
    else:
        sign = '-'
        
    weekly_base = weekly_sale.loc[weekly_sale['Month'] == base].reset_index()
    weekly_comp = weekly_sale.loc[weekly_sale['Month'] == comp].reset_index()
    
    fig1 = go.Figure(data = [go.Scatter(x = weekly_base['week_no'], y = weekly_base['Weekly_Sales'],\
                                   line = dict(color = 'firebrick', width = 4),name = '{}'.format(base)),
                        go.Scatter(x = weekly_comp['week_no'], y = weekly_comp['Weekly_Sales'],\
                                   line = dict(color = '#090059', width = 4),name = '{}'.format(comp))])
                                                                                   
    fig1.update_layout(plot_bgcolor = 'white',
                      margin=dict(l = 40, r = 5, t = 60, b = 40),
                      yaxis_tickprefix = '$',
                      yaxis_ticksuffix = 'M')
    
    store_base = store_df.loc[store_df['Month']==base].sort_values('Weekly_Sales',ascending = False).reset_index()[:10]
    store_comp = store_df.loc[store_df['Month']==comp].sort_values('Weekly_Sales',ascending = False).reset_index()[:10]
    
    bar_fig1 = go.Figure([go.Bar(x = store_base['Weekly_Sales'], y = store_base['Store'], marker_color = 'indianred',name = '{}'.format(base),\
                             text = store_base['Weekly_Sales'], orientation = 'h',
                             textposition = 'outside'
                             ),
                 ])
        
        
    bar_fig2 = go.Figure([go.Bar(x = store_comp['Weekly_Sales'], y = store_comp['Store'], marker_color = '#4863A0',name = '{}'.format(comp),\
                             text = store_comp['Weekly_Sales'], orientation = 'h',
                             textposition = 'outside'
                             ),
                 ])
        
    bar_fig1.update_layout(plot_bgcolor = 'white',
                       xaxis = dict(range = [0,'{}'.format(store_base['Weekly_Sales'].max()+3)]),
                      margin=dict(l = 40, r = 5, t = 60, b = 40),
                      xaxis_tickprefix = '$',
                      xaxis_ticksuffix = 'M',
                      title = '{}'.format(base),
                      title_x = 0.5)
    
    bar_fig2.update_layout(plot_bgcolor = 'white',
                       xaxis = dict(range = [0,'{}'.format(store_comp['Weekly_Sales'].max()+3)]),
                      margin=dict(l = 40, r = 5, t = 60, b = 40),
                      xaxis_tickprefix = '$',
                      xaxis_ticksuffix = 'M',
                      title = '{}'.format(comp),
                      title_x = 0.5)
    
    dept_base = dept_df.loc[dept_df['Month']==base].sort_values('Weekly_Sales',ascending = False).reset_index()[:10]
    dept_base=dept_base.rename(columns = {'Weekly_Sales':'Weekly_Sales_base'})
    dept_comp = dept_df.loc[dept_df['Month']==comp].sort_values('Weekly_Sales',ascending = False).reset_index()
    dept_comp=dept_comp.rename(columns = {'Weekly_Sales':'Weekly_Sales_comp'})
    
    merged_df=pd.merge(dept_base, dept_comp, on = 'Dept', how = 'left')
    merged_df['diff'] = merged_df['Weekly_Sales_base']-merged_df['Weekly_Sales_comp']
    
    last_bar_fig4 = go.Figure([go.Bar(x = merged_df['diff'], y = merged_df['Dept'], marker_color = '#4863A0',\
                              orientation = 'h',
                             textposition = 'outside'
                             ),
                 ])
        
    last_bar_fig4.update_layout(plot_bgcolor = 'white',
                       margin=dict(l = 40, r = 5, t = 60, b = 40),
                      xaxis_tickprefix = '$',
                      xaxis_ticksuffix = 'M'
                     )
        
    card_content_sales = [
        
        dbc.CardBody(
            [
                html.H6('Total sales', style = {'fontWeight':'lighter', 'textAlign':'center'}),
                
                html.H3('{0}{1}{2}'.format("$", sales_base, "M"), style = {'color':'#090059','textAlign':'center'}),
                
                dcc.Markdown(dangerously_allow_html = True,
                             children = ["<sub>{0}{1}{2}{3}</sub>".format(sign, '$', np.absolute(diff_sales), 'M')], style = {'textAlign':'center'})
                ]
                   
            )  
        ]
    
    card_content_holiday_sales = [
        
        dbc.CardBody(
            [
                html.H6('Holiday sales', style = {'fontWeight':'lighter', 'textAlign':'center'}),
                
                html.H3('{0}{1}{2}'.format("$", holiday_sales_base, "M"), style = {'color':'#090059','textAlign':'center'}),
                
                dcc.Markdown(dangerously_allow_html = True,
                             children = ["<sub>{0}{1}{2}{3}</sub>".format(sign, '$', np.absolute(diff_holiday_sales), 'M')], style = {'textAlign':'center'})
                ]
                   
            )  
        ]
    
    card_contents_store = [
        
        dbc.CardBody(
            [
                html.H6('Total Stores', style = {'fontWeight':'lighter', 'textAlign':'center'}),
                
                html.H3('{0}'.format(store_base_count), style = {'color':'#090059','textAlign':'center'}),
                
                dcc.Markdown(dangerously_allow_html = True,
                             children = ["<sub>{0}{1}</sub>".format(sign, np.absolute(diff_store))], style = {'textAlign':'center'})
                ]
                   
            )  
        ]
    
    card_content_bar_graphs = [
        
        dbc.CardBody(
            [
                html.H6('Stores with highest Sales', style = {'fontWeight':'bold', 'textAlign':'center'}),
                
                dbc.Row([
                    dbc.Col([dcc.Graph(figure = bar_fig1, style = {'height':'250px'}),
                ], width=6),
                    dbc.Col([dcc.Graph(figure = bar_fig2, style = {'height':'250px'}),
                ], width=6)
                    
                    ]
                    )
                
                
                
                ]
                   
            )  
        ]
    
    card_content_last_bar_graph = [
        
        dbc.CardBody(
            [
                html.H6('Sales difference between Top departments ({} - {})'.format(base, comp), style = {'fontWeight':'bold', 'textAlign':'center'}),
                
                dcc.Graph(figure = last_bar_fig4, style = {'height':'250px'})
                
                
                ]
                   
            )  
        ]
    
    return card_content_sales, card_content_holiday_sales, card_contents_store, fig1, card_content_bar_graphs, card_content_last_bar_graph

if __name__=='__main__':
    app.run_server(debug=False) 
