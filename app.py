from dash import html, dcc, Input, Output 
import dash_bootstrap_components as dbc 
import plotly.express as px 
import plotly.graph_objects as go 
import pandas as pd 
from dash_bootstrap_templates import ThemeSwitchAIO 
import dash 

FONT_AWESOME = ['https://use.fontawesome.com/releases/v5.10.2/css/all.css']

app = dash.Dash(__name__, external_stylesheets=FONT_AWESOME)
app.scripts.config.serve_locally = True 
server = app.server 

# ================== styles ================= #

tab_card = {'height' : "100%"}

main_config = { 
    'hovermode' : 'x unified', 
    'legend' : {
        "yanchor" : "top", 
        "y": 0.9, 
        'xanchor' : "left", 
        "x": 0.1, 
        'title' : {"text" : None}, 
        'font' : {'color' : 'white'}, 
        'margin' : {'l':10, 'r':10, 't': 10, 'b':10}
    }
}

config_graph = {'displayModeBar' : False, 'showTips' : False}

template_theme1 = 'flatly'
template_theme2 = 'darkly'
url_theme1 = dbc.themes.FLATLY
url_theme2 = dbc.themes.DARKLY 


# ================== reading dataset  ================= #

df = pd.read_csv("dataset_asimov.csv")
df_cru = df.copy()

# ================== transform dataset ================= #

df.loc[ df['Mês'] == 'Jan', 'Mês'] = "1"
df.loc[ df['Mês'] == 'Fev', 'Mês'] = "2"
df.loc[ df['Mês'] == 'Mar', 'Mês'] = "3"
df.loc[ df['Mês'] == 'Abr', 'Mês'] = "4"
df.loc[ df['Mês'] == 'Mai', 'Mês'] = "5"
df.loc[ df['Mês'] == 'Jun', 'Mês'] = "6"
df.loc[ df['Mês'] == 'Jul', 'Mês'] = "7"
df.loc[ df['Mês'] == 'Ago', 'Mês'] = "8"
df.loc[ df['Mês'] == 'Set', 'Mês'] = "9"
df.loc[ df['Mês'] == 'Out', 'Mês'] = "10"
df.loc[ df['Mês'] == 'Nov', 'Mês'] = "11"
df.loc[ df['Mês'] == 'Dez', 'Mês'] = "12"

df['Chamadas Realizadas'] = df['Chamadas Realizadas'].astype(int)
df['Dia'] = df['Dia'].astype(int)
df['Mês'] = df['Mês'].astype(int)

df['Valor Pago'] = df['Valor Pago'].str.lstrip('R$ ')
df['Valor Pago'] = df['Valor Pago'].astype(int)

df.loc[df['Status de Pagamento'] == 'Pago', 'Status de Pagamento'] = "1"
df.loc[df['Status de Pagamento'] == 'Não pago', 'Status de Pagamento'] = "0"
df['Status de Pagamento'] = df['Status de Pagamento'].astype(int)


options_month = [{'label' : 'Ano Todo', 'value' : 0}]
for i, j in zip(df_cru['Mês'].unique(), df['Mês'].unique()): 
    options_month.append({'label' : i, 'value' : int(j)})

options_month = sorted(options_month, key = lambda x: x['value'])


options_team = [{'label' : 'Todas as Equipes', 'value' : 0}]
for i in df['Equipe'].unique():
    options_team.append({'label' : i, 'value' : i})


def month_filter(month): 
    if month == 0: 
        mask = df['Mês'].isin(df['Mês'].unique())
    else: 
        mask = df['Mês'].isin([month])
    return mask 

def team_filter(equipe): 
    if equipe == 0: 
        mask = df['Equipe'].isin(df['Equipe'].unique())
    else: 
        mask = df['Equipe'].isin([equipe])
    return mask 


def convert_to_text(month):
    lista1 = ['Ano Todo', 'Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 
              'Junho', 'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro']
    return lista1[month]

# ================== layout ================= #

