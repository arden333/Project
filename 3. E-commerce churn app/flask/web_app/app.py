import sqlite3
from flask import Flask, request, render_template
import pickle
import pandas as pd
import psycopg2

# sqlite
conn = sqlite3.connect('data.db', check_same_thread=False) 
# DB연동 후 오류 발생해 check_same_thread 추가

#postgresql
# conn = psycopg2.connect(
#     host = 'peanut.db.elephantsql.com',
#     database = 'dwsiqwgs',
#     user = 'dwsiqwgs',
#     password = 'QfY7jVWTDpPoUzikHE8QonmdXrdj67IV',
# )
cur = conn.cursor()

app = Flask(__name__)

with open('model.pkl','rb') as pickle_file:
    model = pickle.load(pickle_file)

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/target/', defaults={'num':0})
@app.route('/target/<num>')
def target(num):
    # 해당 클러스터 인원 수
    cur.execute(f'SELECT * FROM Customer WHERE Cluster = {num}')
    total = len(cur.fetchall())
    # 이탈 예정 유저 수
    cur.execute(f'SELECT * FROM Customer WHERE Cluster = {num} and Churn_pred = 1')
    churn = len(cur.fetchall())
    rate = round(churn/total,2)*100
    return render_template('target.html', total=total, churn=churn, rate=rate)

@app.route("/pred", methods = ['GET','POST'])
def pred():
    global d1, d2, d3, d4, df, prediction
    if request.method == 'POST':
        d1 = int(request.form['Tenure'])
        d2 = int(request.form['Complain'])
        d3 = int(request.form['DaySinceLastOrder'])
        d4 = int(request.form['SatisfactionScore'])
        d5 = int(request.form['HourSpendOnApp'])
        X = pd.DataFrame({'Tenure': int(d1), 'Complain':int(d2), 'DaySinceLastOrder':int(d3), 'SatisfactionScore':int(d4), 'HourSpendOnApp':int(d5)}, index=[0])
        prediction = model.predict(X)
        if prediction == 1:
            return render_template('pred.html', result = '해당')
        else:
            return render_template('pred.html', result = '해당하지 않음')
    else:
        return render_template('pred.html')

if __name__ == "__main__":
    app.run(debug=True)