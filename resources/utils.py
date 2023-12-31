import mailbox
import email
from email.header import decode_header, make_header
from multiprocessing import current_process
from smtpd import SMTPServer
from resources import systemVariables
import sqlite3
import json
import datetime
import logging
import re
import pandas as pd
import plotly
import plotly.express as px
import plotly.graph_objects as go

logging.basicConfig(filename=systemVariables.logFilePath, filemode='a', format='%(asctime)s - %(levelname)s - %(message)s',level=logging.INFO)
logger = logging.getLogger(__name__)

class EmailRemoteProcessor(SMTPServer):
    """
    Class representing processing emails from remote SMTP cliens
    """
    def process_message(self, peer, mailfrom, rcpttos, data, **kwargs):
        self.email = email.message_from_bytes(data)
        self.message = Email(
            subject=make_header(decode_header(self.email.get('subject'))),
            date=self.email.get('date'),
            body=self.email.get_payload(),
            sender=self.email.get('from'),
            receiver=self.email.get('to'),
            contentType=self.email.get_content_type()
        )
        logger.info(self.message)
        self.newExpense = BudgetDatabase(systemVariables.budgetDatabasesPath)
        self.newExpense.SetNewExpenses(timestamp=self.message.GetProperDateFormat(),date=self.message.GetProperDateFormat(),name=self.message.subject,value=self.message.GetExpenseFromSubject(),was_payed=True)
        return self.accept()

class EmailLocalProcessor:
    """
    Class representing processing emails from local inbox file
    """
    def __init__(self,path):
        self.path = path
        return

    def OpenMailbox(self):
        self.mbox = mailbox.mbox(self.path)
        self.mbox.lock()
        return self.mbox

    def CloseMailbox(self):
        self.mbox.unlock()
        return
    
    def __str__(self):
        return 'EmailProcessor %s -- %s' % (self.path, self.mbox)

class Email:
    """
    Class representing email structure
    """
    def __init__(self,subject=None,date=None,sender=None,receiver=None,contentType=None,messageid=None,body=None):
        """
        Create Email object

        :param subject=None,date=None,sender=None,receiver=None,contentType=None,messageid=None,body=None
        :return email object 
        """
        self.subject = subject
        self.date = date
        self.body = body
        self.sender = sender
        self.receiver = receiver
        self.contentType = contentType
        self.messageid = messageid
        return
    
    def ParseHtmlBody(self):
        """
        Parse HTML body of email
        """
        #TODO
        return

    def GetEmailBody(self):
        """
        Print Email body
        """
        return '%s' % (self.body)

    def GetExpenseFromSubject(self):
        """
        Get Expense values from Email subject
        """
        expense = re.search(r'(-)(\d*\,\d{2})',str(self.subject))
        if expense:
            return float(expense.group(2).replace(',','.'))
    
    def GetProperDateFormat(self):
        """
        Get Proper Date Format from email
        """
        original_date = datetime.datetime.strptime(self.date,'%a, %d %b %Y %H:%M:%S %z')
        year = original_date.strftime('%Y')
        month = original_date.strftime('%m')
        day = original_date.strftime('%d')
        return str(year+'-'+month+'-'+day)

    def __str__(self):
        return 'Email %s -- Date: %s -- Subject: %s -- From: %s -- To: %s -- Content-Type: %s' % (self.messageid, self.date, self.subject, self.sender, self.receiver, self.contentType)

