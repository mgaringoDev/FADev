#%%
# Separation of Debit and Credit or Expense and Income
#%% 
# standard library
import os

# dash libs
import dash
from dash.dependencies import Input, Output
import dash_core_components as dcc
import dash_html_components as html
import dash_table_experiments as dt
import plotly.plotly as py
import plotly.figure_factory as ff
import plotly.graph_objs as go

# pydata stack
import pandas as pd
from sqlalchemy import create_engine

# database stuff
import csv, sqlite3
from datetime import datetime
import numpy as np
import unicodedata
#%%
###########################
# Data Manipulation / Model
###########################
#DataBase Generation
conn = sqlite3.connect(":memory:", check_same_thread=False)
cur = conn.cursor()
cur.execute("CREATE TABLE myData (Date,Title,Comment,MainCategory,Subcategory,Account,Amount,Balance);") # use your column names here

with open('TogetherProgrammed.csv','rb') as fin: # `with` statement available in 2.5+
    # csv.DictReader uses first line in file for column headings by default
    dr = csv.DictReader(fin) # comma is default delimiter
    to_db = [(i['Date'], i['Title'],i['Comment'], i['MainCategory'],i['Subcategory'], i['Account'],i['Amount'],i['Balance']) for i in dr]

cur.executemany("INSERT INTO myData (Date, Title, Comment,MainCategory,Subcategory,Account,Amount,Balance) VALUES (?,?,?,?,?,?,?,?);", to_db)
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
    
#    getYearQuery = 'SELECT DISTINCT Date FROM myData WHERE Account=\'%s\'' % account        
#    getYearQuery = 'SELECT Date FROM myData WHERE CAST(SUBSTR(Date,7,4) as integer)=2014'
    getYearQuery = 'SELECT SUBSTR(Date,7,4) FROM myData'
    yearList = fetch_data(getYearQuery)   
    yearUnique = np.unique(yearList)
    return yearUnique

def getTransactionResults(account,category,year):    
    if account == 'All':
#        getTransactionQuery = 'SELECT Date,Title,MainCategory,Account,Amount,Balance FROM myData WHERE SUBSTR(Date,7,4)=\'%s\'' % (year)
        getTransactionQuery = 'SELECT * FROM myData WHERE SUBSTR(Date,7,4)=\'%s\'' % (year)
    else:            
        if category=='All':
#            getTransactionQuery = 'SELECT Date,Title,MainCategory,Account,Amount,Balance FROM myData WHERE SUBSTR(Date,7,4)=\'%s\' AND Account=\'%s\'' % (year, account)
            getTransactionQuery = 'SELECT * FROM myData WHERE SUBSTR(Date,7,4)=\'%s\' AND Account=\'%s\'' % (year, account)
        else:
#            getTransactionQuery = 'SELECT Date,Title,MainCategory,Account,Amount,Balance FROM myData WHERE SUBSTR(Date,7,4)=\'%s\' AND Account=\'%s\' AND MainCategory=\'%s\'' % (year, account,category)
            getTransactionQuery = 'SELECT * FROM myData WHERE SUBSTR(Date,7,4)=\'%s\' AND Account=\'%s\' AND MainCategory=\'%s\'' % (year, account,category)
            
    transactions = fetch_data(getTransactionQuery)    
        
    return transactions    
    
