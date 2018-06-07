#%% 
# standard library
import os

# dash libs
import dash
from dash.dependencies import Input, Output
import dash_core_components as dcc
import dash_html_components as html
import plotly.figure_factory as ff
import plotly.graph_objs as go

# pydata stack
import pandas as pd
from sqlalchemy import create_engine

# database stuff
import csv, sqlite3
from datetime import datetime
import numpy as np
#
###########################
# Data Manipulation / Model
###########################
#DataBase Generation
conn = sqlite3.connect(":memory:", check_same_thread=False)
cur = conn.cursor()
cur.execute("CREATE TABLE myData (Date,Title,Comment,MainCategory,Subcategory,Account,Amount);") # use your column names here

with open('data.csv','rb') as fin: # `with` statement available in 2.5+
    # csv.DictReader uses first line in file for column headings by default
    dr = csv.DictReader(fin) # comma is default delimiter
    to_db = [(i['Date'], i['Title'],i['Comment'], i['MainCategory'],i['Subcategory'], i['Account'],i['Amount']) for i in dr]

cur.executemany("INSERT INTO myData (Date, Title, Comment,MainCategory,Subcategory,Account,Amount) VALUES (?, ?,?,?,?,?,?);", to_db)
conn.commit()

def fetch_data(q):    
    result = pd.read_sql(
        sql=q,
        con=conn
    )
    return result


def getAccounts():
    '''Returns the list of accounts that are stored in the database'''

    getAccountQuery = 'SELECT DISTINCT Account FROM myData'
    accounts = fetch_data(getAccountQuery)
    accounts = list(accounts['Account'].sort_values(ascending=True))    
    accounts.append('All')
    accounts.sort()
    return accounts

def getCategories(account):
    '''Returns the list of categories that are stored in the database'''

    getCategoryQuery = 'SELECT DISTINCT MainCategory FROM myData WHERE Account=\'%s\'' % account
    cats = fetch_data(getCategoryQuery)
    cats = list(cats['MainCategory'].sort_values(ascending=True))    
    cats.append('All')
    cats.sort()
    return cats

def getYear(account):
    '''Returns the list of categories that are stored in the database'''
    
    getYearQuery = 'SELECT DISTINCT Date FROM myData WHERE Account=\'%s\'' % account    
    years = fetch_data(getYearQuery)
    yearList = []
    for date in years['Date']:
        dateParse = datetime.strptime(date, "%m/%d/%Y")
        yearList.append(dateParse.year)    
    yearUnique = np.unique(yearList)
    return yearUnique
    

#########################
# Dashboard Layout / View
#########################
# Functions
def onLoad_GetData():
    '''Actions to perform upon initial page load'''

    accountOptions = (
        [{'label': account, 'value': account}
         for account in getAccounts()]
    )
    return accountOptions

# Set up Dashboard and create layout
app = dash.Dash()

app.css.append_css({
    "external_url": "https://codepen.io/chriddyp/pen/bWLwgP.css"
})
        
app.css.append_css({
    "external_url": "https://code.getmdl.io/1.3.0/material.indigo-pink.min.css"
})

app.css.append_css({
    "external_url": "https://fonts.googleapis.com/icon?family=Material+Icons"
})


        
my_js_url = 'https://code.getmdl.io/1.3.0/material.min.js'
app.scripts.append_script({
    "external_url": my_js_url
})

app.layout = html.Div([
    # Links
    html.Link(href='myCSS.css', rel='stylesheet'),
    
    # Page Header
    html.Header([
        html.Div([
            html.H1('TITLE',className="mdl-layout__header-row"),            
        ]),
            
    ],className="mdl-layout__header"),

    # Page Main
    html.Main([
        # Page Content
        html.Div([
            #Partision of page
            html.Div([
                # Auto Population
                html.Div([
                    html.Div([
                        # Account Selection 
                        html.Div([
                            html.Div('Account Type', className='three columns'),
                            html.Div(dcc.Dropdown(id='accountSelector',options=onLoad_GetData(),className='nine columns')),
                        ],className='twelve columns'),                       
                        
                        #Category Selection
                        html.Div([
                            html.Div('Category Type', className='three columns'),
                            html.Div(dcc.Dropdown(id='categorySelector',className='nine columns')),
                        ],className='twelve columns'),                        
                    ],className='twelve columns'),
    
                    html.Div(['---------------------------------------------------------------']),

                    html.Div([
                        # Year Selection 
                        html.Div([
                            html.Div('Year', className='three columns'),
                            html.Div(dcc.Dropdown(id='yearSelector',className='nine columns')),
                        ],className='twelve columns'),
    
                        # Year Selection 
                        html.Div([
                            html.Div('Month', className='three columns'),
                            html.Div(dcc.Dropdown(id='monthSelector',className='nine columns')),
                        ],className='twelve columns'),
    
                        # Year Selection 
                        html.Div([
                            html.Div('Day', className='three columns'),
                            html.Div(dcc.Dropdown(id='daySelector',className='nine columns')),
                        ],className='twelve columns'),
                        
                                               
                                               
                    ],className='twelve columns'),               
                ],className="mdl-cell mdl-cell--2-col"),


                # List
                html.Div(['Table'],className="mdl-cell mdl-cell--4-col"),
                # Graphs
                html.Div(['Graph'],className="mdl-cell mdl-cell--6-col"),
            
            ],className="mdl-grid"),
                
        ],className='page-content')        
    ],className='mdl-layout__content')   
        
    
    ],className='mdl-layout mdl-js-layout mdl-layout--fixed-header')

#############################################
# Interaction Between Components / Controller
#############################################
# Load Categories in Dropdown
@app.callback(
    Output(component_id='categorySelector', component_property='options'),
    [
        Input(component_id='accountSelector', component_property='value')
    ]
)
def populateCategories(account):
    categories = getCategories(account)
    return [
        {'label': category, 'value': category}
        for category in categories
    ]

# Load Categories in Dropdown
@app.callback(
    Output(component_id='yearSelector', component_property='options'),
    [
        Input(component_id='accountSelector', component_property='value')
    ]
)
def populateYear(account):
    years = list(getYear(account))
    return [
        {'label': year, 'value': year}
        for year in years
    ]

# Load Categories in Dropdown
@app.callback(
    Output(component_id='monthSelector', component_property='options'),
    [
        Input(component_id='accountSelector', component_property='value')
    ]
)
def populateMonth(account):
    months = ['JAN', 'FEB', 'MAR', 'APR', 'MAY', 'JUN', 'JUL', 'AUG', 'SEP', 'OCT', 'NOV', 'DEC']
    return [
        {'label': month, 'value': month}
        for month in months
    ]
    
# Load Categories in Dropdown
@app.callback(
    Output(component_id='daySelector', component_property='options'),
    [
        Input(component_id='accountSelector', component_property='value')
    ]
)
def populateDay(account):
    dayCount = range(32)
    dayCount.pop(0)
    days = list(dayCount)
    return [
        {'label': day, 'value': day}
        for day in days
    ]


# start Flask server
if __name__ == '__main__':
    app.run_server(
        debug=True,
        host='0.0.0.0',
        port=8050
    )