app.layout = dbc.Container(
    children=[
        ## row 1 
        dbc.Row([
            #coluna 1 da primeira linha
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        dbc.Row([
                            dbc.Col([
                                html.Legend("Sales Analytics")
                            ], sm=8), 
                            dbc.Col([
                                html.I(className='fa fa-balance-scale', style={"font-size" : '300%'})
                            ], sm=4, align='center')
                        ]),
                        dbc.Row([
                            dbc.Col([
                                ThemeSwitchAIO(aio_id='theme', themes=[url_theme1, url_theme2]),
                                html.Legend('Creator: Luiz Reis')
                            ])
                        ], style = {'margin-top' : '10px'}), 
                        dbc.Row([
                            dbc.Button('Visite o Site', href='https://asimov.academy/', target='_b1')
                        ], style={'margin-top': "10px"})
                    
                    ])
                ], style=tab_card)
            ],sm = 4, lg=2), 

            #coluna 2 da primeira linha será um card com dois filtros

            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        dbc.Row(
                            dbc.Col([
                                html.H5("Escolha o Mês"), 
                                dbc.RadioItems(
                                    id='radio-month', 
                                    options = options_month, 
                                    value = 0, 
                                    inline = True, 
                                    labelCheckedClassName = 'text-success', 
                                    inputCheckedClassName = 'border border-success bg-success',
                                ), 
                                html.Div(id='month-select', style = {'text-align' : 'center', 'margin-top' : "7px"})
                            ])
                        ), 

                        dbc.Row([
                            dbc.Col([
                                html.H5("Escolha a Equipe"), 
                                dbc.RadioItems(
                                    id='radio-team', 
                                    options = options_team, 
                                    value = 0, 
                                    inline = True, 
                                    labelCheckedClassName = 'text-warning', 
                                    inputCheckedClassName = 'border border-warning bg-warning',
                                ), 
                                html.Div(id='team-select', style = {'text-align' : 'center', 'margin-top' : "30px"})
                            ])
                        ])
                    ])
                ], style = tab_card)
            ], sm=12, lg = 3),


            #coluna 3 da primeira linha será um card com dois gráficos
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        dbc.Row(
                            dbc.Col(
                            html.Legend("Big Numbers")
                            )
                        ), 
                        dbc.Row([
                            dbc.Col([
                                dcc.Graph(id='graph1', className='dbc', config=config_graph)
                            ], sm=12, md=4), 
                            dbc.Col([
                                dcc.Graph(id='graph2', className='dbc', config=config_graph)
                            ],sm=12, md=4), 
                            dbc.Col([
                                dcc.Graph(id='graph3', className='dbc', config=config_graph)
                            ],sm=12, md=4)
                        ])
                    ])
                ], style=tab_card)
            ], sm=12, lg=7)
        ], class_name='g-2 my-auto', style={'margin-top': '7px'}),


        dbc.Row([
            #coluna 1 da segunda linha, com 2 gráficos
            dbc.Col([
                dbc.Row([
                    dbc.Col([
                        dbc.Card([
                            dbc.CardBody([
                                    dbc.Row(
                                        dbc.Col(
                                            html.Legend("Total Chamadas")
                                    ) 
                                ), 
                                dbc.Row(
                                    dcc.Graph(id='graph4', className='dbc', config=config_graph)
                                )
                            ])
                        ], style=tab_card)
                    ])
                ]),

                dbc.Row([
                    dbc.Col([
                        dbc.Card([
                            dbc.CardBody([
                                dcc.Graph(id='graph5', className='dbc', config=config_graph)
                            ])
                        ], style=tab_card)
                    ])
                ], class_name='g-2 my-auto', style={'margin-top': '7px'})

            ], sm=12, lg=4),

            dbc.Col([
                dbc.Row([
                    dbc.Col([
                        dbc.Card([
                            dbc.CardBody([
                                    dbc.Row(
                                        dbc.Col(
                                            html.Legend("Equipes")
                                    ) 
                                ), 
                                dbc.Row([
                                    dbc.Col([
                                        dcc.Graph(id='graph6', className='dbc', config=config_graph)
                                    ], sm=6), 
                                    dbc.Col([
                                        dcc.Graph(id='graph7', className='dbc', config=config_graph)
                                    ], sm=6)
                                ])
                            ])
                        ], style=tab_card)
                    ])
                ]),

                dbc.Row([
                     dbc.Col([
                         dbc.Card([
                             dbc.CardBody([
                                 dcc.Graph(id='graph8', className='dbc', config=config_graph)
                             ])
                         ])
                     ])
                 ], class_name='g-2 my-auto', style={'margin-top': '7px'})
            ], sm=12, lg=4),

            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        dbc.Row(
                            dcc.Graph(id='graph9', className='dbc', config=config_graph)
                        )
                    ])
                ],style=tab_card)
            ],sm=12, lg=4) 

        ], class_name='g-2 my-auto', style={'margin-top': '7px'}),


        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                            dbc.Row(
                                html.Legend("Distribuição de Propaganda")
                            ),
                            dcc.Graph(id='graph10', className='dbc', config=config_graph)
                    ])
                ], style = tab_card)
            ], sm=4),

            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                            dbc.Row(
                                html.Legend("Valores de Propaganda Convertidos")
                            ),
                            dcc.Graph(id='graph11', className='dbc', config=config_graph)
                    ])
                ], style = tab_card)
            ], sm=4), 

            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                            dcc.Graph(id='graph12', className='dbc', config=config_graph)
                    ])
                ], style = tab_card)
            ], sm=4)             
    ], class_name='g-2 my-auto', style={'margin-top': '7px'}),

], fluid=True, style={"height" : "100vh"})