def drawLineGraph(transactions,category,account,year):
    #Yearly Calculations
    months = ['JAN', 'FEB', 'MAR', 'APR', 'MAY', 'JUN', 'JUL', 'AUG', 'SEP', 'OCT', 'NOV', 'DEC'] 
    
    if (account == 'All'):
        #% if statement start--------------------------------------------------------------------------
        #Get unique accounts
        uniqueAccounts = transactions.Account.unique().astype(str)
        
        #Generate a list of data points for each of the unique accounts
        dataPointsList = []
        creditList = []
        debitList = []
        
        #Obtain the current monthly balances for each of the unique accounts
        for accountName in uniqueAccounts:
            accountTransaction = getTransactionResults(accountName,category,year)
            # Create empty array filled with zeroes for each of the months
            dataPoints = []
            creditPoint = []
            debitPoints = []
            
            for i in xrange(12):
                dataPoints.append(0)
                creditPoint.append(0)
                debitPoints.append(0)
            
            #Create the unique monthly balances for each of the accounts
            numberOfTransactions = np.shape(accountTransaction)[0]    
            for transactionNumber in xrange(numberOfTransactions):        
                monthIndex = int(str(accountTransaction['Date'][transactionNumber]).split('/')[0]) -1
                dataPoints[monthIndex] = float(accountTransaction['Balance'][transactionNumber])
                
                if(accountTransaction['Subcategory'][transactionNumber]=="Debit"):
                    debitPoints[monthIndex] += float(accountTransaction['Amount'][transactionNumber])
                
                if(accountTransaction['Subcategory'][transactionNumber]=="Credit"):
                    creditPoint[monthIndex] += float(accountTransaction['Amount'][transactionNumber])
            
            creditList.append(creditPoint)
            debitList.append(debitPoints)
            dataPointsList.append(dataPoints)
        
        # Generate entire net worth
        EntireBalance = []
        EntireCredit = []
        EntireDebit = []        
        
        for i in xrange(12):
                EntireBalance.append(0)
                EntireCredit.append(0)
                EntireDebit.append(0)                
                
        for accountSummary in dataPointsList:
            for monthIndex in xrange(len(accountSummary)):
                EntireBalance[monthIndex] = EntireBalance[monthIndex] + accountSummary[monthIndex]
        
        # Generate the credit debit division
        for accountSummary in creditList:
            for monthIndex in xrange(len(accountSummary)):
                EntireCredit[monthIndex] = EntireCredit[monthIndex] + accountSummary[monthIndex]
        
        for accountSummary in debitList:
            for monthIndex in xrange(len(accountSummary)):
                EntireDebit[monthIndex] = EntireDebit[monthIndex] + accountSummary[monthIndex]
        
        
        #Draw the scatter plot
        figureList = []
        
        for accountIndex in xrange(len(uniqueAccounts)):  
            figureList.append(go.Scatter(x=months, y=dataPointsList[accountIndex], mode='lines+markers',name=uniqueAccounts[accountIndex]))
        
        figureList.append(go.Scatter(x=months, y=EntireBalance, mode='lines+markers',name='Net Worth'))
        figureList.append(go.Scatter(x=months, y=EntireCredit, mode='lines+markers',name='Expenses'))
        figureList.append(go.Scatter(x=months, y=EntireDebit, mode='lines+markers',name='Income'))
        
        
        figure = go.Figure(
            data=figureList,
            layout=go.Layout(
                title='History Scatter Plot',
                showlegend=True
            )
        )           
        #% if statement end----------------------------------------------------------------------------                        
    else:       
        #% else statement start------------------------------------------------------------------------                
        # Create empty array filled with zeroes for each of the months
        dataPoints = []
        for i in xrange(12):
            dataPoints.append(0)
        
        #Create the unique monthly balances
        numberOfTransactions = np.shape(transactions)[0]    
        for transactionNumber in xrange(numberOfTransactions):
    #        print(transactionNumber)        
            monthIndex = int(str(transactions['Date'][transactionNumber]).split('/')[0]) -1
            dataPoints[monthIndex] = float(transactions['Balance'][transactionNumber])                
        
        #Draw the scatter plot
        figure = go.Figure(
            data=[
                go.Scatter(x=months, y=dataPoints, mode='lines+markers',name='End Of Month Balance')
            ],
            layout=go.Layout(
                title='History Scatter Plot',
                showlegend=True
            )
        )
        #% else statement end-------------------------------------------------------------------------

    return figure

def drawPieGraphExpenses(transactions):
    
    transactions['Amount'] = transactions['Amount'].apply(pd.to_numeric)
    categorySum = transactions.groupby(['MainCategory']).sum()
    categorySumList = np.abs(categorySum['Amount'])
    categorySumList = categorySumList.tolist()
    print(categorySumList)
    
    categoryList = np.unique(transactions['MainCategory'].astype(str))
    categoryList = categoryList.tolist()    
    print(categoryList)
    
    
    #-------------------------------------------------------------------------
#    http://pycopy.com/plotly-a-pack-of-donuts/
#    uniqueSubCategory = transactions.Subcategory.unique().astype(str)
#    labels = ['Oxygen','Hydrogen','Carbon_Dioxide','Nitrogen']
#    values = [4500,2500,1053,500]
#    
#    numFig = 2;
#    dom_x = float(0)
#    tmp = float(numFig)
#    dom_dx = round(float(1/tmp),2)
#    
#    traces =[]
#    annotation = []
#    
#    for fig in xrange(numFig):
#        trace = go.Pie(labels=labels, values=values)
#        traces.append(trace)
#        anno = dict(showarrow=False, x=dom_x + (dom_dx/2), y=0.5, xanchor="center")
#        annotation.append(anno)
#        dom_x = dom_x + dom_dx
#     
#    layout = go.Layout(annotations=annotation)
        
        
#    figData = []
#    figData.append()
#    figData.append(go.Pie(labels=categoryList, values=categorySumList))
#    figData.append(go.Pie(labels=labels, values=values))
    