class BudgetDatabase:
    """
    Class representing operations in budget database
    """
    def __init__(self,path=None):
        self.path = path
        self.CreateDatabase(self.path)
        return
    
    def CreateDatabase(self,path=None):
        self.path = path
        open(self.path,'a+')
        self.conn = sqlite3.connect(self.path)
        self.cur = self.conn.cursor()
        self.cur.execute(
            """
            CREATE TABLE IF NOT EXISTS [Incomes] ( 
	            [IncomeId] INTEGER NOT NULL PRIMARY KEY, 
	            [TIMESTAMP] INTEGER(10) NOT NULL,
                [DATE] TEXT NOT NULL,
                [VALUE] REAL(50) NOT NULL,
                [NAME] TEXT NOT NULL
            );
            """
        )
        self.cur = self.conn.cursor()
        self.cur.execute(
            """
            CREATE TABLE IF NOT EXISTS [Expenses] (
                [ExpenseId] INTEGER NOT NULL PRIMARY KEY, 
                [TIMESTAMP] INTEGER(10) NOT NULL,
                [DATE] TEXT NOT NULL,
                [VALUE] REAL(50) NOT NULL,
                [NAME] TEXT NOT NULL,
                [CATEGORY] INTEGER(2) NOT NULL,
                [WAS_PAYED] INTEGER NOT NULL,
                [TYPE] INTEGER(2) NOT NULL
            );
            """
        )
        self.cur = self.conn.cursor()
        self.cur.execute(
            """
            CREATE TABLE IF NOT EXISTS [Investments] (
                [InvestmentId] INTEGER NOT NULL PRIMARY KEY, 
                [TIMESTAMP] INTEGER(10) NOT NULL,
                [DATE] TEXT NOT NULL,
                [VALUE] REAL(50) NOT NULL,
                [GOAL] REAL(50) NOT NULL,
                [NAME] TEXT NOT NULL,
                [WAS_PAYED] INTEGER NOT NULL
            );
            """
        )
        return

    def GetAllIncomes(self,desc_order=True):
        self.conn = sqlite3.connect(self.path)
        self.cur = self.conn.cursor()
        if desc_order:
            self.allIncomes = self.cur.execute('SELECT * FROM Incomes ORDER BY TIMESTAMP DESC;').fetchall()
        else:
            self.allIncomes = self.cur.execute('SELECT * FROM Incomes ORDER BY TIMESTAMP ASC;').fetchall()
        return self.allIncomes

    def GetIncome(self,id):
        self.id = id
        self.conn = sqlite3.connect(self.path)
        self.cur = self.conn.cursor()
        self.income = self.cur.execute('SELECT * FROM Incomes WHERE IncomeId='+str(self.id)+';')
        return self.income

    def GetLatestIncome(self):
        self.conn = sqlite3.connect(self.path)
        self.cur = self.conn.cursor()
        self.income = self.cur.execute('SELECT * FROM Incomes ORDER BY TIMESTAMP DESC LIMIT 1;').fetchall()
        return self.income

    def GetIncomesByDate(self,delta):
        self.delta = delta
        self.lastNdays = int((datetime.datetime.now() - datetime.timedelta(days=self.delta)).timestamp())
        self.delta_timestamp = datetime.timedelta(days=self.delta)
        self.conn = sqlite3.connect(self.path)
        self.cur = self.conn.cursor()
        self.FoundedIncomes = self.cur.execute('SELECT * FROM Incomes WHERE TIMESTAMP > '+str(self.lastNdays)+' ORDER BY TIMESTAMP DESC;').fetchall()
        return self.FoundedIncomes

    def GetIncomeByDateRange(self,start_date,end_date):
        self.start_date = start_date
        self.end_date = end_date
        self.conn = sqlite3.connect(self.path)
        self.cur = self.conn.cursor()
        self.FoundedIncomes = self.cur.execute('SELECT * FROM Incomes WHERE TIMESTAMP > '+str(self.EpochConverter(self.start_date))+' AND TIMESTAMP < '+str(self.EpochConverter(self.end_date))+' ORDER BY TIMESTAMP DESC;').fetchall()
        return self.FoundedIncomes

    def GetAllExpenses(self,desc_order=True):
        self.conn = sqlite3.connect(self.path)
        self.cur = self.conn.cursor()
        if desc_order:
            self.allExpenses = self.cur.execute('SELECT * FROM Expenses ORDER BY TIMESTAMP DESC;').fetchall()
        else:
            self.allExpenses = self.cur.execute('SELECT * FROM Expenses ORDER BY TIMESTAMP ASC;').fetchall()
        return self.allExpenses

    def GetExpenses(self,id):
        self.id = id
        self.conn = sqlite3.connect(self.path)
        self.cur = self.conn.cursor()
        self.income = self.cur.execute('SELECT * FROM Expenses WHERE ExpenseId='+str(self.id)+';')
        return self.income

    def GetExpensesByDate(self,delta):
        self.delta = delta
        self.lastNdays = int((datetime.datetime.now() - datetime.timedelta(days=self.delta)).timestamp())
        self.delta_timestamp = datetime.timedelta(days=self.delta)
        self.conn = sqlite3.connect(self.path)
        self.cur = self.conn.cursor()
        self.FoundedExpenses = self.cur.execute('SELECT * FROM Expenses WHERE TIMESTAMP > '+str(self.lastNdays)+' ORDER BY TIMESTAMP DESC;').fetchall()
        return self.FoundedExpenses

    def GetExpensesByDateRange(self,start_date,end_date):
        self.start_date = start_date
        self.end_date = end_date
        self.conn = sqlite3.connect(self.path)
        self.cur = self.conn.cursor()
        self.FoundedExpenses = self.cur.execute('SELECT * FROM Expenses WHERE TIMESTAMP > '+str(self.EpochConverter(self.start_date))+' AND TIMESTAMP < '+str(self.EpochConverter(self.end_date))+' ORDER BY TIMESTAMP DESC;').fetchall()
        return self.FoundedExpenses

    def GetExpensesSinceLastIncomes(self):
        self.latestIncome = pd.DataFrame(self.GetLatestIncome(),columns=['index','timestamp','date','value','name'])
        self.end_date = int((datetime.datetime.now()).timestamp())
        if self.latestIncome.empty:
            self.start_date = self.end_date
        else:
            self.start_date = int(self.latestIncome['timestamp'])
        self.conn = sqlite3.connect(self.path)
        self.cur = self.conn.cursor()
        self.FoundedExpenses = self.cur.execute('SELECT * FROM Expenses WHERE TIMESTAMP >= '+str(self.start_date)+' AND TIMESTAMP <= '+str(self.end_date)+' ORDER BY TIMESTAMP DESC;').fetchall()
        return self.FoundedExpenses

    def SetNewIncomes(self, timestamp=0, date=0, value=0, name='income'):
        self.timestamp = self.EpochConverter(timestamp)
        self.date = date
        self.name = name
        self.value = value
        self.conn = sqlite3.connect(self.path)
        self.cur = self.conn.cursor()
        self.income = self.cur.execute("INSERT INTO Incomes (TIMESTAMP,DATE,VALUE,NAME) VALUES (%s, '%s', %s, '%s');" % (self.timestamp, self.date, self.value, self.name))
        self.conn.commit()
        logger.info('New income has been added - value: '+str(self.value)+' name: '+str(self.name))
        return 'New Income: '+str(self.value)+' PLN'

    def SetNewExpenses(self, timestamp=0, date=0, name='expenses', category=8, value=0, was_payed=False,type=1):
        self.timestamp = self.EpochConverter(timestamp)
        self.date = date
        self.name = name
        self.category = systemVariables.ExpensesCategories[category]
        self.value = value
        self.was_payed = was_payed
        self.type = systemVariables.ExpensesTypes[type]
        self.conn = sqlite3.connect(self.path)
        self.cur = self.conn.cursor()
        self.expense = self.cur.execute("INSERT INTO Expenses (TIMESTAMP,DATE,VALUE,NAME,CATEGORY,WAS_PAYED,TYPE) VALUES (%s, '%s', %s, '%s', '%s', %s, '%s');" % (self.timestamp, self.date, self.value, self.name, self.category, self.was_payed, self.type))
        self.conn.commit()
        logger.info('New expense has been added - value: '+str(self.value)+' name: '+str(self.name))
        return 'New Expense: '+str(self.value)+' PLN'
    
    def DelIncomes(self, id):
        self.id = id
        self.conn = sqlite3.connect(self.path)
        self.cur = self.conn.cursor()
        self.income = self.cur.execute('DELETE FROM Incomes WHERE IncomeId=%s;' % (self.id))
        self.conn.commit()
        logger.info('Income has been deleted - id: '+str(self.id))
        return 'Income has been deleted - id: '+str(self.id)

    def DelExpenses(self, id):
        self.id = id
        self.conn = sqlite3.connect(self.path)
        self.cur = self.conn.cursor()
        self.expense = self.cur.execute('DELETE FROM Expenses WHERE ExpenseId=%s;' % (self.id))
        self.conn.commit()
        logger.info('Expense has been deleted - id: '+str(self.id))
        return 'Expense has been deleted - id: '+str(self.id)

    def UpdateIncome(self,id, timestamp, date, value, name):
        self.id = id
        self.timestamp = self.EpochConverter(timestamp)
        self.date = date
        self.name = name
        self.value = value
        self.conn = sqlite3.connect(self.path)
        self.cur = self.conn.cursor()
        self.income = self.cur.execute("UPDATE Incomes SET TIMESTAMP=%s,DATE='%s',VALUE=%s,NAME='%s' WHERE IncomeId=%s;" % (self.timestamp, self.date, self.value, self.name,self.id))
        self.conn.commit()
        logger.info('Income has been updated - id:'+str(self.id)+' timestamp:'+str(self.timestamp)+' date:'+str(self.date)+' value: '+str(self.value)+' name: '+str(self.name))
        return 'Income has been updated - id: '+str(self.id)+' timestamp: '+str(self.timestamp)+' date: '+str(self.date)+' value: '+str(self.value)+' name: '+str(self.name)

    def UpdateExpenses(self,id, timestamp, date, value, name, category, was_payed, type):
        self.id = id
        self.timestamp = self.EpochConverter(timestamp)
        self.date = date
        self.name = name
        self.value = value
        self.category = systemVariables.ExpensesCategories[int(category)]
        self.was_payed = was_payed
        self.type = systemVariables.ExpensesTypes[int(type)]
        self.conn = sqlite3.connect(self.path)
        self.cur = self.conn.cursor()
        self.income = self.cur.execute("UPDATE Expenses SET TIMESTAMP=%s,DATE='%s',VALUE=%s,NAME='%s',CATEGORY='%s',WAS_PAYED=%s,TYPE='%s' WHERE ExpenseId=%s;" % (self.timestamp, self.date, self.value, self.name, self.category, self.was_payed, self.type, self.id))
        self.conn.commit()
        logger.info('Expense has been updated - id:'+str(self.id)+' timestamp:'+str(self.timestamp)+' date:'+str(self.date)+' value: '+str(self.value)+' name: '+str(self.name)+' category: '+str(self.category)+' was_payed: '+str(self.was_payed)+' type: '+str(self.type))
        return 'Expense has been updated - id:'+str(self.id)+' timestamp:'+str(self.timestamp)+' date:'+str(self.date)+' value: '+str(self.value)+' name: '+str(self.name)+' category: '+str(self.category)+' was_payed: '+str(self.was_payed)+' type: '+str(self.type)
    
    def EpochConverter(self,date,convert=True):
        self.date = date
        if convert:
            self.outputTime = datetime.datetime.strptime(self.date, '%Y-%m-%d').timestamp()
        else:
            self.outputTime = datetime.datetime.fromtimestamp(self.date)
        return self.outputTime
    
    def GetAllSavings(self,desc_order=True):
        self.conn = sqlite3.connect(self.path)
        self.cur = self.conn.cursor()
        if desc_order:
            self.allInvestments = self.cur.execute('SELECT * FROM Expenses WHERE type == "savings/investments" ORDER BY TIMESTAMP DESC;').fetchall()
        else:
            self.allInvestments = self.cur.execute('SELECT * FROM Expenses WHERE type == "savings/investments" ORDER BY TIMESTAMP ASC;').fetchall()
        return self.allInvestments
    
    def GetAllInvestments(self,desc_order=True):
        self.conn = sqlite3.connect(self.path)
        self.cur = self.conn.cursor()
        if desc_order:
            self.allInvestments = self.cur.execute('SELECT * FROM Investments ORDER BY TIMESTAMP DESC;').fetchall()
        else:
            self.allInvestments = self.cur.execute('SELECT * FROM Investments ORDER BY TIMESTAMP ASC;').fetchall()
        return self.allInvestments
    
    def GetInvestment(self,id):
        self.id = id
        self.conn = sqlite3.connect(self.path)
        self.cur = self.conn.cursor()
        self.income = self.cur.execute('SELECT * FROM Investments WHERE InvestmentId='+str(self.id)+';')
        return self.income
    
    def GetSavingByDate(self,delta):
        self.delta = delta
        self.lastNdays = int((datetime.datetime.now() - datetime.timedelta(days=self.delta)).timestamp())
        self.delta_timestamp = datetime.timedelta(days=self.delta)
        self.conn = sqlite3.connect(self.path)
        self.cur = self.conn.cursor()
        self.FoundedIncomes = self.cur.execute('SELECT * FROM Expenses WHERE TIMESTAMP > '+str(self.lastNdays)+' AND type == "savings/investments" ORDER BY TIMESTAMP DESC;').fetchall()
        return self.FoundedIncomes
    
    def SetNewInvestment(self, timestamp=0, date=0, value=0, goal=0, name='Custom Investment', was_payed=False):
        self.timestamp = self.EpochConverter(timestamp)
        self.date = date
        self.name = name
        self.value = value
        self.goal = goal
        self.was_payed = was_payed
        self.conn = sqlite3.connect(self.path)
        self.cur = self.conn.cursor()
        self.investment = self.cur.execute("INSERT INTO Investments (TIMESTAMP,DATE,VALUE,GOAL,NAME,WAS_PAYED) VALUES (%s, '%s', %s, %s, '%s',%s);" % (self.timestamp, self.date, self.value, self.goal, self.name,self.was_payed))
        self.conn.commit()
        logger.info('New investment has been added - value: '+str(self.goal)+' name: '+str(self.name))
        return 'New Investment: '+str(self.name)
    
    def UpdateInvestment(self,id, timestamp, date, value, goal, name, was_payed):
        self.id = id
        self.timestamp = self.EpochConverter(timestamp)
        self.date = date
        self.name = name
        self.value = value
        self.goal = goal
        self.was_payed = was_payed
        self.conn = sqlite3.connect(self.path)
        self.cur = self.conn.cursor()
        self.investment = self.cur.execute("UPDATE Investments SET TIMESTAMP=%s,DATE='%s',VALUE=%s,GOAL=%s,NAME='%s',WAS_PAYED=%s WHERE InvestmentId=%s;" % (self.timestamp, self.date, self.value, self.goal, self.name, self.was_payed, self.id))
        self.conn.commit()
        logger.info('Investment has been updated - id:'+str(self.id)+' timestamp:'+str(self.timestamp)+' date:'+str(self.date)+' value: '+str(self.value)+' name: '+str(self.name)+' goal: '+str(self.goal))
        return 'Investment has been updated - id: '+str(self.id)+' timestamp: '+str(self.timestamp)+' date: '+str(self.date)+' value: '+str(self.value)+' name: '+str(self.name)+' goal: '+str(self.goal)
    
    def DelInvestment(self, id):
        self.id = id
        self.conn = sqlite3.connect(self.path)
        self.cur = self.conn.cursor()
        self.investment = self.cur.execute('DELETE FROM Investments WHERE InvestmentId=%s;' % (self.id))
        self.conn.commit()
        logger.info('Investment has been deleted - id: '+str(self.id))
        return 'Investment has been deleted - id: '+str(self.id)

