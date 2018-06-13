#%%
# I want to make something like this :https://vanguard-report.herokuapp.com/
# the source code is here: https://github.com/plotly/dash-vanguard-report
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
    
    getYearQuery = 'SELECT SUBSTR(Date,7,4) FROM myData'
    yearList = fetch_data(getYearQuery)   
    yearUnique = np.unique(yearList)
    return yearUnique

def getTransactionResultsForSubcategory(account,category,year,subcategory,month):        
    if (month == '00'):
        # if month statement start -------------------------------------------------------------------
        if account == 'All':
            getTransactionQuery = 'SELECT * FROM myData WHERE SUBSTR(Date,7,4)=\'%s\' AND Subcategory=\'%s\'' % (year,subcategory)
        else:            
            if category=='All':
                getTransactionQuery = 'SELECT * FROM myData WHERE SUBSTR(Date,7,4)=\'%s\' AND Account=\'%s\' AND Subcategory=\'%s\'' % (year, account,subcategory)
            else:
                getTransactionQuery = 'SELECT * FROM myData WHERE SUBSTR(Date,7,4)=\'%s\' AND Account=\'%s\' AND MainCategory=\'%s\' AND Subcategory=\'%s\'' % (year, account,category,subcategory)
        # if month statement end  -----------------------------------------------
    else:
         # else month statement start -------------------------------------------------------------------
        if account == 'All':
            getTransactionQuery = 'SELECT * FROM myData WHERE SUBSTR(Date,7,4)=\'%s\' AND Subcategory=\'%s\' AND SUBSTR(Date,1,2)=\'%s\'' % (year,subcategory,month)
        else:            
            if category=='All':
                getTransactionQuery = 'SELECT * FROM myData WHERE SUBSTR(Date,7,4)=\'%s\' AND Account=\'%s\' AND Subcategory=\'%s\' AND SUBSTR(Date,1,2)=\'%s\'' % (year, account,subcategory,month)
            else:
                getTransactionQuery = 'SELECT * FROM myData WHERE SUBSTR(Date,7,4)=\'%s\' AND Account=\'%s\' AND MainCategory=\'%s\' AND Subcategory=\'%s\' AND SUBSTR(Date,1,2)=\'%s\'' % (year, account,category,subcategory,month)
        # else month statement end  -----------------------------------------------        
        
    transactions = fetch_data(getTransactionQuery)    
        
    return transactions   
 
def getTransactionResults(account,category,year,month):  
    if (month=='00'):
        # if month statement start -------------------------------------------------------------------
        if account == 'All':
            getTransactionQuery = 'SELECT * FROM myData WHERE SUBSTR(Date,7,4)=\'%s\'' % (year)
        else:            
            if category=='All':
                getTransactionQuery = 'SELECT * FROM myData WHERE SUBSTR(Date,7,4)=\'%s\' AND Account=\'%s\'' % (year, account)
            else:
                getTransactionQuery = 'SELECT * FROM myData WHERE SUBSTR(Date,7,4)=\'%s\' AND Account=\'%s\' AND MainCategory=\'%s\'' % (year, account,category)
        # if month statement end -------------------------------------------------------------------        
    else:
        # else month statement start -------------------------------------------------------------------
        if account == 'All':
            getTransactionQuery = 'SELECT * FROM myData WHERE SUBSTR(Date,7,4)=\'%s\' AND AND SUBSTR(Date,1,2)=\'%s\'' % (year,month)
        else:            
            if category=='All':
                getTransactionQuery = 'SELECT * FROM myData WHERE SUBSTR(Date,7,4)=\'%s\' AND Account=\'%s\' AND SUBSTR(Date,1,2)=\'%s\' ' % (year, account,month)
            else:
                getTransactionQuery = 'SELECT * FROM myData WHERE SUBSTR(Date,7,4)=\'%s\' AND Account=\'%s\' AND MainCategory=\'%s\' AND SUBSTR(Date,1,2)=\'%s\'' % (year, account,category,month)
        # else month statement end -------------------------------------------------------------------
        
    
            
    transactions = fetch_data(getTransactionQuery)    
        
    return transactions    
    
