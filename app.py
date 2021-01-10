from flask import Flask, render_template, g, request
from datetime import datetime
from database import get_db, connect_db

app = Flask(__name__)


@app.teardown_appcontext

def close_db(error):
    if hasattr(g, 'sqlite_db'):
        g.sqlite_db.close()

@app.route('/', methods=['POST', 'GET'])
def index():
    db = get_db()#initialise the database
    if request.method == 'POST':
        date = request.form['date']#assuming the date is in YYYY-MM-DD format

        dt = datetime.strptime(date, '%Y-%m-%d')#converts date to date object e.g. "(2017, 1, 28, 0, 0)"
        database_date = datetime.strftime(dt, '%Y%m%d')#converts date to e.g. "20170128" format

        db.execute('insert into log_date (entry_date) values (?)', [database_date])
        db.commit()
      #query the database for everything in the table
    cursor = db.execute('''select log_date.entry_date, sum(food.protein) as protein, sum(food.carbohydrates) as carbohydrates, sum(food.fat) as fat, sum(food.calories) as calories 
                        from log_date 
                        left join food_date on food_date.log_date_id = log_date.id 
                        left join food on food.id = food_date.food_id 
                        group by log_date.id order by log_date.entry_date desc''')
    results = cursor.fetchall()

    date_results = []

    for i in results:
        single_date = {}#empty dictionary to be able to append it at the end of the for loop
        
        single_date['entry_date'] = i['entry_date']
        single_date['protein'] = i['protein']
        single_date['carbohydrates'] = i['carbohydrates']
        single_date['fat'] = i['fat']
        single_date['calories'] = i['calories']

        d = datetime.strptime(str(i['entry_date']), '%Y%m%d')#converts every date to e.g. "20170128" format
        single_date['pretty_date'] = datetime.strftime(d, '%B %d , %Y')#converts every date in the database into the rightly formated date
        date_results.append(single_date)

    return render_template('home.html', results=date_results)

@app.route('/view/<date>', methods=['POST', 'GET'])
def view(date):
    db = get_db()#initialise the database
  #query the database for one variable
    cursor = db.execute('select id, entry_date from log_date where entry_date = ?', [date])
    date_result = cursor.fetchone()
    
    if request.method == 'POST':
       db.execute('insert into food_date (food_id, log_date_id) values (?, ?)', [request.form['food-select'], date_result['id']])
       db.commit()
    
    
    d = datetime.strptime(str(date_result['entry_date']), '%Y%m%d')
    pretty_date = datetime.strftime(d, '%B %d, %Y')
      #query the database for everything in the table
    food_cursor = db.execute('select id, food_name from food')
    food_results = food_cursor.fetchall()

    log_cur = db.execute('select food.food_name, food.protein, food.carbohydrates, food.fat, food.calories from log_date join food_date on food_date.log_date_id = log_date.id join food on food.id = food_date.food_id where log_date.entry_date = ?', [date])
    log_results = log_cur.fetchall()

    totals = {}
    totals['protein'] = 0
    totals['carbohydrates'] = 0
    totals['fat'] = 0
    totals['calories'] = 0
    for food in log_results:
        totals['protein'] += food['protein']
        totals['carbohydrates'] += food['carbohydrates']
        totals['fat'] += food['fat']
        totals['calories'] += food['calories']

    return render_template('day.html', entry_date=date_result['entry_date'], pretty_date=pretty_date, \
                            food_results=food_results, log_results=log_results, totals=totals)

@app.route('/food', methods=['GET', 'POST'])
def food():

    db = get_db()#initialise the database

    if request.method == 'POST':
        name = request.form['food_name']
        protein = int(request.form['protein'])
        carbohydrates = int(request.form['carbohydrates'])
        fat = int(request.form['fat'])

        calories = protein * 4 + carbohydrates + 4 + fat * 9

        db.execute('insert into food (food_name, protein, carbohydrates, fat, calories) values(?, ?, ?, ?, ?)', \
            [name, protein, carbohydrates, fat, calories])
        db.commit()
    #query the database for everything in the table
    cursor = db.execute('select food_name, protein, carbohydrates, fat, calories from food')
    results = cursor.fetchall()

   
    return render_template('add_food.html', results=results)

if __name__=='__main__':
    app.run(debug=True)