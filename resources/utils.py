import mailbox
import email
from email.header import decode_header, make_header
from smtpd import SMTPServer
from os import close, write
import smtpd
from resources import systemVariables
import sqlite3
import json
import datetime
import logging
import re
import pandas as pd
import plotly
import plotly.graph_objects as go
from plotly.subplots import make_subplots

logging.basicConfig(filename=systemVariables.logFilePath, filemode='w', format='%(asctime)s - %(levelname)s - %(message)s',level=logging.WARNING)
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
        newExpense = BudgetDatabase(systemVariables.budgetDatabasesPath)
        newExpense.SetNewExpenses(year=self.message.GetProperDateFormat()[0],month=self.message.GetProperDateFormat()[1],day=self.message.GetProperDateFormat()[2],cost=self.message.GetExpenseFromSubject())
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
        original_date = datetime.datetime.strptime(self.date,'%a, %d %b %Y %H:%M:%S +0100')
        year = original_date.strftime('%Y')
        month = original_date.strftime('%m')
        day = original_date.strftime('%d')
        return int(year),int(month),int(day)

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
	            [YEAR] INTEGER(4) NOT NULL,
                [MONTH] INTEGER(2) NOT NULL,
                [DAY] INTEGER(2) NOT NULL,
                [SALARY] REAL(50) NOT NULL,
                [NAME] TEXT NOT NULL
            );
            """
        )
        self.cur = self.conn.cursor()
        self.cur.execute(
            """
            CREATE TABLE IF NOT EXISTS [Expenses] (
                [ExpenseId] INTEGER NOT NULL PRIMARY KEY, 
                [YEAR] INTEGER(4) NOT NULL,
                [MONTH] INTEGER(2) NOT NULL,
                [DAY] INTEGER(2) NOT NULL,
                [NAME] TEXT NOT NULL,
                [CATEGORY] INTEGER(2) NOT NULL,
                [COST] REAL(50) NOT NULL,
                [WAS_PAYED] INTEGER NOT NULL
            );
            """
        )
        return

    def GetAllIncomes(self,desc_order=True):
        self.conn = sqlite3.connect(self.path)
        self.cur = self.conn.cursor()
        if desc_order:
            self.allIncomes = self.cur.execute('SELECT * FROM Incomes ORDER BY rowid DESC;').fetchall()
        else:
            self.allIncomes = self.cur.execute('SELECT * FROM Incomes ORDER BY rowid ASC;').fetchall()
        return self.allIncomes

    def GetAllExpenses(self,desc_order=True):
        self.conn = sqlite3.connect(self.path)
        self.cur = self.conn.cursor()
        if desc_order:
            self.allExpenses = self.cur.execute('SELECT * FROM Expenses ORDER BY rowid DESC;').fetchall()
        else:
            self.allExpenses = self.cur.execute('SELECT * FROM Expenses ORDER BY rowid ASC;').fetchall()
        return self.allExpenses

    def SetNewIncomes(self, year=0, month=0, day=0, salary=0, name='income'):
        self.year = year
        self.month = month
        self.day = day
        self.name = name
        self.salary = salary
        self.conn = sqlite3.connect(self.path)
        self.cur = self.conn.cursor()
        self.income = self.cur.execute("INSERT INTO Incomes (YEAR,MONTH,DAY,SALARY,NAME) VALUES (%s, %s, %s, %s, '%s');" % (self.year, self.month, self.day, self.salary, self.name))
        self.conn.commit()
        return 'New IncomeId: '+str(self.cur.lastrowid)

    def SetNewExpenses(self, year=0, month=0, day=0, name='expenses', category=8, cost=0, was_payed=False):
        self.year = year
        self.month = month
        self.day = day
        self.name = name
        self.category = systemVariables.ExpensesCategories[category]
        self.cost = cost
        self.was_payed = was_payed
        self.conn = sqlite3.connect(self.path)
        self.cur = self.conn.cursor()
        self.income = self.cur.execute("INSERT INTO Expenses (YEAR,MONTH,DAY,NAME,CATEGORY,COST,WAS_PAYED) VALUES (%s, %s, %s, '%s', '%s', %s, %s);" % (self.year, self.month, self.day, self.name, self.category, self.cost, self.was_payed))
        self.conn.commit()
        return 'New ExpenseId: '+str(self.cur.lastrowid)
    
    def DelIncomes(self, id):
        self.id = id
        self.conn = sqlite3.connect(self.path)
        self.cur = self.conn.cursor()
        self.income = self.cur.execute('DELETE FROM Incomes WHERE IncomeId=%s;' % (self.id))
        self.conn.commit()
        return 'Total Changes: '+str(self.cur.rowcount)

    def DelExpenses(self, id):
        self.id = id
        self.conn = sqlite3.connect(self.path)
        self.cur = self.conn.cursor()
        self.income = self.cur.execute('DELETE FROM Expenses WHERE ExpenseId=%s;' % (self.id))
        self.conn.commit()
        return 'Total Changes: '+str(self.cur.rowcount)

class Vizualizer(BudgetDatabase):
    """
    Class representing visualizations from Budget DB
    """
    def PrintAllBudget(self):
        income = pd.DataFrame(self.GetAllIncomes(desc_order=False),columns=['index','year','month', 'day','salary','name'])
        expenses = pd.DataFrame(self.GetAllExpenses(desc_order=False),columns=['index','year','month', 'day','name','category','cost','was_payed'])
        date_income = income['year'].astype(str) + '-' + income['month'].astype(str) + '-' + income['day'].astype(str)
        date_expenses = expenses['year'].astype(str) + '-' + expenses['month'].astype(str) + '-' + income['day'].astype(str)
        fig = make_subplots(specs=[[{"secondary_y": True}]])
        fig.add_trace(go.Scatter(x=date_income, y=income['salary'], name="incomes"),secondary_y=False)
        fig.add_trace(go.Scatter(x=date_expenses, y=expenses['cost'], name="expenses"),secondary_y=True)
        fig.update_xaxes(rangeslider_visible=True)
        fig.update_layout(width=1500, height=500,title_text="Budget summary")
        plot_json = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
        return plot_json

class Validator:
    """
    Validator - class to validate http requests
    """
    #TODO