#    anno = dict(title='History Scatter Plot',showlegend=True,autosize = False,)
    #-------------------------------------------------------------------------
    figure = go.Figure(
        data=[
             go.Pie(labels=categoryList, values=categorySumList)           
        ],
        layout=go.Layout(
            title='Expense Categories',
            showlegend=True
        )
    )

    return figure

def drawPieGraphIncome(transactions):
    
    transactions['Amount'] = transactions['Amount'].apply(pd.to_numeric)
    categorySum = transactions.groupby(['MainCategory']).sum()
    categorySumList = np.abs(categorySum['Amount'])
    categorySumList = categorySumList.tolist()
    print(categorySumList)
    
    categoryList = np.unique(transactions['MainCategory'].astype(str))
    categoryList = categoryList.tolist()    
    print(categoryList)
    
    
    #-------------------------------------------------------------------------
#    http://pycopy.com/plotly-a-pack-of-donuts/
#    uniqueSubCategory = transactions.Subcategory.unique().astype(str)
#    labels = ['Oxygen','Hydrogen','Carbon_Dioxide','Nitrogen']
#    values = [4500,2500,1053,500]
#    
#    numFig = 2;
#    dom_x = float(0)
#    tmp = float(numFig)
#    dom_dx = round(float(1/tmp),2)
#    
#    traces =[]
#    annotation = []
#    
#    for fig in xrange(numFig):
#        trace = go.Pie(labels=labels, values=values)
#        traces.append(trace)
#        anno = dict(showarrow=False, x=dom_x + (dom_dx/2), y=0.5, xanchor="center")
#        annotation.append(anno)
#        dom_x = dom_x + dom_dx
#     
#    layout = go.Layout(annotations=annotation)
        
        
#    figData = []
#    figData.append()
#    figData.append(go.Pie(labels=categoryList, values=categorySumList))
#    figData.append(go.Pie(labels=labels, values=values))
    
#    anno = dict(title='History Scatter Plot',showlegend=True,autosize = False,)
    #-------------------------------------------------------------------------
    figure = go.Figure(
        data=[
             go.Pie(labels=categoryList, values=categorySumList)           
        ],
        layout=go.Layout(
            title='Income Categories',
            showlegend=True
        )
    )

    return figure
#%%
#########################
# Dashboard Layout / View
#########################
## Functions
def onLoad_GetData():
    '''Actions to perform upon initial page load'''

    accountOptions = (
        [{'label': account, 'value': account}
         for account in getAccounts()]
    )
    return accountOptions

# Set up Dashboard and create layout
app = dash.Dash()


#%%
app.css.append_css({
    "external_url": "https://codepen.io/chriddyp/pen/bWLwgP.css"
})
        
app.css.append_css({
    "external_url": "https://code.getmdl.io/1.3.0/material.indigo-pink.min.css"
})

app.css.append_css({
    "external_url": "https://fonts.googleapis.com/icon?family=Material+Icons"
})

app.css.append_css({
    "external_url": "myCSS.css"
})


        
my_js_url = 'https://code.getmdl.io/1.3.0/material.min.js'
app.scripts.append_script({
    "external_url": my_js_url
})