def drawLineGraph(transactions,category,account,year,month):    
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
            accountTransaction = getTransactionResults(accountName,category,year,month)
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
        MonthlySavings = []
        
        #Initialize these arrays to 0
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
        
        for i in xrange(12):
            MonthlySavings.append(EntireDebit[i] + EntireCredit[i])
            
        
        
        #Draw the scatter plot
        figureList = []
        
        for accountIndex in xrange(len(uniqueAccounts)):  
            figureList.append(go.Scatter(x=months, y=dataPointsList[accountIndex], mode='lines+markers',name=uniqueAccounts[accountIndex]))
        
        figureList.append(go.Scatter(x=months, y=EntireBalance, mode='lines+markers',name='Net Worth'))
        figureList.append(go.Scatter(x=months, y=EntireCredit, mode='lines+markers',name='Expenses'))
        figureList.append(go.Scatter(x=months, y=EntireDebit, mode='lines+markers',name='Income'))
        figureList.append(go.Scatter(x=months, y=MonthlySavings, mode='lines+markers',name='Monthly Savings'))
        
        
        figure = go.Figure(
            data=figureList,
            layout=go.Layout(
                title='History Scatter Plot',
                legend=dict(orientation="h"),
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
                legend=dict(orientation="h"),
                showlegend=True
            )
        )
        #% else statement end-------------------------------------------------------------------------

    return figure

def drawBarGraph(transactions):
    transactions['Amount'] = transactions['Amount'].apply(pd.to_numeric)
    categorySum = transactions.groupby(['MainCategory']).sum()
    categorySumList = np.abs(categorySum['Amount'])
    categorySumList = categorySumList.tolist()
        
    categoryList = np.unique(transactions['MainCategory'].astype(str))
    categoryList = categoryList.tolist()    
    
    categoryDF = pd.DataFrame({
                'CategoryName':categoryList,
                'CategorySum':categorySumList                
            })
    
    categoryDFSorted = categoryDF.sort_values(by=['CategorySum'])
    categorySumList = categoryDFSorted['CategorySum']
    categoryList = categoryDFSorted['CategoryName']
    
    #-------------------------------------------------------------------------
#    http://pycopy.com/plotly-a-pack-of-donuts/
#    uniqueSubCategory = transactions.Subcategory.unique().astype(str)
    #-------------------------------------------------------------------------
    figure = go.Figure(
        data=[
             go.Bar(y=categoryList, 
                    x=categorySumList,
                    orientation="h",
                    )           
        ]
    )
    return figure

def drawPieGraphExpenses(transactions):
    
    transactions['Amount'] = transactions['Amount'].apply(pd.to_numeric)
    categorySum = transactions.groupby(['MainCategory']).sum()
    categorySumList = np.abs(categorySum['Amount'])
    categorySumList = categorySumList.tolist()
        
    categoryList = np.unique(transactions['MainCategory'].astype(str))
    categoryList = categoryList.tolist()    
        
    #-------------------------------------------------------------------------
#    http://pycopy.com/plotly-a-pack-of-donuts/
#    uniqueSubCategory = transactions.Subcategory.unique().astype(str)
    #-------------------------------------------------------------------------
    figure = go.Figure(
        data=[
             go.Pie(labels=categoryList, values=categorySumList,textposition="inside")           
        ],
        layout=go.Layout(
            title='Expenses',
            showlegend=True
        )
    )

    return figure

def drawLineGraphByCategory(transactions,category,account,year,month):   
    #Yearly Calculations
    months = ['JAN', 'FEB', 'MAR', 'APR', 'MAY', 'JUN', 'JUL', 'AUG', 'SEP', 'OCT', 'NOV', 'DEC'] 
    
    if (account == 'All'):
        #% if statement start--------------------------------------------------------------------------
        #Get unique accounts
        uniqueCategory= transactions.MainCategory.unique().astype(str)
        
        #Generate a list of data points for each of the unique accounts
        dataPointsList = []        
        
        #Obtain the current monthly balances for each of the unique accounts
        for categoryName in uniqueCategory:                             
            # Create empty array filled with zeroes for each of the months
            dataPoints = []            
            
            for i in xrange(12):
                dataPoints.append(0)                
            
            #Create the unique monthly balances for each of the accounts
            numberOfTransactions = np.shape(transactions)[0]    
            for transactionNumber in xrange(numberOfTransactions):
                if(transactions['MainCategory'][transactionNumber]==categoryName):
                    monthIndex = int(str(transactions['Date'][transactionNumber]).split('/')[0]) -1
                    dataPoints[monthIndex] += float(transactions['Amount'][transactionNumber])                                
                
            dataPointsList.append(dataPoints)
        
             
        #Draw the scatter plot
        figureList = []
        
        for categoryIndex in xrange(len(uniqueCategory)):  
            figureList.append(go.Scatter(x=months, y=dataPointsList[categoryIndex], mode='lines+markers',name=uniqueCategory[categoryIndex]))
            
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
    
