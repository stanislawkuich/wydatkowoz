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
    return flask.render_template('dashboard.html', title='Wydatkowoz',context1=plot.PrintAllBudget(),context2=plot.PrintLast30DaysBudget(),context3=plot.PrintLast30DaysExpenses(),context4=plot.PrintPreviousYearsBudget())

@app.route('/api/v1/incomes',methods=['GET'])
def Allincomes():
    db = utils.BudgetDatabase(systemVariables.budgetDatabasesPath)
    if flask.request.content_type == 'application/json':
        return flask.jsonify(db.GetAllIncomes())
    else:
        return flask.render_template('incomes.html', items=db.GetAllIncomes())

@app.route('/api/v1/incomes/recently=<int:days>',methods=['GET'])
def LastNdaysIncomes(days):
    db = utils.BudgetDatabase(systemVariables.budgetDatabasesPath)
    if flask.request.content_type == 'application/json':
        return flask.jsonify(db.GetIncomesByDate(days))
    else:
        return flask.render_template('incomes.html', items=db.GetIncomesByDate(days))

@app.route('/api/v1/expenses',methods=['GET'])
def Allexpenses():
    db = utils.BudgetDatabase(systemVariables.budgetDatabasesPath)
    if flask.request.content_type == 'application/json':
        return flask.jsonify(db.GetAllExpenses())
    else:
        return flask.render_template('outcomes.html', items=db.GetAllExpenses())

@app.route('/api/v1/expenses/recently=<int:days>',methods=['GET'])
def LastNDaysExpenses(days):
    db = utils.BudgetDatabase(systemVariables.budgetDatabasesPath)
    if flask.request.content_type == 'application/json':
        return flask.jsonify(db.GetExpensesByDate(id))
    else:
        return flask.render_template('outcomes.html', items=db.GetExpensesByDate(days))

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
    date = flask.request.form['outcome_date']
    outcome = flask.request.form['outcome']
    description = flask.request.form['description']
    category = flask.request.form['category']
    waspayed = flask.request.form['waspayed']
    if description:
        data = {'date':date, 'value':outcome, 'name':description, 'category':int(category),'was_payed':waspayed}
    else:
        data = {'date':date, 'value':outcome, 'name':'expenses', 'category':int(category),'was_payed':waspayed}
    if 'date' not in data or 'value' not in data or 'was_payed' not in data:
        return 'Missing mandatory arguments...', 400
    db = utils.BudgetDatabase(systemVariables.budgetDatabasesPath)
    if 'name' not in data or 'category' not in data:
        response = db.SetNewExpenses(timestamp=data['date'],date=data['date'],value=data['value'],was_payed=data['was_payed'])
    else:
        response = db.SetNewExpenses(timestamp=data['date'],date=data['date'],value=data['value'],name=data['name'],category=data['category'],was_payed=data['was_payed'])
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

@app.route('/api/v1/expenses/id=<int:id>',methods=['DELETE'])
def DeleteExpenses(id):
    db = utils.BudgetDatabase(systemVariables.budgetDatabasesPath)
    response = db.DelExpenses(id)
    if flask.request.content_type == 'application/json':
        return flask.jsonify(response)
    else:
        return flask.render_template('status.html', value=response)

if __name__ == '__main__':
    app.run()