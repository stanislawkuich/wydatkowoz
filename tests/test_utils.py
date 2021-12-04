from datetime import date, datetime
from unittest import result
from unittest.loader import makeSuite
from unittest.mock import patch
from resources import utils
from resources import systemVariables
import unittest
import mailbox
import asyncore

#@unittest.skip
class BudgetDatabase(unittest.TestCase):
    # obiekt ktory testujemy
    g = None

    # przed kazdym testem
    def setUp(self):
        self.g = utils.BudgetDatabase(systemVariables.budgetDatabasesPath)
    
    # po kazdym tescie:
    def tearDown(self):
        self.g = None

    def test_should_GetAllIncomes(self):
        # given
        msg = 0

        # when
        result = self.g.GetAllIncomes()

        # then
        print(result)
        self.assertNotEqual(msg, result)

    def test_should_GetAllExpenses(self):
        # given
        msg = 0

        # when
        result = self.g.GetAllExpenses()

        # then
        print(result)
        self.assertNotEqual(msg, result)

#@unittest.skip
class Vizualizer(unittest.TestCase):
    # obiekt ktory testujemy
    g = None

    # przed kazdym testem
    def setUp(self):
        self.g = utils.Vizualizer(systemVariables.budgetDatabasesPath)

    # po kazdym tescie
    def tearDown(self):
        self.g = None

    def test_should_PrintAllBudget(self):
        # given
        msg = 0

        # when
        result = self.g.PrintAllBudget()

        # then
        #print(result)
        self.assertNotEqual(msg, result)

#@unittest.skip
class EmailLocalProcessor(unittest.TestCase):
    # obiekt ktory testujemy
    g = None

    # przed kazdym testem
    def setUp(self):
        self.g = utils.EmailLocalProcessor(systemVariables.emailsFilePath)

    # po kazdym tescie
    def tearDown(self):
        self.g = None
    
    def test_should_OpenMailbox(self):
        # given
        msg = 0

        # when
        result = self.g.OpenMailbox()

        # then
        for n in result.iterkeys():
            message = utils.Email(
                subject= result.get_message(n).get('subject'),
                date= result.get_message(n).get('date'),
                body= result.get_message(n).get_payload(),
                sender= result.get_message(n).get('from'),
                receiver= result.get_message(n).get('to'),
                contentType= result.get_message(n).get_content_type() 
            )
            self.assertIsInstance(message,utils.Email)
        self.g.CloseMailbox()
        self.assertIsInstance(result,mailbox.mbox)

#@unittest.skip
class Email(unittest.TestCase):
    # obiekt ktory testujemy
    g = None

    # przed kazdym testem
    def setUp(self):
        self.g = utils.Email(
            subject='Test: płatność kartą xxx na kwotę -1000,00 PLN',
            date='Wed, 29 Jan 2020 06:47:24 +0100',
            sender='Sender <sender@test.com>',
            receiver='<receiver@gmail.com>',
            contentType='text/html; charset=UTF-8',
            body='<html>\
                    <head>\
                        <title>\
                            Test\
                        </title>\
                    </head>\
                        <body>\
                            <h1>Parse me!</h1>\
                        </body>\
                </html>')

    # po kazdym tescie
    def tearDown(self):
        self.g = None

    def test_shouldInitializeEmailObject(self):
        # given
        msg = 0

        # when
        print(self.g)

        # then
        self.assertIsInstance(self.g,utils.Email)

    def test_GetExpenseFromSubject(self):
        # given
        msg = 1000.00

        # when
        result = self.g.GetExpenseFromSubject()

        # then
        self.assertEqual(result,msg)

    def test_GetProperDateFormat(self):
        # given
        msg = 2020

        # when
        result = self.g.GetProperDateFormat()

        # then
        self.assertEqual(result[0],msg)

@unittest.skip
class EmailRemoteProcessor(unittest.TestCase):
    # obiekt ktory testujemy
    g = None

    # przed kazdym testem
    def setUp(self):
        self.g = utils.EmailRemoteProcessor(('localhost',8025),None)

    # po kazdym tescie
    def tearDown(self):
        self.g.close()

    def test_ReceiveEmail(self):
        # given
        msg = 0

        # when
        try:
            asyncore.loop()
        except KeyboardInterrupt:
            pass

        # then