# ================== callbacks ================= #

@app.callback(
    Output(component_id='graph1', component_property='figure'),
    Output(component_id='graph2', component_property='figure'),
    Output(component_id='month-select', component_property='children'),
    Output(component_id='team-select', component_property='children'),
    Input(component_id='radio-month', component_property='value'), 
    Input(component_id='radio-team', component_property='value'), 
    Input(component_id=ThemeSwitchAIO.ids.switch('theme'), component_property='value')
)

def graphs_first_row(month, team, theme): 
    template = template_theme1 if theme else template_theme2

    month_mask = month_filter(month)
    team_mask = team_filter(team)
    df_filtrado_full = df.loc[month_mask].loc[team_mask]

    df_consultor = df_filtrado_full.groupby(['Consultor', 'Equipe'])['Valor Pago'].sum()
    df_consultor.sort_values(ascending=False, inplace=True)
    df_consultor = df_consultor.reset_index()
    
    df_equipe = df_filtrado_full.groupby('Equipe')['Valor Pago'].sum()
    df_equipe.sort_values(ascending=False, inplace=True)
    df_equipe = df_equipe.reset_index()

    fig_graph1 = go.Figure()
    fig_graph2 = go.Figure()

    fig_graph1.add_trace(go.Indicator(mode='number',
            title = {"text": f"<span style='font-size:150%'>Valor Total</span><br><span style='font-size:70%'>Em Reais</span><br>"},
            value = df_filtrado_full['Valor Pago'].sum(),
            number = {'prefix': "R$"}
    ))

    fig_graph2.add_trace(go.Indicator(mode='number+delta',
            title = {"text": f"<span style='font-size:150%'>{df_consultor['Consultor'].iloc[0]} - Top Consultant</span><br><span style='font-size:70%'>Em vendas - em relação a média</span><br>"},
            value = df_consultor['Valor Pago'].iloc[0],
            number = {'prefix': "R$"},
            delta = {'relative': True, 'valueformat': '.1%', 'reference': df_consultor['Valor Pago'].mean()}
    ))

    fig_graph1.update_layout(height=300, template = template)
    fig_graph2.update_layout(height=300, template = template)

    select_month = html.H1(convert_to_text(month))
    select_team = html.H1('Todas as Equipes') if team == 0 else html.H1(team)

    return fig_graph1, fig_graph2, select_month, select_team


@app.callback(
    Output(component_id='graph3', component_property='figure'),
    Input(component_id='radio-month', component_property='value'), 
    Input(component_id=ThemeSwitchAIO.ids.switch('theme'), component_property='value')
)

