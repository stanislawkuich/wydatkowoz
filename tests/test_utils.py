from unittest.loader import makeSuite
from resources import utils
import unittest
import pandas as pd
import plotly
import plotly.express as px

#@unittest.skip
class BudgetDatabase(unittest.TestCase):
    # obiekt ktory testujemy
    g = None

    # przed kazdym testem
    def setUp(self):
        self.g = utils.BudgetDatabase('tests/budgetTest.db')
    
    # po kazdym tescie:
    def tearDown(self):
        self.g = None

    def test_should_GetAllIncomes(self):
        # given
        msg = 0

        # when
        result = self.g.GetAllIncomes()

        # then
        #print(result)
        self.assertNotEqual(msg, result)

    def test_should_GetAllExpenses(self):
        # given
        msg = 0

        # when
        result = self.g.GetAllExpenses()

        # then
        #print(result)
        self.assertNotEqual(msg, result)

#@unittest.skip
class Vizualizer(unittest.TestCase):
    # obiekt ktory testujemy
    g = None

    # przed kazdym testem
    def setUp(self):
        self.g = utils.Vizualizer('tests/budgetTest.db')

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
