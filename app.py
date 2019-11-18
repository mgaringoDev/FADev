# coding: utf-8
#%% Imports
import dash
from dash.dependencies import Input, Output
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objs as go
import pandas as pd
import os
import numpy as np

import dash_table_experiments as dt
import plotly.plotly as py
import plotly.figure_factory as ff

# pydata stack
from sqlalchemy import create_engine

# database stuff
import csv, sqlite3
from datetime import datetime
import unicodedata
from math import log10, floor
#%% Global
app = dash.Dash(__name__)
server = app.server

# read data for tables (one df per table)
df_fund_facts = pd.read_csv('https://plot.ly/~bdun9/2754.csv')
df_price_perf = pd.read_csv('https://plot.ly/~bdun9/2756.csv')
df_current_prices = pd.read_csv('https://plot.ly/~bdun9/2753.csv')
df_hist_prices = pd.read_csv('https://plot.ly/~bdun9/2765.csv')
df_avg_returns = pd.read_csv('https://plot.ly/~bdun9/2793.csv')
df_after_tax = pd.read_csv('https://plot.ly/~bdun9/2794.csv')
df_recent_returns = pd.read_csv('https://plot.ly/~bdun9/2795.csv')
df_equity_char = pd.read_csv('https://plot.ly/~bdun9/2796.csv')
df_equity_diver = pd.read_csv('https://plot.ly/~bdun9/2797.csv')
df_expenses = pd.read_csv('https://plot.ly/~bdun9/2798.csv')
df_minimums = pd.read_csv('https://plot.ly/~bdun9/2799.csv')
df_dividend = pd.read_csv('https://plot.ly/~bdun9/2800.csv')
df_realized = pd.read_csv('https://plot.ly/~bdun9/2801.csv')
df_unrealized = pd.read_csv('https://plot.ly/~bdun9/2802.csv')

df_graph = pd.read_csv("https://plot.ly/~bdun9/2804.csv")

#%% Data Manipulation / Model
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

def round_to_1(x):
    return round(x, -int(floor(log10(abs(x)))))

def getAccounts():
    '''Returns the list of accounts that are stored in the database'''

    getAccountQuery = 'SELECT DISTINCT Account FROM myData'
    accounts = fetch_data(getAccountQuery)
    accounts = list(accounts['Account'].sort_values(ascending=True))    
    accounts.append('All')
    accounts.sort()
    return accounts

def getAllAccounts(cat):
    '''Returns the list of accounts that are stored in the database'''

    getAccountQuery = 'SELECT * FROM myData WHERE MainCategory=\'%s\'' % cat
    accounts = fetch_data(getAccountQuery)
    return accounts

def getAllCategories():
    '''Returns the list of accounts that are stored in the database'''

    getCategoryQuery = 'SELECT DISTINCT MainCategory FROM myData'
    category = fetch_data(getCategoryQuery)
    category = list(category['MainCategory'].sort_values(ascending=True))    
    category.append('All')
    category.sort()
    return category

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
                autosize= True,
                margin = {
                    "r": 40,
                    "t": 30,
                    "b": 30,
                    "l": 40
                  },
#                title='History Scatter Plot',
#                legend=dict(orientation="v"),  
                height = 240,
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
            autosize= True,
            margin = {
                "r": 5,
                "t": 30,
                "b": 30,
                "l": 5
              },
            legend=dict(orientation="h"),  
            height = 350,
            showlegend=False
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
                autosize= True,
                margin = {
                    "r": 40,
                    "t": 30,
                    "b": 30,
                    "l": 40
                  },
                legend=dict(orientation="v"),  
                height = 350,
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
                autosize= True,
                margin = {
                    "r": 40,
                    "t": 30,
                    "b": 30,
                    "l": 40
                  },
                legend=dict(orientation="h"),  
                height = 350,
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
            autosize= True,
            margin = {
                "r": 5,
                "t": 30,
                "b": 30,
                "l": 5
              },
            legend=dict(orientation="h"),  
            height = 300,
            showlegend=False
        )
    )

    return figure
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

def onLoadGetAllCategories():
    '''Actions to perform upon initial page load'''

    categoryOptions = (
        [{'label': category, 'value': category}
         for category in getAllCategories()]
    )
    return categoryOptions

# reusable componenets
def make_dash_table(df):
    ''' Return a dash definition of an HTML table for a Pandas dataframe '''
    table = []
    for index, row in df.iterrows():
        html_row = []
        for i in range(len(row)):
            html_row.append(html.Td([row[i]]))
        table.append(html.Tr(html_row))
    return table


def print_button():
    printButton = html.A(['Print PDF'],className="button no-print print",style={'position': "absolute", 'top': '-40', 'right': '0'})
    return printButton

# includes page/full view
def get_logo():
    logo = html.Div([

        html.Div([
            html.Img(src='http://logonoid.com/images/vanguard-logo.png', height='40', width='160')
        ], className="ten columns padded"),

        html.Div([
            dcc.Link('Full View   ', href='/full-view')
        ], className="two columns page-view no-print")

    ], className="row gs-header")
    return logo


def get_header():
    header = html.Div([
        html.Div([
            html.H5(
                'Ma FA')
        ], className="twelve columns padded")
    ], className="row gs-header gs-text-header")
    return header

