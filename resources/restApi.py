import flask
import logging
from resources import utils, systemVariables

app = flask.Flask(__name__, template_folder='../web/templates', static_folder='../web/templates/static')
app.config["DEBUG"] = False
app.logger = logging.getLogger('werkzeug')
app.logger.setLevel(logging.WARNING)


@app.route('/')
@app.route('/dashboard')
def index():
    plot = utils.Vizualizer(systemVariables.budgetDatabasesPath)
    return flask.render_template('dashboard.html', title='Wydatkowoz',context1=plot.PrintAllBudget(),context2=plot.PrintBudgetSinceLastIncome(),context3=plot.PrintPreviousMonthsExpenses(),context4=plot.PrintPreviousYearsBudget(),context5=plot.PrintLast365DaysExpenses(),context7=plot.PrintPreviousExpenses(),context8=plot.PrintPreviousMonthsExpensesHistogram(),context9=plot.PrintPreviousExpensesHistogram(),context10=plot.PrintExpensesSinceLastIncomeByType(),context11=plot.PrintPreviousMonthsExpensesByType(),context12=plot.PrintPreviousMonthsExpensesHistogramByType())

@app.route('/api/v1/incomes',methods=['GET'])
def Allincomes():
    db = utils.BudgetDatabase(systemVariables.budgetDatabasesPath)
    if flask.request.content_type == 'application/json':
        return flask.jsonify(db.GetAllIncomes())
    else:
        return flask.render_template('incomes.html', title="Incomes", items=db.GetAllIncomes())

@app.route('/api/v1/incomes/recently=<int:days>',methods=['GET'])
def LastNdaysIncomes(days):
    db = utils.BudgetDatabase(systemVariables.budgetDatabasesPath)
    if flask.request.content_type == 'application/json':
        return flask.jsonify(db.GetIncomesByDate(days))
    else:
        return flask.render_template('incomes.html', items=db.GetIncomesByDate(days))

@app.route('/api/v1/incomes/latest',methods=['GET'])
def LatestIncomes():
    db = utils.BudgetDatabase(systemVariables.budgetDatabasesPath)
    if flask.request.content_type == 'application/json':
        return flask.jsonify(db.GetLatestIncome())
    else:
        return flask.render_template('incomes.html', items=db.GetLatestIncome())

@app.route('/api/v1/expenses',methods=['GET'])
def Allexpenses():
    db = utils.BudgetDatabase(systemVariables.budgetDatabasesPath)
    if flask.request.content_type == 'application/json':
        return flask.jsonify(db.GetAllExpenses())
    else:
        return flask.render_template('outcomes.html', title="Expenses", items=db.GetAllExpenses())
    
@app.route('/api/v1/investments',methods=['GET'])
def Allinvestments():
    db = utils.BudgetDatabase(systemVariables.budgetDatabasesPath)
    plot = utils.Vizualizer(systemVariables.budgetDatabasesPath)
    return flask.render_template('investments.html', title="Savings/Investments",items=db.GetAllInvestments(),context1=plot.PrintSavingsTrends(),context2=plot.PrintPreviousYearSavings(),context3=plot.PrintSafetyDebtCalculation())

@app.route('/api/v1/investment',methods=['POST'])
def NewInvestment():
    if flask.request.content_type == 'application/json':
        json_data = flask.request.json
        date = json_data['date']
        investment = json_data['value']
        goal = json_data['goal']
        description = json_data['name']
        waspayed = json_data['waspayed']
    else:
        date = flask.request.form['investment_date']
        investment = flask.request.form['investment']
        goal = flask.request.form['goal']
        description = flask.request.form['description']
        waspayed = flask.request.form['waspayed']
    if description:
        data = {'date':date, 'value':investment, 'goal':goal, 'name':description, 'was_payed':waspayed}
    else:
        data = {'date':date, 'value':investment, 'goal':goal, 'name':'Custom Investment', 'was_payed':waspayed}
    if 'date' not in data or 'value' not in data or 'was_payed' not in data:
        return 'Missing mandatory arguments...', 400
    db = utils.BudgetDatabase(systemVariables.budgetDatabasesPath)
    if 'name' not in data or 'goal' not in data:
        response = db.SetNewInvestment(timestamp=data['date'],date=data['date'],value=data['value'],was_payed=data['was_payed'])
    else:
        response = db.SetNewInvestment(timestamp=data['date'],date=data['date'],value=data['value'],goal=data['goal'],name=data['name'],was_payed=data['was_payed'])
    if flask.request.content_type == 'application/json':
        return flask.jsonify(response)
    else:
        return flask.render_template('status.html', value=response)
    
