# -*- coding: utf-8 -*-


from topics import topics
import os
import config
from flask import Flask, request, redirect, url_for, session, g, flash, render_template
from flask_oauth import OAuth

from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base

from bs4 import BeautifulSoup
import urllib.request as urllib2
import json
import datetime as dt
from azure.storage.blob import (
    BlockBlobService
) 

# configuration
SECRET_KEY = 'development key'
DEBUG = True

# setup flask
app = Flask(__name__)
app.debug = DEBUG
app.secret_key = SECRET_KEY

oauth = OAuth()

accountName = config.ACCOUNT_NAME
accountKey = config.ACCOUNT_KEY
containerName = config.CONTAINER_NAME
blobService = BlockBlobService(account_name=accountName, account_key=accountKey)

consumer_key = config.CONSUMER_KEY
consumer_secret = config.CONSUMER_SECRET

twitter = oauth.remote_app('twitter',
    base_url='https://api.twitter.com/1.1/',
    request_token_url='https://api.twitter.com/oauth/request_token',
    access_token_url='https://api.twitter.com/oauth/access_token',
    authorize_url='https://api.twitter.com/oauth/authorize',
    consumer_key=consumer_key,
    consumer_secret=consumer_secret
)

@twitter.tokengetter
def get_twitter_token(token=None):
    return session.get('twitter_token')

@app.route('/')
def landing():
    access_token = session.get('access_token')
    cond = session.get('cond')
    if cond is None:
        cond = request.args.get('cond')
        session['cond'] = cond
    #print('Condition: '+cond)
    if access_token is None:
        return redirect(url_for('login'))

    access_token = access_token[0]
    map_trails = get_trails(cond=cond)
    return render_template('landing.html', map_trails=map_trails)

@app.route('/login')
def login():
    return twitter.authorize(callback=url_for('oauth_authorized',
      next=request.args.get('next') or request.referrer or None))
    
@app.route('/logout')
def logout():
    session.pop('screen_name', None)
    flash('You were signed out')
    return redirect(request.referrer or url_for('index'))

@app.route('/oauth-authorized')
@twitter.authorized_handler
def oauth_authorized(resp):
    next_url = request.args.get('next') or url_for('landing')
    if resp is None:
        flash(u'You denied the request to sign in.')
        return redirect(next_url)

    access_token = resp['oauth_token']
    session['access_token'] = access_token
    session['screen_name'] = resp['screen_name']

    session['twitter_token'] = (resp['oauth_token'],resp['oauth_token_secret'])

    return redirect(url_for('landing'))

def get_trails(cond='cancer', gender='Female', age='23', country='US', intervention=''):
    i = 0
    # specify the url
    #quote_page = 'https://clinicaltrials.gov/ct2/results?cond=cancer&term=breast&locn=&cntry=US&state=US%3ALA&city=New+Orleans&dist=&Search=Search&recrs=a&gndr=Female&age_v=23'
    quote_page = 'https://clinicaltrials.gov/ct2/results?cond='+cond.replace(" ", "%20")+'&cntry='+country+'&gndr='+gender+'&age_v='+age+'&recrs=a&intr='+intervention
    print(quote_page)
    # query the website and return the html to the variable ‘page’
    page = urllib2.urlopen(quote_page)
    
    html_soup = BeautifulSoup(page, 'html.parser')
    
    map_trails = {}
    for row in html_soup.findAll('table', {"id": "theDataTable"})[0].tbody.findAll('tr'):
        if i <= 10:
            for td in row.find("td", text="Recruiting").find_next_sibling("td"):
                #print('-'*20)
                link = 'https://clinicaltrials.gov'+str(td['href'])
                name = str(td.text) 
                #print(link)
                #print(name)
                map_trails[name] = link
                i+=1
        else:
            break
            
    
    #map_trails = json.dumps(map_trails)
    return map_trails

@app.route('/personal_trails', methods = ['GET'])
def personal_trails():

#    age = request.form['age']
#    gender = request.form['gender']
#    country = request.form['country']
    
    map_trails = get_trails()
    return render_template('personal_trails.html', map_trails=map_trails)

@app.route('/personal-trails', methods = ['POST'])
def get_personal_trails():
    age = request.form['age']
    gender = request.form['gender']
    country = request.form['country']
    intervention = request.form['intervention']
    cond = session['cond']
    map_trails = get_trails(age=age,gender=gender,country=country, intervention=intervention, cond=cond)
    blb = map_trails
    blb['personal_details'] = '{age:'+age+',gender:'+gender+',country:'+country+',intervention:'+intervention+'}'
    file = session['screen_name']+'_'+str(dt.datetime.now().timestamp())+'.json'
    print(file)
    blobService.create_blob_from_text(containerName, file, json.dumps(blb))
    return render_template('personal_trails.html', map_trails=map_trails)

@app.route('/get_topics', methods=['GET'])
def get_topics():
    tweet = request.args.get('tweet')
    json_res = topics(tweet)
    return str(json_res)

if __name__ == '__main__':
    app.run()