def getDropDowns():
    dropDowns = html.Div([                               
        html.Div([
            html.Div([
                html.Div('ACC', className='three columns'),
                html.Div(dcc.Dropdown(id='accountSelector',options=onLoad_GetData(),value='All',className='nine columns')),                                                        
            ],className ='three columns'),            
            html.Div([  
                html.Div('CAT', className='three columns'),
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
    ],className ='twelve columns')
    return dropDowns

def get_menu():
    menu = html.Div([

        dcc.Link('myOverview   ', href='/myOverview', className="tab first"),
        dcc.Link('Overview   ', href='/overview', className="tab"),

        dcc.Link('Price Performance   ', href='/price-performance', className="tab"),

        dcc.Link('Portfolio & Management   ', href='/portfolio-management', className="tab"),

        dcc.Link('Fees & Minimums   ', href='/fees', className="tab"),

        dcc.Link('Distributions   ', href='/distributions', className="tab"),

        dcc.Link('News & Reviews   ', href='/news-and-reviews', className="tab")

    ], className="row ")
    return menu

def loadHeaderInfo():
    headerInfo = html.Div([
#            get_logo(),
            get_header(),
            html.Br([])
#            get_menu(),
#            getDropDowns()
            ])
    return headerInfo

#%% My Layout
myOverview = html.Div([  # page 1

        print_button(),

        html.Div([

            # Header
            loadHeaderInfo(),
            
            # ---------------- Row For History Scatter Plot Start -------------
            html.Div([

                html.Div([
                    html.H6("Transactions",
                            className="gs-header gs-table-header padded"),
                    # table start                    
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
                ], className="twelve columns")

            ], className="row "),
            # ---------------- Row For History Scatter Plot End -------------
            # Row 3
            html.Div([

                html.Div([
                    html.H6('Transactions',
                            className="gs-header gs-text-header padded"),

                    html.Br([]),
                    
                    # ---------------------------------------------------------------------------------------
                    html.P("\
                            As the industry’s first index fund for individual investors, \
                            the 500 Index Fund is a low-cost way to gain diversified exposure \
                            to the U.S. equity market. The fund offers exposure to 500 of the \
                            largest U.S. companies, which span many different industries and \
                            account for about three-fourths of the U.S. stock market’s value. \
                            The key risk for the fund is the volatility that comes with its full \
                            exposure to the stock market. Because the 500 Index Fund is broadly \
                            diversified within the large-capitalization market, it may be \
                            considered a core equity holding in a portfolio."),
                    
                   # ---------------------------------------------------------------------------------------

                ], className="six columns"),

                html.Div([
                    html.H6(["Fund Facts"],
                            className="gs-header gs-table-header padded"),
                    html.Table(make_dash_table(df_fund_facts))
                ], className="six columns"),

            ], className="row "),            
           

        ], className="subpage")

    ], className="page")

#%% Page layouts
overview = html.Div([  # page 1

        print_button(),

        html.Div([

            # Header
            loadHeaderInfo(),

            # Row 3

            html.Div([

                html.Div([
                    html.H6('Product Summary',
                            className="gs-header gs-text-header padded"),

                    html.Br([]),

                    html.P("\
                            As the industry’s first index fund for individual investors, \
                            the 500 Index Fund is a low-cost way to gain diversified exposure \
                            to the U.S. equity market. The fund offers exposure to 500 of the \
                            largest U.S. companies, which span many different industries and \
                            account for about three-fourths of the U.S. stock market’s value. \
                            The key risk for the fund is the volatility that comes with its full \
                            exposure to the stock market. Because the 500 Index Fund is broadly \
                            diversified within the large-capitalization market, it may be \
                            considered a core equity holding in a portfolio."),

                ], className="six columns"),

                html.Div([
                    html.H6(["Fund Facts"],
                            className="gs-header gs-table-header padded"),
                    html.Table(make_dash_table(df_fund_facts))
                ], className="six columns"),

            ], className="row "),

            # Row 4

            html.Div([

                html.Div([
                    html.H6('Average annual performance',
                            className="gs-header gs-text-header padded"),
                    dcc.Graph(
                        id = "graph-1",
                        figure={
                            'data': [
                                go.Bar(
                                    x = ["1 Year", "3 Year", "5 Year", "10 Year", "41 Year"],
                                    y = ["21.67", "11.26", "15.62", "8.37", "11.11"],
                                    marker = {
                                      "color": "rgb(53, 83, 255)",
                                      "line": {
                                        "color": "rgb(255, 255, 255)",
                                        "width": 2
                                      }
                                    },
                                    name = "500 Index Fund",
                                    type = "bar"
                                ),
                                go.Bar(
                                    x = ["1 Year", "3 Year", "5 Year", "10 Year", "41 Year"],
                                    y = ["21.83", "11.41", "15.79", "8.50"],
                                    marker = {
                                      "color": "rgb(255, 225, 53)",
                                      "line": {
                                        "color": "rgb(255, 255, 255)",
                                        "width": 2
                                        }
                                    },
                                    name = "S&P 500 Index",
                                    type = "bar"
                                ),
                            ],
                            'layout': go.Layout(
                                autosize = False,
                                bargap = 0.35,
                                font = {
                                  "family": "Raleway",
                                  "size": 10
                                },
                                height = 200,
                                hovermode = "closest",
                                legend = {
                                  "x": -0.0228945952895,
                                  "y": -0.189563896463,
                                  "orientation": "h",
                                  "yanchor": "top"
                                },
                                margin = {
                                  "r": 0,
                                  "t": 20,
                                  "b": 10,
                                  "l": 10
                                },
                                showlegend = True,
                                title = "",
                                width = 340,
                                xaxis = {
                                  "autorange": True,
                                  "range": [-0.5, 4.5],
                                  "showline": True,
                                  "title": "",
                                  "type": "category"
                                },
                                yaxis = {
                                  "autorange": True,
                                  "range": [0, 22.9789473684],
                                  "showgrid": True,
                                  "showline": True,
                                  "title": "",
                                  "type": "linear",
                                  "zeroline": False
                                }
                            )
                        },
                        config={
                            'displayModeBar': False
                        }
                    )
                ], className="six columns"),

                html.Div([
                    html.H6("Hypothetical growth of $10,000",
                            className="gs-header gs-table-header padded"),
                    dcc.Graph(
                        id="grpah-2",
                        figure={
                            'data': [
                                go.Scatter(
                                    x = ["2008", "2009", "2010", "2011", "2012", "2013", "2014", "2015", "2016", "2017", "2018"],
                                    y = ["10000", "7500", "9000", "10000", "10500", "11000", "14000", "18000", "19000", "20500", "24000"],
                                    line = {"color": "rgb(53, 83, 255)"},
                                    mode = "lines",
                                    name = "500 Index Fund Inv"
                                )
                            ],
                            'layout': go.Layout(
                                autosize = False,
                                title = "",
                                font = {
                                  "family": "Raleway",
                                  "size": 10
                                },
                                height = 200,
                                width = 340,
                                hovermode = "closest",
                                legend = {
                                  "x": -0.0277108433735,
                                  "y": -0.142606516291,
                                  "orientation": "h"
                                },
                                margin = {
                                  "r": 20,
                                  "t": 20,
                                  "b": 20,
                                  "l": 50
                                },
                                showlegend = True,
                                xaxis = {
                                  "autorange": True,
                                  "linecolor": "rgb(0, 0, 0)",
                                  "linewidth": 1,
                                  "range": [2008, 2018],
                                  "showgrid": False,
                                  "showline": True,
                                  "title": "",
                                  "type": "linear"
                                },
                                yaxis = {
                                  "autorange": False,
                                  "gridcolor": "rgba(127, 127, 127, 0.2)",
                                  "mirror": False,
                                  "nticks": 4,
                                  "range": [0, 30000],
                                  "showgrid": True,
                                  "showline": True,
                                  "ticklen": 10,
                                  "ticks": "outside",
                                  "title": "$",
                                  "type": "linear",
                                  "zeroline": False,
                                  "zerolinewidth": 4
                                }
                            )
                        },
                        config={
                            'displayModeBar': False
                        }
                    )
                ], className="six columns"),

            ], className="row "),

            # Row 5

            html.Div([

                html.Div([
                    html.H6('Price & Performance (%)',
                            className="gs-header gs-table-header padded"),
                    html.Table(make_dash_table(df_price_perf))
                ], className="six columns"),

                html.Div([
                    html.H6("Risk Potential",
                            className="gs-header gs-table-header padded"),
                    dcc.Graph(
                        id='graph-3',
                        figure = {
                            'data': [
                                go.Scatter(
                                    x = ["0", "0.18", "0.18", "0"],
                                    y = ["0.2", "0.2", "0.4", "0.2"],
                                    fill = "tozerox",
                                    fillcolor = "rgba(31, 119, 180, 0.2)",
                                    hoverinfo = "none",
                                    line = {"width": 0},
                                    mode = "lines",
                                    name = "B",
                                    showlegend = False
                                ),
                                go.Scatter(
                                    x = ["0.2", "0.38", "0.38", "0.2", "0.2"],
                                    y = ["0.2", "0.2", "0.6", "0.4", "0.2"],
                                    fill = "tozerox",
                                    fillcolor = "rgba(31, 119, 180, 0.4)",
                                    hoverinfo = "none",
                                    line = {"width": 0},
                                    mode = "lines",
                                    name = "D",
                                    showlegend = False
                                ),
                                go.Scatter(
                                    x = ["0.4", "0.58", "0.58", "0.4", "0.4"],
                                    y = ["0.2", "0.2", "0.8", "0.6", "0.2"],
                                    fill = "tozerox",
                                    fillcolor = "rgba(31, 119, 180, 0.6)",
                                    hoverinfo = "none",
                                    line = {"width": 0},
                                    mode = "lines",
                                    name = "F",
                                    showlegend = False
                                ),
                                go.Scatter(
                                    x = ["0.6", "0.78", "0.78", "0.6", "0.6"],
                                    y = ["0.2", "0.2", "1", "0.8", "0.2"],
                                    fill = "tozerox",
                                    fillcolor = "rgb(31, 119, 180)",
                                    hoverinfo = "none",
                                    line = {"width": 0},
                                    mode = "lines",
                                    name = "H",
                                    showlegend = False
                                ),
                                go.Scatter(
                                    x = ["0.8", "0.98", "0.98", "0.8", "0.8"],
                                    y = ["0.2", "0.2", "1.2", "1", "0.2"],
                                    fill = "tozerox",
                                    fillcolor = "rgba(31, 119, 180, 0.8)",
                                    hoverinfo = "none",
                                    line = {"width": 0},
                                    mode = "lines",
                                    name = "J",
                                    showlegend = False
                                ),
                            ],
                            'layout': go.Layout(
                                title = "",
                                annotations = [
                                    {
                                      "x": 0.69,
                                      "y": 0.6,
                                      "font": {
                                        "color": "rgb(31, 119, 180)",
                                        "family": "Raleway",
                                        "size": 30
                                      },
                                      "showarrow": False,
                                      "text": "<b>4</b>",
                                      "xref": "x",
                                      "yref": "y"
                                    },
                                    {
                                      "x": 0.0631034482759,
                                      "y": -0.04,
                                      "align": "left",
                                      "font": {
                                        "color": "rgb(44, 160, 44)",
                                        "family": "Raleway",
                                        "size": 10
                                      },
                                      "showarrow": False,
                                      "text": "<b>Less risk<br>Less reward</b>",
                                      "xref": "x",
                                      "yref": "y"
                                    },
                                    {
                                      "x": 0.92125,
                                      "y": -0.04,
                                      "align": "right",
                                      "font": {
                                        "color": "rgb(214, 39, 40)",
                                        "family": "Raleway",
                                        "size": 10
                                      },
                                      "showarrow": False,
                                      "text": "<b>More risk<br>More reward</b>",
                                      "xref": "x",
                                      "yref": "y"
                                    }
                                  ],
                                  autosize = False,
                                  height = 200,
                                  width = 340,
                                  hovermode = "closest",
                                  margin = {
                                    "r": 10,
                                    "t": 20,
                                    "b": 80,
                                    "l": 10
                                  },
                                  shapes = [
                                    {
                                      "fillcolor": "rgb(255, 255, 255)",
                                      "line": {
                                        "color": "rgb(31, 119, 180)",
                                        "width": 4
                                      },
                                      "opacity": 1,
                                      "type": "circle",
                                      "x0": 0.621,
                                      "x1": 0.764,
                                      "xref": "x",
                                      "y0": 0.135238095238,
                                      "y1": 0.98619047619,
                                      "yref": "y"
                                    }
                                  ],
                                  showlegend = True,
                                  xaxis = {
                                    "autorange": False,
                                    "fixedrange": True,
                                    "range": [-0.05, 1.05],
                                    "showgrid": False,
                                    "showticklabels": False,
                                    "title": "<br>",
                                    "type": "linear",
                                    "zeroline": False
                                  },
                                  yaxis = {
                                    "autorange": False,
                                    "fixedrange": True,
                                    "range": [-0.3, 1.6],
                                    "showgrid": False,
                                    "showticklabels": False,
                                    "title": "<br>",
                                    "type": "linear",
                                    "zeroline": False
                                }
                            )
                        },
                        config={
                            'displayModeBar': False
                        }
                    )
                ], className="six columns"),

            ], className="row ")

        ], className="subpage")

    ], className="page")

#%% Price Performance
pricePerformance = html.Div([  # page 2

        print_button(),

        html.Div([

            # Header
            loadHeaderInfo(),

            # Row ``

            html.Div([

                html.Div([
                    html.H6(["Current Prices"],
                            className="gs-header gs-table-header padded"),
                    html.Table(make_dash_table(df_current_prices))

                ], className="six columns"),

                html.Div([
                    html.H6(["Historical Prices"],
                            className="gs-header gs-table-header padded"),
                    html.Table(make_dash_table(df_hist_prices))
                ], className="six columns"),

            ], className="row "),

            # Row 2

            html.Div([

                html.Div([
                    html.H6("Performance",
                            className="gs-header gs-table-header padded"),
                    dcc.Graph(
                        id='graph-4',
                        figure={
                            'data': [
                                go.Scatter(
                                    x = df_graph['Date'],
                                    y = df_graph['Vanguard 500 Index Fund'],
                                    line = {"color": "rgb(53, 83, 255)"},
                                    mode = "lines",
                                    name = "Vanguard 500 Index Fund"
                                ),
                                go.Scatter(
                                    x = df_graph['Date'],
                                    y = df_graph['MSCI EAFE Index Fund (ETF)'],
                                    line = {"color": "rgb(255, 225, 53)"},
                                    mode = "lines",
                                    name = "MSCI EAFE Index Fund (ETF)"
                                )
                            ],
                            'layout': go.Layout(
                                autosize = False,
                                width = 700,
                                height = 200,
                                font = {
                                    "family": "Raleway",
                                    "size": 10
                                  },
                                 margin = {
                                    "r": 40,
                                    "t": 40,
                                    "b": 30,
                                    "l": 40
                                  },
                                  showlegend = True,
                                  titlefont = {
                                    "family": "Raleway",
                                    "size": 10
                                  },
                                  xaxis = {
                                    "autorange": True,
                                    "range": ["2007-12-31", "2018-03-06"],
                                    "rangeselector": {"buttons": [
                                        {
                                          "count": 1,
                                          "label": "1Y",
                                          "step": "year",
                                          "stepmode": "backward"
                                        },
                                        {
                                          "count": 3,
                                          "label": "3Y",
                                          "step": "year",
                                          "stepmode": "backward"
                                        },
                                        {
                                          "count": 5,
                                          "label": "5Y",
                                          "step": "year"
                                        },
                                        {
                                          "count": 10,
                                          "label": "10Y",
                                          "step": "year",
                                          "stepmode": "backward"
                                        },
                                        {
                                          "label": "All",
                                          "step": "all"
                                        }
                                      ]},
                                    "showline": True,
                                    "type": "date",
                                    "zeroline": False
                                  },
                                  yaxis = {
                                    "autorange": True,
                                    "range": [18.6880162434, 278.431996757],
                                    "showline": True,
                                    "type": "linear",
                                    "zeroline": False
                                  }
                            )
                        },
                        config={
                            'displayModeBar': False
                        }
                    )
                ], className="twelve columns")

            ], className="row "),

            # Row 3

            html.Div([

                html.Div([
                    html.H6(["Average annual returns--updated monthly as of 02/28/2018"], className="gs-header gs-table-header tiny-header"),
                    html.Table(make_dash_table(df_avg_returns), className="tiny-header")
                ], className=" twelve columns"),

            ], className="row "),

            # Row 4

            html.Div([

                html.Div([
                    html.H6(["After-tax returns--updated quarterly as of 12/31/2017"], className="gs-header gs-table-header tiny-header"),
                    html.Table(make_dash_table(df_after_tax), className="tiny-header")
                ], className=" twelve columns"),

            ], className="row "),

            # Row 5

            html.Div([

                html.Div([
                    html.H6(["Recent investment returns"], className="gs-header gs-table-header tiny-header"),
                    html.Table(make_dash_table(df_recent_returns), className="tiny-header")
                ], className=" twelve columns"),

            ], className="row "),

        ], className="subpage")

    ], className="page")

#%% Porfolio
portfolioManagement = html.Div([ # page 3

        print_button(),

        html.Div([

            # Header
            loadHeaderInfo(),

            # Row 1

            html.Div([

                html.Div([
                    html.H6(["Portfolio"],
                            className="gs-header gs-table-header padded")
                ], className="twelve columns"),

            ], className="row "),

            # Row 2

            html.Div([

                html.Div([
                    html.Strong(["Stock style"]),
                    dcc.Graph(
                        id='graph-5',
                        figure={
                            'data': [
                                go.Scatter(
                                    x = ["1"],
                                    y = ["1"],
                                    hoverinfo = "none",
                                    marker = {
                                        "color": ["transparent"]
                                    },
                                    mode = "markers",
                                    name = "B",
                                )
                            ],
                            'layout': go.Layout(
                                title = "",
                                annotations = [
                                {
                                  "x": 0.990130093458,
                                  "y": 1.00181709504,
                                  "align": "left",
                                  "font": {
                                    "family": "Raleway",
                                    "size": 9
                                  },
                                  "showarrow": False,
                                  "text": "<b>Market<br>Cap</b>",
                                  "xref": "x",
                                  "yref": "y"
                                },
                                {
                                  "x": 1.00001816013,
                                  "y": 1.35907755794e-16,
                                  "font": {
                                    "family": "Raleway",
                                    "size": 9
                                  },
                                  "showarrow": False,
                                  "text": "<b>Style</b>",
                                  "xref": "x",
                                  "yanchor": "top",
                                  "yref": "y"
                                }
                              ],
                              autosize = False,
                              width = 200,
                              height = 150,
                              hovermode = "closest",
                              margin = {
                                "r": 30,
                                "t": 20,
                                "b": 20,
                                "l": 30
                              },
                              shapes = [
                                {
                                  "fillcolor": "rgb(127, 127, 127)",
                                  "line": {
                                    "color": "rgb(0, 0, 0)",
                                    "width": 2
                                  },
                                  "opacity": 0.3,
                                  "type": "rectangle",
                                  "x0": 0,
                                  "x1": 0.33,
                                  "xref": "paper",
                                  "y0": 0,
                                  "y1": 0.33,
                                  "yref": "paper"
                                },
                                {
                                  "fillcolor": "rgb(127, 127, 127)",
                                  "line": {
                                    "color": "rgb(0, 0, 0)",
                                    "dash": "solid",
                                    "width": 2
                                  },
                                  "opacity": 0.3,
                                  "type": "rectangle",
                                  "x0": 0.33,
                                  "x1": 0.66,
                                  "xref": "paper",
                                  "y0": 0,
                                  "y1": 0.33,
                                  "yref": "paper"
                                },
                                {
                                  "fillcolor": "rgb(127, 127, 127)",
                                  "line": {
                                    "color": "rgb(0, 0, 0)",
                                    "width": 2
                                  },
                                  "opacity": 0.3,
                                  "type": "rectangle",
                                  "x0": 0.66,
                                  "x1": 0.99,
                                  "xref": "paper",
                                  "y0": 0,
                                  "y1": 0.33,
                                  "yref": "paper"
                                },
                                {
                                  "fillcolor": "rgb(127, 127, 127)",
                                  "line": {
                                    "color": "rgb(0, 0, 0)",
                                    "width": 2
                                  },
                                  "opacity": 0.3,
                                  "type": "rectangle",
                                  "x0": 0,
                                  "x1": 0.33,
                                  "xref": "paper",
                                  "y0": 0.33,
                                  "y1": 0.66,
                                  "yref": "paper"
                                },
                                {
                                  "fillcolor": "rgb(127, 127, 127)",
                                  "line": {
                                    "color": "rgb(0, 0, 0)",
                                    "width": 2
                                  },
                                  "opacity": 0.3,
                                  "type": "rectangle",
                                  "x0": 0.33,
                                  "x1": 0.66,
                                  "xref": "paper",
                                  "y0": 0.33,
                                  "y1": 0.66,
                                  "yref": "paper"
                                },
                                {
                                  "fillcolor": "rgb(127, 127, 127)",
                                  "line": {
                                    "color": "rgb(0, 0, 0)",
                                    "width": 2
                                  },
                                  "opacity": 0.3,
                                  "type": "rectangle",
                                  "x0": 0.66,
                                  "x1": 0.99,
                                  "xref": "paper",
                                  "y0": 0.33,
                                  "y1": 0.66,
                                  "yref": "paper"
                                },
                                {
                                  "fillcolor": "rgb(127, 127, 127)",
                                  "line": {
                                    "color": "rgb(0, 0, 0)",
                                    "width": 2
                                  },
                                  "opacity": 0.3,
                                  "type": "rectangle",
                                  "x0": 0,
                                  "x1": 0.33,
                                  "xref": "paper",
                                  "y0": 0.66,
                                  "y1": 0.99,
                                  "yref": "paper"
                                },
                                {
                                  "fillcolor": "rgb(255, 127, 14)",
                                  "line": {
                                    "color": "rgb(0, 0, 0)",
                                    "width": 1
                                  },
                                  "opacity": 0.9,
                                  "type": "rectangle",
                                  "x0": 0.33,
                                  "x1": 0.66,
                                  "xref": "paper",
                                  "y0": 0.66,
                                  "y1": 0.99,
                                  "yref": "paper"
                                },
                                {
                                  "fillcolor": "rgb(127, 127, 127)",
                                  "line": {
                                    "color": "rgb(0, 0, 0)",
                                    "width": 2
                                  },
                                  "opacity": 0.3,
                                  "type": "rectangle",
                                  "x0": 0.66,
                                  "x1": 0.99,
                                  "xref": "paper",
                                  "y0": 0.66,
                                  "y1": 0.99,
                                  "yref": "paper"
                                }
                              ],
                              xaxis = {
                                "autorange": True,
                                "range": [0.989694747864, 1.00064057995],
                                "showgrid": False,
                                "showline": False,
                                "showticklabels": False,
                                "title": "<br>",
                                "type": "linear",
                                "zeroline": False
                              },
                              yaxis = {
                                "autorange": True,
                                "range": [-0.0358637178721, 1.06395696354],
                                "showgrid": False,
                                "showline": False,
                                "showticklabels": False,
                                "title": "<br>",
                                "type": "linear",
                                "zeroline": False
                              }
                            )
                        },
                        config={
                            'displayModeBar': False
                        }
                    )

                ], className="four columns"),

                html.Div([
                    html.P("Vanguard 500 Index Fund seeks to track the performance of\
                     a benchmark index that meaures the investment return of large-capitalization stocks."),
                    html.P("Learn more about this portfolio's investment strategy and policy.")
                ], className="eight columns middle-aligned"),

            ], className="row "),

            # Row 3

            html.Br([]),

            html.Div([

                html.Div([
                    html.H6(["Equity characteristics as of 01/31/2018"], className="gs-header gs-table-header tiny-header"),
                    html.Table(make_dash_table(df_equity_char), className="tiny-header")
                ], className=" twelve columns"),

            ], className="row "),

            # Row 4

            html.Div([

                html.Div([
                    html.H6(["Equity sector diversification"], className="gs-header gs-table-header tiny-header"),
                    html.Table(make_dash_table(df_equity_diver), className="tiny-header")
                ], className=" twelve columns"),

            ], className="row "),

        ], className="subpage")

    ], className="page")

#%% Fees
feesMins = html.Div([  # page 4

        print_button(),

        html.Div([

            # Header
            loadHeaderInfo(),

            # Row 1

            html.Div([

                html.Div([
                    html.H6(["Expenses"],
                            className="gs-header gs-table-header padded")
                ], className="twelve columns"),

            ], className="row "),

            # Row 2

            html.Div([

                html.Div([
                    html.Strong(),
                    html.Table(make_dash_table(df_expenses)),
                    html.H6(["Minimums"],
                            className="gs-header gs-table-header padded"),
                    html.Table(make_dash_table(df_minimums))
                ], className="six columns"),

                html.Div([
                    html.Br([]),
                    html.Strong("Fees on $10,000 invested over 10 years"),
                    dcc.Graph(
                        id = 'graph-6',
                        figure = {
                            'data': [
                                go.Bar(
                                    x = ["Category Average", "This fund"],
                                    y = ["2242", "329"],
                                    marker = {"color": "rgb(53, 83, 255)"},
                                    name = "A"
                                ),
                                go.Bar(
                                    x = ["This fund"],
                                    y = ["1913"],
                                    marker = {"color": "#ADAAAA"},
                                    name = "B"
                                )
                            ],
                            'layout': go.Layout(
                                annotations = [
                                    {
                                      "x": -0.0111111111111,
                                      "y": 2381.92771084,
                                      "font": {
                                        "color": "rgb(0, 0, 0)",
                                        "family": "Raleway",
                                        "size": 10
                                      },
                                      "showarrow": False,
                                      "text": "$2,242",
                                      "xref": "x",
                                      "yref": "y"
                                    },
                                    {
                                      "x": 0.995555555556,
                                      "y": 509.638554217,
                                      "font": {
                                        "color": "rgb(0, 0, 0)",
                                        "family": "Raleway",
                                        "size": 10
                                      },
                                      "showarrow": False,
                                      "text": "$329",
                                      "xref": "x",
                                      "yref": "y"
                                    },
                                    {
                                      "x": 0.995551020408,
                                      "y": 1730.32432432,
                                      "font": {
                                        "color": "rgb(0, 0, 0)",
                                        "family": "Raleway",
                                        "size": 10
                                      },
                                      "showarrow": False,
                                      "text": "You save<br><b>$1,913</b>",
                                      "xref": "x",
                                      "yref": "y"
                                    }
                                  ],
                                  autosize = False,
                                  height = 150,
                                  width = 340,
                                  bargap = 0.4,
                                  barmode = "stack",
                                  hovermode = "closest",
                                  margin = {
                                    "r": 40,
                                    "t": 20,
                                    "b": 20,
                                    "l": 40
                                  },
                                  showlegend = False,
                                  title = "",
                                  xaxis = {
                                    "autorange": True,
                                    "range": [-0.5, 1.5],
                                    "showline": True,
                                    "tickfont": {
                                      "family": "Raleway",
                                      "size": 10
                                    },
                                    "title": "",
                                    "type": "category",
                                    "zeroline": False
                                  },
                                  yaxis = {
                                    "autorange": False,
                                    "mirror": False,
                                    "nticks": 3,
                                    "range": [0, 3000],
                                    "showgrid": True,
                                    "showline": True,
                                    "tickfont": {
                                      "family": "Raleway",
                                      "size": 10
                                    },
                                    "tickprefix": "$",
                                    "title": "",
                                    "type": "linear",
                                    "zeroline": False
                                  }
                            )
                        },
                        config={
                            'displayModeBar': False
                        }
                    )
                ], className="six columns"),

            ], className="row "),

            # Row 3

            html.Div([

                html.Div([
                    html.H6(["Fees"],
                            className="gs-header gs-table-header padded"),

                    html.Br([]),

                    html.Div([

                        html.Div([
                            html.Strong(["Purchase fee"])
                        ], className="three columns right-aligned"),

                        html.Div([
                            html.P(["None"])
                        ], className="nine columns")


                    ], className="row "),

                    html.Div([

                        html.Div([
                            html.Strong(["Redemption fee"])
                        ], className="three columns right-aligned"),

                        html.Div([
                            html.P(["None"])
                        ], className="nine columns")

                    ], className="row "),

                    html.Div([

                        html.Div([
                            html.Strong(["12b-1 fee"])
                        ], className="three columns right-aligned"),

                        html.Div([
                            html.P(["None"])
                        ], className="nine columns")

                    ], className="row "),

                    html.Div([

                        html.Div([
                            html.Strong(["Account service fee"])
                        ], className="three columns right-aligned"),

                        html.Div([
                            html.Strong(["Nonretirement accounts, traditional IRAs, Roth IRAs, UGMAs/UTMAs, SEP-IRAs, and education savings accounts (ESAs)"]),
                            html.P(["We charge a $20 annual account service fee for each Vanguard Brokerage Account, as well as each individual Vanguard mutual fund holding with a balance of less than $10,000 in an account. This fee does not apply if you sign up for account access on vanguard.com and choose electronic delivery of statements, confirmations, and Vanguard fund reports and prospectuses. This fee also does not apply to members of Flagship Select™, Flagship®, Voyager Select®, and Voyager® Services."]),
                            html.Br([]),
                            html.Strong(["SIMPLE IRAs"]),
                            html.P(["We charge participants a $25 annual account service fee for each fund they hold in their Vanguard SIMPLE IRA. This fee does not apply to members of Flagship Select, Flagship, Voyager Select, and Voyager Services."]),
                            html.Br([]),
                            html.Strong(["403(b)(7) plans"]),
                            html.P(["We charge participants a $15 annual account service fee for each fund they hold in their Vanguard 403(b)(7) account. This fee does not apply to members of Flagship Select, Flagship, Voyager Select, and Voyager Services."]),
                            html.Br([]),
                            html.Strong(["Individual 401(k) plans"]),
                            html.P(["We charge participants a $20 annual account service fee for each fund they hold in their Vanguard Individual 401(k) account. This fee will be waived for all participants in the plan if at least 1 participant qualifies for Flagship Select, Flagship, Voyager Select, and Voyager Services"]),
                            html.Br([]),
                        ], className="nine columns")

                    ], className="row ")

                ], className="twelve columns")

            ], className="row "),

        ], className="subpage")

    ], className="page")

#%% Distribution
distributions = html.Div([  # page 5

        print_button(),

        html.Div([

            # Header
            loadHeaderInfo(),

            # Row 1

            html.Div([

                html.Div([
                    html.H6(["Distributions"],
                            className="gs-header gs-table-header padded"),
                    html.Strong(["Distributions for this fund are scheduled quaterly"])
                ], className="twelve columns"),

            ], className="row "),

            # Row 2

            html.Div([

                html.Div([
                    html.Br([]),
                    html.H6(["Dividend and capital gains distributions"], className="gs-header gs-table-header tiny-header"),
                    html.Table(make_dash_table(df_dividend), className="tiny-header")
                ], className="twelve columns"),

            ], className="row "),

            # Row 3

            html.Div([

                html.Div([
                    html.H6(["Realized/unrealized gains as of 01/31/2018"], className="gs-header gs-table-header tiny-header")
                ], className=" twelve columns")

            ], className="row "),

            # Row 4

            html.Div([

                html.Div([
                    html.Table(make_dash_table(df_realized))
                ], className="six columns"),

                html.Div([
                    html.Table(make_dash_table(df_unrealized))
                ], className="six columns"),

            ], className="row "),

        ], className="subpage")

    ], className="page")

#%% News
newsReviews = html.Div([  # page 6

        print_button(),

        html.Div([

            # Header
            loadHeaderInfo(),

            # Row 1

            html.Div([

                html.Div([
                    html.H6('Vanguard News',
                            className="gs-header gs-text-header padded"),
                    html.Br([]),
                    html.P('10/25/16    The rise of indexing and the fall of costs'),
                    html.Br([]),
                    html.P("08/31/16    It's the index mutual fund's 40th anniversary: Let the low-cost, passive party begin")
                ], className="six columns"),

                html.Div([
                    html.H6("Reviews",
                            className="gs-header gs-table-header padded"),
                    html.Br([]),
                    html.Li('Launched in 1976.'),
                    html.Li('On average, has historically produced returns that have far outpaced the rate of inflation.*'),
                    html.Li("Vanguard Quantitative Equity Group, the fund's advisor, is among the world's largest equity index managers."),
                    html.Br([]),
                    html.P("Did you know? The fund launched in 1976 as Vanguard First Index Investment Trust—the nation's first index fund available to individual investors."),
                    html.Br([]),
                    html.P("* The performance of an index is not an exact representation of any particular investment, as you cannot invest directly in an index."),
                    html.Br([]),
                    html.P("Past performance is no guarantee of future returns. See performance data current to the most recent month-end.")
                ], className="six columns"),

            ], className="row ")

        ], className="subpage")

    ], className="page")

noPage = html.Div([  # 404

    html.P(["404 Page not found"])

    ], className="no-page")


app.config['suppress_callback_exceptions']=True

#%% Layout
app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    
#    html.Div(id='page-content')
    #%% First Page Overview
    #-----------------------------------------------------------------------------------------------------------------------------------
    html.Div([  # page 1
        print_button(),
        html.Div([
            # Header
            loadHeaderInfo(),            
            getDropDowns(),
            # ---------------- Row For History Scatter Plot Start -------------
            html.Div([
                html.Div([
                    html.H6("Performance",
                            className="gs-header gs-table-header padded"),
                    # table start                    
                        # ------------------------------------------------------------------------------
                         html.Div([
                            dt.DataTable(
                                # Initialise the rows
                                columns=['Month','Day','Year','Account','Title','MainCategory','Amount','Balance'],
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
                ], className="twelve columns")
            ], className="row "),
                            
            # ---------------- Row For History Scatter Plot End -------------
            # Row 3
            html.Div([
                html.Div([
                    html.H6("History",className="gs-header gs-table-header padded"),
                    # table start                    
                    # ------------------------------------------------------------------------------
                     html.Div([
                        #Scatter Plot
                        dcc.Graph(id='lineGraph',
                                  config={
                                        'displayModeBar': False
                                        })
                    ]),  
                    # ------------------------------------------------------------------------------                                                
                    # table end
                ], className="twelve columns")
            ], className="row "),

        ], className="subpage")
    ], className="page"),
    #-----------------------------------------------------------------------------------------------------------------------------------
        
    
    
    #%% Second Page Overview
    #-----------------------------------------------------------------------------------------------------------------------------------
    html.Div([  # page 2
        print_button(),
        html.Div([
            # Header
            loadHeaderInfo(),
            
            #----------------------------------------------------------------------------
            html.Div([
                html.Div([
                    html.H6("Expenses",
                            className="gs-header gs-table-header padded"),                    
                ], className="six columns"),
            ], className="row "),
            html.Div([
                html.Div([                    
                    dcc.Graph(id='categoryBarGraphExpenses',
                                  config={
                                        'displayModeBar': False
                                        })                                                                
                ], className="nine columns"),
                html.Div([                    
                    dcc.Graph(id='categoryGraphExpenses',
                                  config={
                                        'displayModeBar': False
                                        })                                                                
                ], className="three columns"),
            ], className="row "),
            html.Div([
                   
                html.Div([                                        
                    # table start                    
                        # ------------------------------------------------------------------------------                         
                            dt.DataTable(
                                # Initialise the rows
                                columns=['Month','Day','Year','Account','Title','MainCategory','Amount','Balance'],
                                rows=[{}],                            
                                row_selectable=False,
                                filterable=True,
                                sortable=True,
                                selected_row_indices=[],
                                max_rows_in_viewport = 7,
                                id='tableExpense'
                            ),
                        # ------------------------------------------------------------------------------                                                
                    # table end
                ], className="twelve columns"),
            ], className="row "),
            #----------------------------------------------------------------------------
        ], className="subpage")
    ], className="page"),
    #-----------------------------------------------------------------------------------------------------------------------------------
    #%% Third Page Overview
    #-----------------------------------------------------------------------------------------------------------------------------------
    html.Div([  # page 3
        print_button(),
        html.Div([
            # Header
            loadHeaderInfo(),            
            #----------------------------------------------------------------------------
            html.Div([
                html.Div([
                    html.H6("Income",
                            className="gs-header gs-table-header padded"),                    
                ], className="six columns"),
            ], className="row "),
            html.Div([
                html.Div([                    
                    dcc.Graph(id='categoryBarGraphIncome',
                                  config={
                                        'displayModeBar': False
                                        })                                                                
                ], className="nine columns"),                    
                html.Div([                    
                    dcc.Graph(id='categoryGraphIncome',
                                  config={
                                        'displayModeBar': False
                                        })                                                                
                ], className="three columns"),  
            ], className="row "),
            html.Div([                 
                html.Div([                                        
                    # table start                    
                        # ------------------------------------------------------------------------------                         
                            dt.DataTable(
                                # Initialise the rows
                                columns=['Month','Day','Year','Account','Title','MainCategory','Amount','Balance'],
                                rows=[{}],                            
                                row_selectable=False,
                                filterable=True,
                                sortable=True,
                                selected_row_indices=[],
                                max_rows_in_viewport = 7,
                                id='tableIncome'
                            ),
                        # ------------------------------------------------------------------------------                                                
                    # table end
                ], className="twelve columns"),                            
            ], className="row "),
            #----------------------------------------------------------------------------          
        ], className="subpage")
    ], className="page"),
    #-----------------------------------------------------------------------------------------------------------------------------------
    #%% Fourth Page Overview
    #-----------------------------------------------------------------------------------------------------------------------------------
    html.Div([  # page 4
        print_button(),
        html.Div([
            # Header
            loadHeaderInfo(),            
            #----------------------------------------------------------------------------
            html.Div([
                html.Div([
                    html.H6("Search Queries",
                            className="gs-header gs-table-header padded"),                    
                ], className="six columns"),
            ], className="row "),
            html.Div([
                html.Div([
                    html.Div('Category', className='three columns'),
                    html.Div(dcc.Dropdown(id='categorySearchSelector',options=onLoadGetAllCategories(),value='Food',className='nine columns')),                                                        
                ],className ='six columns'), 
            ], className="row "),            
            #----------------------------------------------------------------------------
              html.Div([                 
                html.Div([                                        
                    # table start                    
                        # ------------------------------------------------------------------------------                                                    
                            dt.DataTable(
                                # Initialise the rows
                                columns=['Month','Day','Year','Account','Title','MainCategory','Amount'],
                                rows=[{}],                            
                                row_selectable=False,
                                filterable=True,
                                sortable=True,
                                selected_row_indices=[],
                                max_rows_in_viewport = 10,
                                id='tableCategory'
                            ),
                        # ------------------------------------------------------------------------------                                                
                    # table end
                ], className="twelve columns"),                            
            #----------------------------------------------------------------------------             
                html.Div([ 
                        dcc.Graph(id='categorySearchGraph',
                                  config={
                                        'displayModeBar': False
                                        })                                                                
                ], className="five columns"),                            
                html.Div([ 
                        dcc.Graph(id='categorySearchGraphLine',
                                  config={
                                        'displayModeBar': False
                                        })                                                                
                ], className="six columns"),                            
            #----------------------------------------------------------------------------
            ], className="row "),
        ], className="subpage")
    ], className="page")
    #-----------------------------------------------------------------------------------------------------------------------------------
])

#%% Interaction Between Components / Controller
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
    dateAll = transactions.Date
    day = []
    month = []
    year = []
    for date in dateAll:
        dateSplit = date.split('/')
        day.append(dateSplit[1])
        month.append(dateSplit[0])
        year.append(dateSplit[2])
    
    transactions['Day'] = day
    transactions['Month'] = month
    transactions['Year'] = year
    #HERE
    transactions.Amount = pd.to_numeric(transactions.Amount)
    return transactions.to_dict('records')

@app.callback(
    Output('tableCategory', 'rows'), 
    [         
         Input(component_id='categorySearchSelector', component_property='value'),         
    ]
)
def update_tableCategory(category):
    """
    For user selections, return the relevant table
    """
    transactions = getAllAccounts(category)
    dateAll = transactions.Date
    day = []
    month = []
    year = []
    for date in dateAll:
        dateSplit = date.split('/')
        day.append(dateSplit[1])
        month.append(dateSplit[0])
        year.append(dateSplit[2])
    
    transactions['Day'] = day
    transactions['Month'] = month
    transactions['Year'] = year
    #HERE
    transactions.Amount = pd.to_numeric(transactions.Amount)
    
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

#%% Graphing Callbacks
@app.callback(
    Output(component_id='categorySearchGraphLine', component_property='figure'),
    [
        Input(component_id='categorySearchSelector', component_property='value')        
    ]
)
def updateCategorySearchGraphLine(subcategory):  
          
    transactions = getAllAccounts(subcategory)    
    
    # Add month and year to the data frame
    dateAll = transactions.Date
    day = []
    month = []
    year = []
    for date in dateAll:
        dateSplit = date.split('/')
        day.append(dateSplit[1])
        month.append(dateSplit[0])
        year.append(dateSplit[2])
    
    transactions['Day'] = day
    transactions['Month'] = month
    transactions['Year'] = year
    
    transactions.Amount = pd.to_numeric(transactions.Amount)
    getAllSumsByYear = transactions.groupby(['Year','Month']).Amount.sum()
    unstacked = getAllSumsByYear.unstack()
    unstacked = unstacked.fillna(0)
    monthlyValues = unstacked.get_values()
    
    yearSize = monthlyValues.shape[0]
    monthSize = monthlyValues.shape[1]
    
    summaryList = []
    
    for y in xrange(yearSize):
        yArray = []
        for m in xrange(monthSize):
            yArray.append(monthlyValues[y,m])
        summaryList.append(yArray)
    
    uniqueYear = np.unique(year).tolist()
    
    # Get monthly Means
    monthlyMeans = np.ndarray.tolist(unstacked.mean().get_values())
    summaryList.append(monthlyMeans)
    uniqueYear.append('Monthly Avg')    
    
    months = ['JAN', 'FEB', 'MAR', 'APR', 'MAY', 'JUN', 'JUL', 'AUG', 'SEP', 'OCT', 'NOV', 'DEC']
    
    
        #Draw the scatter plot
    figureList = []
    
    for yearIndex in xrange(len(summaryList)):  
        if yearIndex >= (len(summaryList)-2):
            figureList.append(go.Scatter(x=months, y=summaryList[yearIndex], mode='lines+markers',name=uniqueYear[yearIndex],visible=True))
        else:
            figureList.append(go.Scatter(x=months, y=summaryList[yearIndex], mode='lines+markers',name=uniqueYear[yearIndex],visible='legendonly'))
    
  
    figure = go.Figure(
        data=figureList,
        layout=go.Layout(
            autosize= True,
            margin = {
                "r": 40,
                "t": 30,
                "b": 30,
                "l": 40
              },
#                title='History Scatter Plot',
            legend=dict(orientation="v"),  
            height = 240,
            showlegend=True
        )
    )           
    return figure

@app.callback(
    Output(component_id='categorySearchGraph', component_property='figure'),
    [
        Input(component_id='categorySearchSelector', component_property='value')        
    ]
)
def updateCategorySearchGraph(subcategory):  
          
    transactions = getAllAccounts(subcategory)    
    
    # Add month and year to the data frame
    dateAll = transactions.Date
    day = []
    month = []
    year = []
    for date in dateAll:
        dateSplit = date.split('/')
        day.append(dateSplit[0])
        month.append(dateSplit[1])
        year.append(dateSplit[2])
    
    transactions['Day'] = day
    transactions['Month'] = month
    transactions['Year'] = year
    
    transactions.Amount = pd.to_numeric(transactions.Amount)
    getAllSumsByYear = transactions.groupby('Year').Amount.sum()
    overAllMeanSum = getAllSumsByYear.mean()
    
    months = ['JAN', 'FEB', 'MAR', 'APR', 'MAY', 'JUN', 'JUL', 'AUG', 'SEP', 'OCT', 'NOV', 'DEC']
    
    summaryList = []
    
    for y in getAllSumsByYear:
        yearArray=[]
        for m in xrange(len(months)):
            yearArray.append(y*-1)
        summaryList.append(yearArray) 
    
    yearArray=[]
    for m in xrange(len(months)):
        yearArray.append(overAllMeanSum*-1)
    summaryList.append(yearArray)
    
    uniqueYear = np.unique(year).tolist()
    uniqueYear.append('Mean of All Years')
    
    dataArray = []
    for m in getAllSumsByYear:
        m = round(m,2)
        if m>0:
            dataArray.append(m)
        else:
            dataArray.append(m*-1)
    
    overAllMeanSum = round(overAllMeanSum,2)
    if overAllMeanSum>0:        
        dataArray.append(overAllMeanSum)
    else:
        dataArray.append(overAllMeanSum*-1.00)
    
    
    figure = go.Figure(
        data=[
             go.Bar(x=dataArray, 
                    y=uniqueYear,
                    text=dataArray,
                    textposition = 'auto',
                    orientation = 'h'
                    )           
        ],
        layout=go.Layout(
            autosize= True,
            margin = {
                "r": 40,
                "t": 30,
                "b": 30,
                "l": 40
              },            
            height = 240,            
        )
    )
        
#    #Draw the scatter plot
#    figureList = []
#    
#    for yearIndex in xrange(len(summaryList)):  
#        figureList.append(go.Scatter(x=months, y=summaryList[yearIndex], mode='lines+markers',name=uniqueYear[yearIndex]))
#    
#  
#    figure = go.Figure(
#        data=figureList,
#        layout=go.Layout(
#            autosize= True,
#            margin = {
#                "r": 40,
#                "t": 30,
#                "b": 30,
#                "l": 40
#              },
##                title='History Scatter Plot',
##                legend=dict(orientation="v"),  
#            height = 240,
#            showlegend=True
#        )
#    )           
    return figure

@app.callback(
    Output(component_id='lineGraph', component_property='figure'),
    [
        Input(component_id='accountSelector', component_property='value'),
        Input(component_id='categorySelector', component_property='value'),
        Input(component_id='yearSelector', component_property='value'),
        Input(component_id='monthSelector', component_property='value')
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

@app.callback(
    Output('tableExpense', 'rows'), 
    [
         Input(component_id='accountSelector', component_property='value'),
         Input(component_id='categorySelector', component_property='value'),
         Input(component_id='yearSelector', component_property='value'),
         Input(component_id='monthSelector', component_property='value')
    ]
)
def update_tableExpense(account,category,year,month):
    """
    For user selections, return the relevant table
    """
    transactions = getTransactionResultsForSubcategory(account,category,year,'Credit',month)        
    dateAll = transactions.Date
    day = []
    month = []
    year = []
    for date in dateAll:
        dateSplit = date.split('/')
        day.append(dateSplit[1])
        month.append(dateSplit[0])
        year.append(dateSplit[2])
    
    transactions['Day'] = day
    transactions['Month'] = month
    transactions['Year'] = year
    #HERE
    transactions.Amount = pd.to_numeric(transactions.Amount)
    return transactions.to_dict('records')

@app.callback(
    Output('tableIncome', 'rows'), 
    [
         Input(component_id='accountSelector', component_property='value'),
         Input(component_id='categorySelector', component_property='value'),
         Input(component_id='yearSelector', component_property='value'),
         Input(component_id='monthSelector', component_property='value')
    ]
)
def update_tableIncome(account,category,year,month):
    """
    For user selections, return the relevant table
    """
    transactions = getTransactionResultsForSubcategory(account,category,year,'Debit',month)        
    dateAll = transactions.Date
    day = []
    month = []
    year = []
    for date in dateAll:
        dateSplit = date.split('/')
        day.append(dateSplit[1])
        month.append(dateSplit[0])
        year.append(dateSplit[2])
    
    transactions['Day'] = day
    transactions['Month'] = month
    transactions['Year'] = year
    #HERE
    transactions.Amount = pd.to_numeric(transactions.Amount)
    return transactions.to_dict('records')

#Update Category Bar Graph Income    
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

#%% Update page
@app.callback(dash.dependencies.Output('page-content', 'children'),
              [dash.dependencies.Input('url', 'pathname')])
def display_page(pathname):
    if pathname == '/' or pathname == '/overview':
        return overview
    elif pathname == '/price-performance':
        return pricePerformance
    elif pathname == '/portfolio-management':
        return portfolioManagement
    elif pathname == '/fees':
        return feesMins
    elif pathname == '/distributions':
        return distributions
    elif pathname == '/news-and-reviews':
        return newsReviews
    elif pathname == '/myOverview':
        return myOverview
    elif pathname == '/full-view':
        return overview,pricePerformance,portfolioManagement,feesMins,distributions,newsReviews
    else:
        return noPage


external_css = ["https://cdnjs.cloudflare.com/ajax/libs/normalize/7.0.0/normalize.min.css",
                "https://cdnjs.cloudflare.com/ajax/libs/skeleton/2.0.4/skeleton.min.css",
                "//fonts.googleapis.com/css?family=Raleway:400,300,600",
#                "https://codepen.io/bcd/pen/KQrXdb.css",
                "https://maxcdn.bootstrapcdn.com/font-awesome/4.7.0/css/font-awesome.min.css",
                "https://codepen.io/MGDev/pen/yEoRjg.css"
                ]

for css in external_css:
    app.css.append_css({"external_url": css})

external_js = ["https://code.jquery.com/jquery-3.2.1.min.js",
               "https://codepen.io/bcd/pen/YaXojL.js",]

for js in external_js:
    app.scripts.append_script({"external_url": js})


if __name__ == '__main__': 
    os.system('python combineData.py')
    app.run_server(
            debug=True,
            host='0.0.0.0',
            port=8050
        )