app.layout = html.Div([
    # Links
#    html.Link(href='myCSS.css', rel='stylesheet'),
    
    # Page Header
    html.Header([
        html.Div([
            html.H1('TITLE V10 - Pie Chart D/C Split',className="mdl-layout__header-row"),            
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
                            html.Div(dcc.Dropdown(id='accountSelector',options=onLoad_GetData(),value='All',className='nine columns')),
                        ],className='twelve columns'),                       
                        
                        #Category Selection
                        html.Div([
                            html.Div('Category Type', className='three columns'),
                            html.Div(dcc.Dropdown(id='categorySelector',value='All',className='nine columns')),
                        ],className='twelve columns'),                        
                    ],className='twelve columns'),
    
                    html.Div(['---------------------------------------------------------------']),

                    html.Div([
                        # Year Selection 
                        html.Div([
                            html.Div('Year', className='three columns'),
                            html.Div(dcc.Dropdown(id='yearSelector',value=str(datetime.now().year),className='nine columns')),
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
                html.Div([
                    # ------------------------------------------------------------------------------
                     html.Div([
                        dt.DataTable(
                            # Initialise the rows
                            columns=['Date','Account','Title','MainCategory','Amount','Balance'],
                            rows=[{}],                            
                            row_selectable=False,
                            filterable=True,
                            sortable=True,
                            selected_row_indices=[],
                            max_rows_in_viewport = 20,
                            id='table'
                        ),
                        html.Div(id='selected-indexes')
                    ]),
                    # ------------------------------------------------------------------------------    
                ],className="mdl-cell mdl-cell--4-col"),
    
                # Graphs
                html.Div([
                    # Top Row Plots
                    html.Div([
                        #Scatter Plot
                        dcc.Graph(id='lineGraph')
                    ]),   
                    
                    # Bottom Row Plots
#                    https://community.plot.ly/t/two-graphs-side-by-side/5312
#                    html.Div([
#                        html.Div([
#                            #Pie
#                            dcc.Graph(id='categoryGraph')
#                        ]),
#                        html.Div([
#                            #Pie
#                            dcc.Graph(id='categoryGraph')
#                        ]),
#                    ]), 
                    html.Div([
                        html.Div([
#                            html.H3('Column 1'),
#                            dcc.Graph(id='g1', figure={'data': [{'y': [1, 2, 3]}]})
                                dcc.Graph(id='categoryGraphExpenses')
                        ], className="six columns"),
                
                        html.Div([
#                            html.H3('Column 2'),
#                            dcc.Graph(id='g2', figure={'data': [{'y': [1, 2, 3]}]})
                            dcc.Graph(id='categoryGraphIncome')
                        ], className="six columns"),
                    ], className="row")
                ],className="mdl-cell mdl-cell--6-col"),
            
            ],className="mdl-grid"),
                
        ],className='page-content')        
    ],className='mdl-layout__content')   
        
    
    ],className='mdl-layout mdl-js-layout mdl-layout--fixed-header')

#############################################
# Interaction Between Components / Controller
#############################################
@app.callback(
    Output('table', 'rows'), 
    [
         Input(component_id='accountSelector', component_property='value'),
         Input(component_id='categorySelector', component_property='value'),
         Input(component_id='yearSelector', component_property='value')
    ]
)
def update_table(account,category,year):
    """
    For user selections, return the relevant table
    """
    transactions = getTransactionResults(account,category,year)
    return transactions.to_dict('records')

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

# Load Year in Dropdown
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

# Load Month in Dropdown
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
    
# Load Day in Dropdown
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

# Update line Graph
@app.callback(
    Output(component_id='lineGraph', component_property='figure'),
    [
        Input(component_id='accountSelector', component_property='value'),
        Input(component_id='categorySelector', component_property='value'),
        Input(component_id='yearSelector', component_property='value')
    ]
)
def updateDrawLineGraph(account,category,year):
    transactions = getTransactionResults(account,category,year)

    figure = []
    if len(transactions) > 0:
        figure = drawLineGraph(transactions,category,account,year)

    return figure

# Update Category Graph Expenses
@app.callback(
    Output(component_id='categoryGraphExpenses', component_property='figure'),
    [
        Input(component_id='accountSelector', component_property='value'),
        Input(component_id='categorySelector', component_property='value'),
        Input(component_id='yearSelector', component_property='value')
    ]
)
def updateDrawPieGraphExpenses(account,category,year):
    transactions = getTransactionResults(account,category,year)

    figure = []
    if len(transactions) > 0:
        figure = drawPieGraphExpenses(transactions)

    return figure

# Update Category Graph Income
@app.callback(
    Output(component_id='categoryGraphIncome', component_property='figure'),
    [
        Input(component_id='accountSelector', component_property='value'),
        Input(component_id='categorySelector', component_property='value'),
        Input(component_id='yearSelector', component_property='value')
    ]
)
def updateDrawPieGraphIncome(account,category,year):
    transactions = getTransactionResults(account,category,year)

    figure = []
    if len(transactions) > 0:
        figure = drawPieGraphIncome(transactions)

    return figure

# start Flask server
if __name__ == '__main__':
    try:
        print('Trying to append all CSV files into TogetherProgrammed.csv')    
        os.system('python combineData.py')
        print('csv combine success.....')
        print('Now running server')        
        
        app.run_server(
            debug=True,
            host='0.0.0.0',
            port=8050
        )
    except: 
        print('csv combine FAIL!!!')
    