def drawPieGraphIncome(transactions):
    
    transactions['Amount'] = transactions['Amount'].apply(pd.to_numeric)
    categorySum = transactions.groupby(['MainCategory']).sum()
    categorySumList = np.abs(categorySum['Amount'])
    categorySumList = categorySumList.tolist()
        
    categoryList = np.unique(transactions['MainCategory'].astype(str))
    categoryList = categoryList.tolist()    
        
    
    #-------------------------------------------------------------------------
#    http://pycopy.com/plotly-a-pack-of-donuts/
#    uniqueSubCategory = transactions.Subcategory.unique().astype(str)

    #-------------------------------------------------------------------------
    figure = go.Figure(
        data=[
             go.Pie(labels=categoryList, values=categorySumList,textposition="inside")           
        ],
        layout=go.Layout(
            title='Income',
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

#app.css.append_css({
#    "external_url": "myModifiedCSS.css"
#})


        
my_js_url = 'https://code.getmdl.io/1.3.0/material.min.js'
app.scripts.append_script({
    "external_url": my_js_url
})

divPadding = '15px'
# NOTE: The layout design for dash can be found here:
#    https://codepen.io/chriddyp/pen/bWLwgP
app.layout = html.Div([
    # Links
#    html.Link(href='myCSS.css', rel='stylesheet'),
     
        # Page Main Start
        html.Main([
                # Page Content Start
                html.Div([
                    # Partision of page start
                    html.Div([
                            # Search row start
                            html.Div([                               
                                html.Div([
                                    html.Div([
                                        html.Div('Account Type', className='three columns'),
                                        html.Div(dcc.Dropdown(id='accountSelector',options=onLoad_GetData(),value='All',className='nine columns')),                                                        
                                    ],className ='three columns'),            
                                    html.Div([  
                                        html.Div('Category Type', className='three columns'),
                                        html.Div(dcc.Dropdown(id='categorySelector',value='All',className='nine columns')),                              
                                        
                                    ],className ='three columns'),            
                                    html.Div([  
                                        html.Div('Year', className='three columns'),
                                        html.Div(dcc.Dropdown(id='yearSelector',value=str(datetime.now().year),className='nine columns')),                              
                                        
                                    ],className ='three columns'),            
                                    html.Div([                                
                                        html.Div('Month', className='three columns'),
                                        html.Div(dcc.Dropdown(id='monthSelector',value='00',className='nine columns')),
                                    ],className ='three columns'),                                                        
                                ],className ='twelve columns'),            
                            # Search row end
                            ],className ='twelve columns'),                            
                            
                            # Top row start
                            html.Div([                                    
                                    # table start
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
                                                max_rows_in_viewport = 10,
                                                id='table'
                                            ),
                                            html.Div(id='selected-indexes')
                                        ]),
                                        # ------------------------------------------------------------------------------                                                
                                    # table end
                                    ], className="seven columns",style={'padding': divPadding}),
                                    
                                    # Graph start
                                    html.Div([
                                        # ------------------------------------------------------------------------------
                                         # Top Row Plots
                                            html.Div([
                                                #Scatter Plot
                        #                        html.Button('Refresh', id='buttonRefresh'),
                                                dcc.Graph(id='lineGraph')
                                            ]),  
                                        # ------------------------------------------------------------------------------                                                
                                    # Graph end
                                    ], className="five columns",style={'padding': divPadding}),
                            # top row end        
                            ], className="twelve columns"),
                            
                            # Bottom row start
                            html.Div([
                                # Bottom Row Plots
            #                    https://community.plot.ly/t/two-graphs-side-by-side/5312
                                html.Div([
                                    html.Div([
            #                            html.Button('Plot Expenses', id='buttonExpense'),
                                        dcc.Graph(id='categoryGraphExpenses')
                                    ], className="six columns",style={'padding': divPadding}),
                            
                                    html.Div([
#                                        html.H1('Table')
            #                            html.Button('Plot Income', id='buttonIncome'),            
                                        dcc.Graph(id='categoryBarGraphExpenses')
                                    ], className="six columns"),
                                ], className="six columns",style={'padding': divPadding}),
                                
                                html.Div([
                                    html.Div([
            #                            html.Button('Plot Expenses', id='buttonExpense'),
                                        dcc.Graph(id='categoryGraphIncome')
                                    ], className="six columns",style={'padding': divPadding}),
                            
                                    html.Div([
            #                            html.Button('Plot Income', id='buttonIncome'),
#                                        html.H1('Table')
                                        dcc.Graph(id='categoryBarGraphIncome')
                                    ], className="six columns",style={'padding': divPadding}),
                                ], className="six columns")                                    
                            # bottom row end        
                            ], className="twelve columns")
                    # Partision of page end
                    ],className="mdl-grid"),
                # Page content end
                ],className='page-content',style={'background-color': 'black'})        
        # Page Main End
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
         Input(component_id='yearSelector', component_property='value'),
         Input(component_id='monthSelector', component_property='value')
    ]
)
def update_table(account,category,year,month):
    """
    For user selections, return the relevant table
    """
    transactions = getTransactionResults(account,category,year,month)
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
    months = ['All','JAN', 'FEB', 'MAR', 'APR', 'MAY', 'JUN', 'JUL', 'AUG', 'SEP', 'OCT', 'NOV', 'DEC']
    value = ['00','01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12']
    return [
        {'label': months[month], 'value': value[month]}
        for month in xrange(len(months))
    ]