@app.route('/api/v1/investment/delete/<int:id>',methods=['DELETE','GET'])
def DeleteInvestment(id):
    db = utils.BudgetDatabase(systemVariables.budgetDatabasesPath)
    if flask.request.content_type == 'application/json':
        if flask.request.method == 'DELETE':
            response = db.DelInvestment(id)
            return flask.jsonify(response)
        else:
            return 'Wrong method...', 500
    else:
        response = db.DelInvestment(id)
        return flask.render_template('status.html', value=response)

@app.route('/api/v1/investment/edit/<int:id>',methods=['GET'])
def EditInvestment(id):
    db = utils.BudgetDatabase(systemVariables.budgetDatabasesPath)
    return flask.render_template('edit_investment.html',items=db.GetInvestment(id))

@app.route('/api/v1/investment/update',methods=['POST'])
def UpdateInvestment():
    db = utils.BudgetDatabase(systemVariables.budgetDatabasesPath)
    if flask.request.content_type == 'application/json':
        json_data = flask.request.json
        id = json_data['id']
        date = json_data['date']
        investment = json_data['value']
        goal = json_data['goal']
        description = json_data['name']
        waspayed = json_data['waspayed']
        response = db.UpdateInvestment(id,date,date,investment,goal,description,waspayed)
        return flask.jsonify(response)
    else:
        id = flask.request.form['id']
        date = flask.request.form['investment_date']
        investment = flask.request.form['investment']
        goal = flask.request.form['goal']
        description = flask.request.form['description']
        waspayed = flask.request.form['waspayed']
        response = db.UpdateInvestment(id,date,date,investment,goal,description,waspayed)
        return flask.render_template('status.html', value=response)

@app.route('/api/v1/expenses/recently=<int:days>',methods=['GET'])
def LastNDaysExpenses(days):
    db = utils.BudgetDatabase(systemVariables.budgetDatabasesPath)
    if flask.request.content_type == 'application/json':
        return flask.jsonify(db.GetExpensesByDate(id))
    else:
        return flask.render_template('outcomes.html', items=db.GetExpensesByDate(days))

@app.route('/api/v1/expenses/latest',methods=['GET'])
def LatestExpenses():
    db = utils.BudgetDatabase(systemVariables.budgetDatabasesPath)
    if flask.request.content_type == 'application/json':
        return flask.jsonify(db.GetExpensesSinceLastIncomes())
    else:
        return flask.render_template('outcomes.html', items=db.GetExpensesSinceLastIncomes())

@app.route('/api/v1/incomes',methods=['POST'])
def NewIncomes():
    if flask.request.content_type == 'application/json':
        json_data = flask.request.json
        date = json_data['date']
        income = json_data['value']
        description = json_data['name']
    else:
        date = flask.request.form['income_date']
        income = flask.request.form['income']
        description = flask.request.form['description']
    if description:
        data = {'date':date,'value':income, 'name':description}
    else:
        data = {'date':date,'value':income}
    if 'date' not in data or 'value' not in data:
        return 'Missing mandatory arguments...', 400
    db = utils.BudgetDatabase(systemVariables.budgetDatabasesPath)
    if 'name' not in data:
        response = db.SetNewIncomes(data['date'],data['date'],data['value'])
    else:
        response = db.SetNewIncomes(data['date'],data['date'],data['value'],data['name'])
    if flask.request.content_type == 'application/json':
        return flask.jsonify(response)
    else:
        return flask.render_template('status.html', value=response)