def graphs_first_row(month, theme): 
    template = template_theme1 if theme else template_theme2

    month_mask = month_filter(month)
    df_filtrado_full = df.loc[month_mask]

    df_equipe = df_filtrado_full.groupby('Equipe')['Valor Pago'].sum()
    df_equipe.sort_values(ascending=False, inplace=True)
    df_equipe = df_equipe.reset_index()

    fig_graph3 = go.Figure()

    fig_graph3.add_trace(go.Indicator(mode='number+delta',
            title = {"text": f"<span style='font-size:150%'>{df_equipe['Equipe'].iloc[0]} - Top Team</span><br><span style='font-size:70%'>Em vendas - em relação a média</span><br>"},
            value = df_equipe['Valor Pago'].iloc[0],
            number = {'prefix': "R$"},
            delta = {'relative': True, 'valueformat': '.1%', 'reference': df_equipe['Valor Pago'].mean()}
    ))

    fig_graph3.update_layout(height=300, template = template)

    return fig_graph3

# ============================================================================== #
@app.callback(
    Output(component_id='graph4', component_property='figure'),
    Output(component_id='graph5', component_property='figure'),
    Input(component_id='radio-month', component_property='value'), 
    Input(component_id='radio-team', component_property='value'), 
    Input(component_id=ThemeSwitchAIO.ids.switch('theme'), component_property='value')
)

def graphs_first_row(month, team, theme): 
    template = template_theme1 if theme else template_theme2

    month_mask = month_filter(month)
    team_mask = team_filter(team)
    df_filtrado_full = df.loc[month_mask].loc[team_mask]
    df_dia = df_filtrado_full.groupby('Dia')['Chamadas Realizadas'].sum().reset_index()
    df_mes = df_filtrado_full.groupby('Mês')['Chamadas Realizadas'].sum().reset_index()

    fig_graph4 = go.Figure()
    fig_graph5 = go.Figure()

    fig_graph4 = go.Figure(go.Bar(x=df_dia['Dia'], y=df_dia['Chamadas Realizadas'], text=df_dia['Chamadas Realizadas'],textposition='auto',marker_color='#506784'))
    fig_graph5 = go.Figure(go.Bar(x=df_mes['Mês'], y=df_mes['Chamadas Realizadas'],text=df_mes['Chamadas Realizadas'],textposition='auto',marker_color='#506784'))

    fig_graph4.update_layout(height=450, template = template, xaxis_title="Dia", yaxis_title="Chamadas", xaxis=dict(dtick=1))
    fig_graph5.update_layout(height=450, template = template, xaxis_title="Mês", yaxis_title="Chamadas", xaxis=dict(dtick=1))
    
    return fig_graph4, fig_graph5


# ============================================================================== #
@app.callback(
    Output(component_id='graph6', component_property='figure'),
    Input(component_id='radio-month', component_property='value'), 
    Input(component_id=ThemeSwitchAIO.ids.switch('theme'), component_property='value')
)

def graphs_first_row(month, theme): 
    template = template_theme1 if theme else template_theme2

    month_mask = month_filter(month)
    df_filtrado_full = df.loc[month_mask]
    df_equipe_valor = df_filtrado_full.groupby('Equipe')['Valor Pago'].sum().reset_index()

    fig_graph6 = go.Figure()

    fig_graph6.add_trace(go.Pie(labels=df_equipe_valor['Equipe'].unique(), values=df_equipe_valor['Valor Pago'], hole=.6))

    fig_graph6.update_layout(height=450, template = template)
    
    return fig_graph6 


# ============================================================================== #
@app.callback(
    Output(component_id='graph7', component_property='figure'),
    Output(component_id='graph8', component_property='figure'),
    Input(component_id='radio-month', component_property='value'), 
    Input(component_id='radio-team', component_property='value'), 
    Input(component_id=ThemeSwitchAIO.ids.switch('theme'), component_property='value')
)

def graphs_first_row(month, team, theme): 
    template = template_theme1 if theme else template_theme2

    month_mask = month_filter(month)
    team_mask = team_filter(team)
    df_filtrado_full = df.loc[month_mask].loc[team_mask]

    df_chamadas_equipe = df_filtrado_full.groupby('Equipe')['Chamadas Realizadas'].sum().reset_index()
    
    df_equipe_line = df_filtrado_full.groupby(['Mês', 'Equipe'])['Valor Pago'].sum().reset_index()
    df_equipe_group = df_equipe_line.groupby('Mês')['Valor Pago'].sum().reset_index()

    fig_graph7 = go.Figure()
    fig_graph8 = px.line(df_equipe_line, y="Valor Pago", x="Mês", color="Equipe")

    fig_graph7.add_trace(go.Bar(x = df_chamadas_equipe['Chamadas Realizadas'],y = df_chamadas_equipe['Equipe'], orientation='h', text=df_chamadas_equipe['Chamadas Realizadas']))
    fig_graph8.add_trace(go.Scatter(y=df_equipe_group["Valor Pago"], x=df_equipe_group["Mês"], mode='lines+markers', fill='tonexty', fillcolor='rgba(255, 0, 0, 0.2)', name='Total de Vendas'))

    fig_graph7.update_layout(height=450, template = template)
    fig_graph8.update_layout(height=450, template = template)
    
    return fig_graph7, fig_graph8

