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
    return flask.render_template('dashboard.html', title='Wydatkowoz',context=plot.PrintAllBudget())

@app.route('/api/v1/incomes',methods=['GET'])
def Allincomes():
    db = utils.BudgetDatabase(systemVariables.budgetDatabasesPath)
    #return flask.jsonify(db.GetAllIncomes())
    return flask.render_template('incomes.html', items=db.GetAllIncomes())

@app.route('/api/v1/expenses',methods=['GET'])
def Allexpenses():
    db = utils.BudgetDatabase(systemVariables.budgetDatabasesPath)
    #return flask.jsonify(db.GetAllExpenses())
    return flask.render_template('outcomes.html', items=db.GetAllExpenses())

@app.route('/api/v1/incomes',methods=['POST'])
def NewIncomes():
    date = flask.request.form['income_date']
    time = date.split('-')
    year = time[0]
    month = time[1]
    income = flask.request.form['income']
    salary = income
    description = flask.request.form['description']
    if description:
        data = {'year':year,'month':month,'salary':salary, 'name':description}
    else:
        data = {'year':year,'month':month,'salary':salary}
    if 'year' not in data or 'month' not in data or 'salary' not in data:
        return 'Missing mandatory arguments...', 400
    db = utils.BudgetDatabase(systemVariables.budgetDatabasesPath)
    if 'name' not in data:
        response = db.SetNewIncomes(data['year'],data['month'],data['salary'])
    else:
        response = db.SetNewIncomes(data['year'],data['month'],data['salary'],data['name'])
    #return flask.jsonify(response)
    return flask.render_template('status.html', value=response)

@app.route('/api/v1/expenses',methods=['POST'])
def NewExpenses():
    date = flask.request.form['outcome_date']
    time = date.split('-')
    year = time[0]
    month = time[1]
    outcome = flask.request.form['outcome']
    description = flask.request.form['description']
    category = flask.request.form['category']
    ispayed = flask.request.form['ispayed']
    if description:
        data = {'year':year,'month':month,'cost':outcome, 'name':description, 'category':int(category),'was_payed':ispayed}
    else:
        data = {'year':year,'month':month,'cost':outcome, 'category':int(category),'was_payed':ispayed}
    if 'year' not in data or 'month' not in data or 'cost' not in data or 'was_payed' not in data:
        return 'Missing mandatory arguments...', 400
    db = utils.BudgetDatabase(systemVariables.budgetDatabasesPath)
    if 'name' not in data or 'category' not in data:
        response = db.SetNewExpenses(year=data['year'],month=data['month'],cost=data['cost'],was_payed=data['was_payed'])
    else:
        response = db.SetNewExpenses(data['year'],data['month'],data['name'],data['category'],data['cost'],data['was_payed'])
    #return flask.jsonify(response)
    return flask.render_template('status.html', value=response)

@app.route('/api/v1/incomes/id=<int:id>',methods=['DELETE'])
def DeleteIncomes(id):
    db = utils.BudgetDatabase(systemVariables.budgetDatabasesPath)
    response = db.DelIncomes(id)
    return flask.jsonify(response)

@app.route('/api/v1/expenses/id=<int:id>',methods=['DELETE'])
def DeleteExpenses(id):
    db = utils.BudgetDatabase(systemVariables.budgetDatabasesPath)
    response = db.DelExpenses(id)
    return flask.jsonify(response)

if __name__ == '__main__':
    app.run()