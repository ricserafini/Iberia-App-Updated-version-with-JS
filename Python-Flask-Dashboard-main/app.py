# https://g6a35f299a6bdd5-db202203181048.adb.eu-milan-1.oraclecloudapps.com/ords/admin/monthly_incidents_real_time_2104/?limit=1000&offset=7500
# python 3.9

from dash import Dash, html, dcc
from os.path import exists
from flask import Flask, redirect, render_template, session, request,flash
import flask
import flask_login
import requests
# import dash_auth
import pandas as pd
import numpy as np
from kpis import KPIS, getKpis, getThrends

# @note Safely suppress copy warnings they are ok    
pd.set_option('mode.chained_assignment', None)

app = Flask(__name__)
app.secret_key = 'xxxxyyyyyzzzzz'

login_manager = flask_login.LoginManager(app)
login_manager.init_app(app)

login_manager.login_view = 'login'

# @note Only for demo purposes
users = {'riccardo@demo.com': {'pw': 'demo'}}

class User(flask_login.UserMixin):
    pass

@login_manager.user_loader
def user_loader(email):
    if email not in users:
        return

    user = User()
    user.id = email
    return user

@login_manager.request_loader
def request_loader(request):
    email = request.form.get('email')
    if email not in users:
        return

    user = User()
    user.id = email

    user.is_authenticated = request.form['pw'] == users[email]['pw']
    return user

@login_manager.unauthorized_handler
def unauthorized_handler():
    return 'Unauthorized'

# app = Dash(
#     server=server,
#     url_base_pathname = '/'
# )


@app.route('/', methods=['GET', 'POST'])
def landing():
    return render_template('login.html')

@app.route('/login', methods=[ 'GET','POST'])
def login():
    email = request.form['username']
    pw = request.form['password']
    if (email in users) and pw == users[email]['pw']:
        user = User()
        user.id = email
        flask_login.login_user(user)
        flash('You were successfully logged in')
        return flask.redirect(flask.url_for('dashboard1'))
    else:
        flash('Bad login!')
        return render_template('login.html', error='Invalid credentials')

    # return 'Bad login'

@app.route('/logout', methods=['GET', 'POST'])
def logout():
    flask_login.logout_user()
    return flask.redirect(flask.url_for('landing'))

@app.route('/dashboard1', methods=['GET', 'POST'])
def dashboard1():
    db = pd.read_csv("data/2104.csv");
    db_backlog = pd.read_csv("data/2104_backlog.csv");
    criticalSLAData,criticalIncidents,totalIncidents,incidentTypeBreakdownFraction,backlogTypeBreakdown,incidentTypeBreakdown,p1SLAResolutionTime,p1AverageTimeSLA,p1AverageTimeNotSLA,incidentStatusType=getKpis(db,db_backlog);
    return render_template('main.html',month="April",  dashboard1=True,totalIns={},totalCriticalIns={}, criticalSLAData=criticalSLAData,criticalIncidents=criticalIncidents,totalIncidents=totalIncidents,incidentTypeBreakdownFraction=incidentTypeBreakdownFraction,backlogTypeBreakdown=backlogTypeBreakdown,incidentTypeBreakdown=incidentTypeBreakdown,p1SLAResolutionTime=p1SLAResolutionTime,p1AverageTimeSLA=p1AverageTimeSLA,p1AverageTimeNotSLA=p1AverageTimeNotSLA,incidentStatusType=incidentStatusType)
    
@app.route('/dashboard2', methods=['GET', 'POST'])
def dashboard2():
    db_csv_name = "data/2104.csv";
    db_backlog_csv_name = "data/2104_backlog.csv";
    month = "April"
    if flask.request.method == 'POST':
        month = request.form['comp_select']
        if(month == "January"):
            db_csv_name = "data/2101.csv";
            db_backlog_csv_name = "data/2101_backlog.csv";
        elif(month == "February"):
            db_csv_name = "data/2102.csv";
            db_backlog_csv_name = "data/2102_backlog.csv";
        else:
            db_csv_name = "data/2103.csv";
            db_backlog_csv_name = "data/2103_backlog.csv";

    print("Selected month: ", month)
    db = pd.read_csv(db_csv_name);
    db_backlog = pd.read_csv(db_backlog_csv_name);
    totalIns,totalCriticalIns=getThrends();
    criticalSLAData,criticalIncidents,totalIncidents,incidentTypeBreakdownFraction,backlogTypeBreakdown,incidentTypeBreakdown,p1SLAResolutionTime,p1AverageTimeSLA,p1AverageTimeNotSLA,incidentStatusType = getKpis(db,db_backlog);
    return render_template('main.html', dashboard2=True, set_option = month , month=month , totalIns=totalIns,totalCriticalIns=totalCriticalIns, criticalSLAData=criticalSLAData,criticalIncidents=criticalIncidents,totalIncidents=totalIncidents,incidentTypeBreakdownFraction=incidentTypeBreakdownFraction,backlogTypeBreakdown=backlogTypeBreakdown,incidentTypeBreakdown=incidentTypeBreakdown,p1SLAResolutionTime=p1SLAResolutionTime,p1AverageTimeSLA=p1AverageTimeSLA,p1AverageTimeNotSLA=p1AverageTimeNotSLA,incidentStatusType=incidentStatusType)

if __name__ == '__main__':
    app.run(debug=True, port = 8050)