# ============================================================================== #
@app.callback(
    Output(component_id='graph9', component_property='figure'),
    Input(component_id='radio-month', component_property='value'), 
    Input(component_id=ThemeSwitchAIO.ids.switch('theme'), component_property='value')
)

def graphs_first_row(month, theme): 
    template = template_theme1 if theme else template_theme2

    month_mask = month_filter(month)
    df_filtrado_full = df.loc[month_mask]
    df_equipe = df_filtrado_full.groupby('Equipe')['Valor Pago'].sum().reset_index()

    fig_graph9 = go.Figure(go.Bar(x = df_equipe['Valor Pago'],y = df_equipe['Equipe'], orientation='h', text=df_equipe['Valor Pago']))

    fig_graph9.update_layout(height=450, template = template)
    
    return fig_graph9

# ============================================================================== #
@app.callback(
    Output(component_id='graph10', component_property='figure'),
    Input(component_id='radio-month', component_property='value'), 
    Input(component_id='radio-team', component_property='value'), 
    Input(component_id=ThemeSwitchAIO.ids.switch('theme'), component_property='value')
)

def graphs_first_row(month, team, theme): 
    template = template_theme1 if theme else template_theme2

    month_mask = month_filter(month)
    team_mask = team_filter(team)
    df_filtrado_full = df.loc[month_mask].loc[team_mask]
    df_propaganda = df_filtrado_full.groupby(['Meio de Propaganda'])['Valor Pago'].sum().reset_index()

    fig_graph10 = go.Figure()
    fig_graph10.add_trace(go.Pie(labels=df_propaganda['Meio de Propaganda'], values=df_propaganda['Valor Pago'], hole=.7))

    fig_graph10.update_layout(height=450, template = template)
    
    return fig_graph10

# ============================================================================== #
@app.callback(
    Output(component_id='graph11', component_property='figure'),
    Input(component_id='radio-month', component_property='value'), 
    Input(component_id='radio-team', component_property='value'), 
    Input(component_id=ThemeSwitchAIO.ids.switch('theme'), component_property='value')
)

def graphs_first_row(month, team, theme): 
    template = template_theme1 if theme else template_theme2

    month_mask = month_filter(month)
    team_mask = team_filter(team)
    df_filtrado_full = df.loc[month_mask].loc[team_mask]
    df_propaganda = df_filtrado_full.groupby(['Meio de Propaganda', 'Mês'])['Valor Pago'].sum().reset_index()

    fig_graph11 = px.line(df_propaganda, y="Valor Pago", x="Mês", color="Meio de Propaganda")

    fig_graph11.update_layout(height=450, template = template)
    
    return fig_graph11 

# ============================================================================== #
@app.callback(
    Output(component_id='graph12', component_property='figure'),
    Input(component_id='radio-month', component_property='value'), 
    Input(component_id='radio-team', component_property='value'), 
    Input(component_id=ThemeSwitchAIO.ids.switch('theme'), component_property='value')
)

def graphs_first_row(month, team, theme): 
    template = template_theme1 if theme else template_theme2

    month_mask = month_filter(month)
    team_mask = team_filter(team)
    df_filtrado_full = df.loc[month_mask].loc[team_mask]
    df_status = df_filtrado_full.groupby('Status de Pagamento')['Chamadas Realizadas'].sum()

    fig_graph12 = go.Figure()

    fig_graph12.add_trace(go.Pie(labels=['Não Pago', 'Pago'], values=df_status, hole=.6))

    fig_graph12.update_layout(height=450, template = template)
    
    return fig_graph12 

# ================== run server ================= #
if __name__ == '__main__': 
    app.run(debug=True)