class Vizualizer(BudgetDatabase):
    """
    Class representing visualizations from Budget DB
    """
    def PrintAllBudget(self):
        income = pd.DataFrame(self.GetAllIncomes(desc_order=False),columns=['index','timestamp','date','value','name'])
        expenses = pd.DataFrame(self.GetAllExpenses(desc_order=False),columns=['index','timestamp','date','value','name','category','was_payed','type']).query("category != 'savings'")
        savings = pd.DataFrame(self.GetAllExpenses(desc_order=False),columns=['index','timestamp','date','value','name','category','was_payed','type']).query("category == 'savings'")
        income['type'] = 'income'
        expenses['type'] = 'expenses'
        savings['type'] = 'savings'
        data = income.append(expenses).append(savings)
        fig = px.bar(data,x='date',y='value',color="type", title='Budget summary',barmode='stack')
        average = px.line(expenses,x='date',y='value').update_traces(line_color="red")
        fig.add_traces(average.data)
        plot_json = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
        return plot_json

    def PrintBudgetSinceLastIncome(self):
        income = pd.DataFrame(self.GetLatestIncome(),columns=['index','timestamp','date','value','name'])
        expenses = pd.DataFrame(self.GetExpensesSinceLastIncomes(),columns=['index','timestamp','date','value','name','category','was_payed','type'])
        result = income['value'].sum() -  expenses['value'].sum()
        try:
            usage = (expenses['value'].sum() / income['value'].sum()) * 100
        except ZeroDivisionError:
            usage = 0
        return income['value'].sum(),expenses['value'].sum(),usage,result

    def PrintLast30DaysBudget(self):
        income = pd.DataFrame(self.GetIncomesByDate(30),columns=['index','timestamp','date','value','name'])
        expenses = pd.DataFrame(self.GetExpensesByDate(30),columns=['index','timestamp','date','value','name','category','was_payed','type'])
        result = income['value'].sum() -  expenses['value'].sum()
        try:
            usage = (expenses['value'].sum() / income['value'].sum()) * 100
        except ZeroDivisionError:
            usage = 0
        return income['value'].sum(),expenses['value'].sum(),usage,result

    def PrintLast30DaysExpenses(self):
        expenses = pd.DataFrame(self.GetExpensesByDate(30),columns=['index','timestamp','date','value','name','category','was_payed','type'])
        fig = px.pie(expenses,values='value',names='category',title='Last 30 days expenses by category')
        plot_json = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
        return plot_json

    def PrintExpensesSinceLastIncome(self):
        expenses = pd.DataFrame(self.GetExpensesSinceLastIncomes(),columns=['index','timestamp','date','value','name','category','was_payed','type'])
        fig = px.pie(expenses,values='value',names='category',title='Current expenses - time range between last income and current date')
        plot_json = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
        return plot_json
    
    def PrintExpensesSinceLastIncomeByType(self):
        expenses = pd.DataFrame(self.GetExpensesSinceLastIncomes(),columns=['index','timestamp','date','value','name','category','was_payed','type']).query("was_payed == 1")
        income = pd.DataFrame(self.GetLatestIncome(),columns=['index','timestamp','date','value','name'])
        expenses_unpaid = pd.DataFrame(self.GetAllExpenses(desc_order=False),columns=['index','timestamp','date','value','name','category','was_payed','type']).query("was_payed == 0")
        expenses_unpaid['type'] = 'unpaid expenses'
        income['type'] = 'unclassified income'
        income['value'] = income['value'] - sum(expenses['value']) - sum(expenses_unpaid['value'])
        data = income.append(expenses).append(expenses_unpaid)
        fig = px.pie(data,values='value',names='type',title='Current expenses - 50/30/20 budget')
        plot_json = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
        return plot_json

    def PrintPreviousYearsBudget(self):
        income = pd.DataFrame(self.GetAllIncomes(desc_order=False),columns=['index','timestamp','date','value','name'])
        expenses = pd.DataFrame(self.GetAllExpenses(desc_order=False),columns=['index','timestamp','date','value','name','category','was_payed','type']).query("category != 'savings'")
        savings = pd.DataFrame(self.GetAllExpenses(desc_order=False),columns=['index','timestamp','date','value','name','category','was_payed','type']).query("category == 'savings'")
        income['type'] = 'income'
        expenses['type'] = 'expenses'
        savings['type'] = 'savings'
        data = income.append(expenses).append(savings)
        if not data.empty:
            date_extracted = data['date'].str.split('-',expand=True)
            data['year'] = date_extracted[0]
            fig = px.bar(data,x='year',y='value',color="type", title='Budget trends',barmode="group")
            plot_json = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
            return plot_json

    def PrintPreviousMonthsExpenses(self):
        expenses = pd.DataFrame(self.GetAllExpenses(desc_order=False),columns=['index','timestamp','date','value','name','category','was_payed','type'])
        currentYear = int(datetime.datetime.now().year)
        if not expenses.empty:
            date_extracted = expenses['date'].str.split('-',expand=True)
            expenses['year'] = date_extracted[0]
            expenses['month'] = date_extracted[1]
            currentExpenses = expenses.query("year == '{}'".format(currentYear))
            fig = px.bar(currentExpenses,x='month',y='value',color="category", title='Expenses trends',barmode="stack")
            plot_json = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
            return plot_json
        
    def PrintPreviousMonthsExpensesByType(self):
        expenses = pd.DataFrame(self.GetAllExpenses(desc_order=False),columns=['index','timestamp','date','value','name','category','was_payed','type'])
        currentYear = int(datetime.datetime.now().year)
        if not expenses.empty:
            date_extracted = expenses['date'].str.split('-',expand=True)
            expenses['year'] = date_extracted[0]
            expenses['month'] = date_extracted[1]
            currentExpenses = expenses.query("year == '{}'".format(currentYear))
            fig = px.bar(currentExpenses,x='month',y='value',color="type", title='Expenses trends by Type',barmode="stack")
            plot_json = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
            return plot_json

    def PrintPreviousMonthsExpensesHistogram(self):
        expenses = pd.DataFrame(self.GetAllExpenses(desc_order=False),columns=['index','timestamp','date','value','name','category','was_payed','type'])
        currentYear = int(datetime.datetime.now().year)
        if not expenses.empty:
            date_extracted = expenses['date'].str.split('-',expand=True)
            expenses['year'] = date_extracted[0]
            expenses['month'] = date_extracted[1]
            currentExpenses = expenses.query("year == '{}'".format(currentYear))
            fig = px.histogram(currentExpenses,x='month',y='value',color="category",barnorm='percent',title='Expenses trends - percentage')
            plot_json = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
            return plot_json
        
    def PrintPreviousMonthsExpensesHistogramByType(self):
        expenses = pd.DataFrame(self.GetAllExpenses(desc_order=False),columns=['index','timestamp','date','value','name','category','was_payed','type'])
        currentYear = int(datetime.datetime.now().year)
        if not expenses.empty:
            date_extracted = expenses['date'].str.split('-',expand=True)
            expenses['year'] = date_extracted[0]
            expenses['month'] = date_extracted[1]
            currentExpenses = expenses.query("year == '{}'".format(currentYear))
            fig = px.histogram(currentExpenses,x='month',y='value',color="type",barnorm='percent',title='Expenses trends by Type - percentage')
            plot_json = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
            return plot_json

    def PrintPreviousExpenses(self):
        expenses = pd.DataFrame(self.GetAllExpenses(desc_order=False),columns=['index','timestamp','date','value','name','category','was_payed','type'])
        if not expenses.empty:
            date_extracted = expenses['date'].str.split('-',expand=True)
            expenses['year'] = date_extracted[0]
            expenses['month'] = date_extracted[1]
            fig = px.bar(expenses,x='year',y='value',color="category", title='Expenses trends (all)',barmode="stack")
            plot_json = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
            return plot_json
        
    def PrintPreviousExpensesHistogram(self):
        expenses = pd.DataFrame(self.GetAllExpenses(desc_order=False),columns=['index','timestamp','date','value','name','category','was_payed','type'])
        if not expenses.empty:
            date_extracted = expenses['date'].str.split('-',expand=True)
            expenses['year'] = date_extracted[0]
            expenses['month'] = date_extracted[1]
            fig = px.histogram(expenses,x='year',y='value',color="category",barnorm='percent', title='Expenses trends (all) - percentage')
            plot_json = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
            return plot_json

    def PrintLast365DaysExpenses(self):
        expenses = pd.DataFrame(self.GetExpensesByDate(365),columns=['index','timestamp','date','value','name','category','was_payed','type'])
        fig = px.pie(expenses,values='value',names='category',title='Last 1 year expenses by category')
        plot_json = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
        return plot_json
    
    def PrintSavingsTrends(self):
        investments = pd.DataFrame(self.GetAllSavings(desc_order=False),columns=['index','timestamp','date','value','name','category','was_payed','type'])
        savings = pd.DataFrame(self.GetAllExpenses(desc_order=False),columns=['index','timestamp','date','value','name','category','was_payed','type']).query("category == 'savings'")
        retirement = pd.DataFrame(self.GetAllExpenses(desc_order=False),columns=['index','timestamp','date','value','name','category','was_payed','type']).query("category == 'retirement'")
        vacation = pd.DataFrame(self.GetAllExpenses(desc_order=False),columns=['index','timestamp','date','value','name','category','was_payed','type']).query("category == 'vacation'")
        savings['type'] = 'savings'
        retirement['type'] = 'retirement'
        vacation['type'] = 'vacation'
        investments['type'] = 'investments'
        data = investments.append(savings).append(retirement).append(vacation)
        if not data.empty:
            date_extracted = data['date'].str.split('-',expand=True)
            data['year'] = date_extracted[0]
            fig = px.bar(data,x='year',y='value',color="type", title='Savings trends',barmode="group")
            plot_json = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
            return plot_json
        
    def PrintPreviousYearSavings(self):
        investments = pd.DataFrame(self.GetSavingByDate(365),columns=['index','timestamp','date','value','name','category','was_payed','type'])
        savings = pd.DataFrame(self.GetExpensesByDate(365),columns=['index','timestamp','date','value','name','category','was_payed','type']).query("category == 'savings'")
        savings['type'] = 'savings'
        retirement = pd.DataFrame(self.GetExpensesByDate(365),columns=['index','timestamp','date','value','name','category','was_payed','type']).query("category == 'retirement'")
        retirement['type'] = 'retirement'
        vacation = pd.DataFrame(self.GetExpensesByDate(365),columns=['index','timestamp','date','value','name','category','was_payed','type']).query("category == 'vacation'")
        vacation['type'] = 'vacation'
        safety_debt = pd.DataFrame(self.GetExpensesByDate(365),columns=['index','timestamp','date','value','name','category','was_payed','type']).query("category not in ('savings','retirement','vacation')")
        safety_debt['type'] = 'safety_debt' 
        try:
            safety_debt['value'] = sum(safety_debt['value']) / 2
        except ZeroDivisionError:
            safety_debt['value'] = 0
        investments['type'] = 'unclassified savings'
        investments['value'] = sum(savings['value']) - sum(retirement['value']) - sum(vacation['value']) - safety_debt['value']
        data = investments.append(retirement).append(vacation).append(safety_debt)
        fig = px.pie(data,values='value',names='type',title='Current savings - 1 year period')
        plot_json = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
        return plot_json
    
    def PrintSafetyDebtCalculation(self):
        safety_debt = pd.DataFrame(self.GetExpensesByDate(365),columns=['index','timestamp','date','value','name','category','was_payed','type']).query("category not in ('savings','retirement','vacation')")
        expenses_wo_savings = pd.DataFrame(self.GetExpensesByDate(365),columns=['index','timestamp','date','value','name','category','was_payed','type']).query("category not in ('savings','retirement','vacation')")
        try:
            safety_debt['value'] = sum(safety_debt['value']) / 2
        except ZeroDivisionError:
            safety_debt['value'] = 0
        return expenses_wo_savings['value'].sum(),safety_debt['value'].sum()

class Validator:
    """
    Validator - class to validate http requests
    """
    #TODO