@app.route('/api/v1/expenses',methods=['POST'])
def NewExpenses():
    if flask.request.content_type == 'application/json':
        json_data = flask.request.json
        date = json_data['date']
        outcome = json_data['value']
        description = json_data['name']
        category = json_data['category']
        waspayed = json_data['waspayed']
        type = json_data['type']
    else:
        date = flask.request.form['outcome_date']
        outcome = flask.request.form['outcome']
        description = flask.request.form['description']
        category = flask.request.form['category']
        waspayed = flask.request.form['waspayed']
        type = flask.request.form['type']
    if description:
        data = {'date':date, 'value':outcome, 'name':description, 'category':int(category),'was_payed':waspayed,'type':int(type)}
    else:
        data = {'date':date, 'value':outcome, 'name':'expenses', 'category':int(category),'was_payed':waspayed,'type':int(type)}
    if 'date' not in data or 'value' not in data or 'was_payed' not in data:
        return 'Missing mandatory arguments...', 400
    db = utils.BudgetDatabase(systemVariables.budgetDatabasesPath)
    if 'name' not in data or 'category' not in data:
        response = db.SetNewExpenses(timestamp=data['date'],date=data['date'],value=data['value'],was_payed=data['was_payed'],type=data['type'])
    else:
        response = db.SetNewExpenses(timestamp=data['date'],date=data['date'],value=data['value'],name=data['name'],category=data['category'],was_payed=data['was_payed'],type=data['type'])
    if flask.request.content_type == 'application/json':
        return flask.jsonify(response)
    else:
        return flask.render_template('status.html', value=response)

@app.route('/api/v1/incomes/delete/<int:id>',methods=['DELETE','GET'])
def DeleteIncomes(id):
    db = utils.BudgetDatabase(systemVariables.budgetDatabasesPath)
    if flask.request.content_type == 'application/json':
        if flask.request.method == 'DELETE':
            response = db.DelIncomes(id)
            return flask.jsonify(response)
        else:
            return 'Wrong method...', 500
    else:
        response = db.DelIncomes(id)
        return flask.render_template('status.html', value=response)

@app.route('/api/v1/incomes/edit/<int:id>',methods=['GET'])
def EditIncome(id):
    db = utils.BudgetDatabase(systemVariables.budgetDatabasesPath)
    return flask.render_template('edit_income.html',items=db.GetIncome(id))

@app.route('/api/v1/incomes/update',methods=['POST'])
def UpdateIncomes():
    db = utils.BudgetDatabase(systemVariables.budgetDatabasesPath)
    if flask.request.content_type == 'application/json':
        json_data = flask.request.json
        id = json_data['id']
        date = json_data['date']
        income = json_data['value']
        description = json_data['name']
        response = db.UpdateIncome(id,date,date,income,description)
        return flask.jsonify(response)
    else:
        id = flask.request.form['id']
        date = flask.request.form['income_date']
        income = flask.request.form['income']
        description = flask.request.form['description']
        response = db.UpdateIncome(id,date,date,income,description)
        return flask.render_template('status.html', value=response)

@app.route('/api/v1/expenses/delete/<int:id>',methods=['DELETE','GET'])
def DeleteExpenses(id):
    db = utils.BudgetDatabase(systemVariables.budgetDatabasesPath)
    if flask.request.content_type == 'application/json':
        if flask.request.method == 'DELETE':
            response = db.DelExpenses(id)
            return flask.jsonify(response)
        else:
            return 'Wrong method...', 500
    else:
        response = db.DelExpenses(id)
        return flask.render_template('status.html', value=response)

@app.route('/api/v1/expenses/edit/<int:id>',methods=['GET'])
def EditExpenses(id):
    db = utils.BudgetDatabase(systemVariables.budgetDatabasesPath)
    return flask.render_template('edit_expenses.html',items=db.GetExpenses(id))

@app.route('/api/v1/expenses/update',methods=['POST'])
def UpdateExpenses():
    db = utils.BudgetDatabase(systemVariables.budgetDatabasesPath)
    if flask.request.content_type == 'application/json':
        json_data = flask.request.json
        id = json_data['id']
        date = json_data['date']
        outcome = json_data['value']
        description = json_data['name']
        category = json_data['category']
        waspayed = json_data['waspayed']
        type = json_data['type']
        response = db.UpdateExpenses(id,date,date,outcome,description,category,waspayed,type)
        return flask.jsonify(response)
    else:
        id = flask.request.form['id']
        date = flask.request.form['outcome_date']
        outcome = flask.request.form['outcome']
        description = flask.request.form['description']
        category = flask.request.form['category']
        waspayed = flask.request.form['waspayed']
        type = flask.request.form['type']
        response = db.UpdateExpenses(id,date,date,outcome,description,category,waspayed,type)
        return flask.render_template('status.html', value=response)

if __name__ == '__main__':
    app.run()