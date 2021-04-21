import dash
from dash.dependencies import Input, Output
import dash_core_components as dcc
import dash_html_components as html
import yfinance as yf
import plotly.graph_objects as go

app = dash.Dash(__name__,
                external_stylesheets=['https://codepen.io/chriddyp/pen/bWLwgP.css'],
                meta_tags=[
                    {"name": "viewport",
                     'content': 'width=device-width, initial-scale=1.0, maximum-scale=1.2, minimum-scale=0.5,'}
                ])
app.title = 'Money Management Calculator'

symbol = []

app.layout = html.Div([
    html.Div([
        html.Div('Money Management / Trading Plan Calculator',
                 style={'textAlign': 'center',
                        'fontSize': 30}),
        html.Br(),
    ], className='row'),

    html.Div([
        html.Div([
            html.Label('Modal:'),
            dcc.Input(id='modal', type='number', value=10000000),
            html.Br(),
            html.Label('Resiko Per Transaksi:'),
            dcc.Input(id='risk', type='number', value=200000),
            html.Br(),
            html.Label('Risk reward ratio:'),
            dcc.Input(id='rrr', type='number', value=2),
            html.Br(),
            html.Label('Stop Loss (%):'),
            dcc.Input(id='SL', type='number', value=5),


            html.Br(),
            html.Br(),
            html.Label('Kode Emiten: '),
            dcc.Input(id='emiten', value='SIDO'),
            html.Label('Harga Beli: '),
            dcc.Input(id='harga_beli', value=750),
            html.Br(),
            html.Br(),
            html.Div(id='output-table')
        ], className='six columns'),

        html.Div([
            html.Div(id='output'),
            html.Div(id='output2')
        ], className='six columns'),
    ], className='row'),
], className='ten columns offset-by-one')

@app.callback(
    Output('output2', 'children'),
    [
        Input('emiten', 'value')
    ]
)
def update2(emiten):
    if len(emiten) == 4:
        info_emiten = yf.Ticker(emiten+'.jk')
        todays_data = info_emiten.history(period='2d')
        nama = info_emiten.info['longName']
        symbol = info_emiten.info['symbol']
        last = todays_data['Close'][1]
        yest = todays_data['Close'][0]

        hist = info_emiten.history(period='150d')
        open = hist['Open']
        high = hist['High']
        low = hist['Low']
        close = hist['Close']
        tanggal = hist.index

        change = (last - yest) / yest * 100
        app.Title = emiten + str(last)

        if change > 0:
            style = {
                'color': 'green'
            }
        elif change == 0:
            style = {
                'color': 'black'
            }
        elif change < 0:
            style = {
                'color': 'red'
            }

        fig = go.Figure(data=[go.Candlestick(x=tanggal,
                                             open=open,
                                             high=high,
                                             low=low,
                                             close=close)])

        fig.update_layout(xaxis_rangeslider_visible=False,
                          margin=dict(l=20, r=20, t=50, b=50),)
        fig.update_yaxes(fixedrange=True)

        return html.Div([
            html.Hr(),
            html.H5(nama + ' (' + symbol + ')'),
            html.H3([
                html.Strong(last),
                html.Span(' ' + str((last - yest)) + ' (' + str(round(change, 2)) + '%) ',
                          style=style)
            ]),

            dcc.Graph(id='candlestick-chart',
                      figure=fig,
                      config={'displayModeBar': False}
                      ),
        ])

@app.callback(
    Output('output', 'children'),
    [
        Input('modal', 'value'),
        Input('risk', 'value'),
        Input('rrr', 'value'),
        Input('SL', 'value'),
    ]
)
def update(modal, risk, rrr, SL):
    return html.Div([
        html.Hr(),
        html.P([
            html.Strong('Modal: '),
            html.Span('Rp. ' + f'{modal:,}')
        ]),
        html.P([
            html.Strong('Resiko per transaksi: '),
            html.Span('Rp. ' + f'{risk:,}' + ' / '),
            html.Strong(str(risk/modal*100) + '% '),
            html.Span('dari modal')
        ]),
        html.P([
            html.Strong('Risk Reward Ratio: '),
            html.Span('1/' + str(rrr)),
        ]),
        html.P([
            html.Strong('Stop Loss: '),
            html.Span(str(SL) + '%')
        ]),
        html.P([
            html.Strong('Target Taking Profit: '),
            html.Span(str(SL*rrr) + '%')
        ]),
        html.P([
            html.Strong('Maksimal pembelian: '),
            html.Span('Rp. ' + f'{round(risk/(SL/100)):,}')
        ])
    ])

@app.callback(
    Output('output-table', 'children'),
    [
        Input('harga_beli', 'value'),
        Input('emiten', 'value'),
        Input('risk', 'value'),
        Input('rrr', 'value'),
        Input('SL', 'value'),
    ]
)
def update_table(harga_beli, emiten, risk, rrr, SL):
    jumlah_lot = (risk // (SL / 100)) // harga_beli / 100
    nominal = round(jumlah_lot) * int(harga_beli) * 100
    stop_loss = round(int(harga_beli) * (1 - SL / 100))
    taking_profit = int(harga_beli) * (1 + (SL * rrr) / 100)

    return html.Div([
            html.Tr([
                html.Th('Saham'),
                html.Th('Harga Beli'),
                html.Th('Jumlah Lot'),
                html.Th('Nominal'),
                html.Th('Stop Loss'),
                html.Th('Taking Profit'),
            ]),
            html.Tr([
                html.Td(emiten),
                html.Td(harga_beli),
                html.Td(round(jumlah_lot)),
                html.Td(nominal),
                html.Td(stop_loss),
                html.Td(round(taking_profit)),

            ])
        ])



if __name__ == '__main__':
    app.run_server(debug=True)