@app.callback(
    Output(component_id='lineGraph', component_property='figure'),
    [
        Input(component_id='accountSelector', component_property='value'),
        Input(component_id='categorySelector', component_property='value'),
        Input(component_id='yearSelector', component_property='value'),
        Input(component_id='monthSelector', component_property='value')
#        Input(component_id='stateSelector', component_property='value')
                
    ]
)
def updateDrawLineGraph(account,category,year,month):        
       
    transactions = getTransactionResults(account,category,year,month)

    figure = []
    if len(transactions) > 0:
        figure = drawLineGraph(transactions,category,account,year,month)

    return figure

# Update Category Graph Expenses
@app.callback(
    Output(component_id='categoryGraphExpenses', component_property='figure'),
    [
        Input(component_id='accountSelector', component_property='value'),
        Input(component_id='categorySelector', component_property='value'),
        Input(component_id='yearSelector', component_property='value'),
        Input(component_id='monthSelector', component_property='value')
    ]
)
def updateDrawPieGraphExpenses(account,category,year,month):
    transactions = getTransactionResultsForSubcategory(account,category,year,'Credit',month)

    figure = []
    if len(transactions) > 0:
        figure = drawPieGraphExpenses(transactions)

    return figure

#Update Category Bar Graph Expenses    
@app.callback(
    Output(component_id='categoryBarGraphExpenses', component_property='figure'),
    [
        Input(component_id='accountSelector', component_property='value'),
        Input(component_id='categorySelector', component_property='value'),
        Input(component_id='yearSelector', component_property='value'),
        Input(component_id='monthSelector', component_property='value')
    ]
)
def updateDrawBarGraphExpenses(account,category,year,month):
    transactions = getTransactionResultsForSubcategory(account,category,year,'Credit',month)        
    figure = []
    if len(transactions) > 0:
        if(month=="00"):        
            figure = []
            if len(transactions) > 0:
                figure = drawLineGraphByCategory(transactions,category,account,year,month)
        else:        
            figure = drawBarGraph(transactions)
    return figure

# Update Category Graph Income
@app.callback(
    Output(component_id='categoryGraphIncome', component_property='figure'),
    [
        Input(component_id='accountSelector', component_property='value'),
        Input(component_id='categorySelector', component_property='value'),
        Input(component_id='yearSelector', component_property='value'),
        Input(component_id='monthSelector', component_property='value')        
    ]
)
def updateDrawPieGraphIncome(account,category,year,month):
    transactions = getTransactionResultsForSubcategory(account,category,year,'Debit',month)

    figure = []
    if len(transactions) > 0:
        figure = drawPieGraphIncome(transactions)

    return figure

#Update Category Bar Graph Expenses    
@app.callback(
    Output(component_id='categoryBarGraphIncome', component_property='figure'),
    [
        Input(component_id='accountSelector', component_property='value'),
        Input(component_id='categorySelector', component_property='value'),
        Input(component_id='yearSelector', component_property='value'),
        Input(component_id='monthSelector', component_property='value')
    ]
)
def updateDrawBarGraphIncome(account,category,year,month):
    transactions = getTransactionResultsForSubcategory(account,category,year,'Debit',month)        
    figure = []
    if len(transactions) > 0:
        if(month=="00"):        
            figure = []
            if len(transactions) > 0:
                figure = drawLineGraphByCategory(transactions,category,account,year,month)
        else:        
            figure = drawBarGraph(transactions)
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
    