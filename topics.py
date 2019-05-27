# -*- coding: utf-8 -*-
"""
Created on Sun May 26 13:15:52 2019

@author: vsriram7
"""

from joblib import dump, load

def topics(tweet):
    #tweet = request.args.get('tweet')
    vectorizer = load('tf_vectorizer.joblib') 
    model = load('nmf.joblib')
    #text = "My friend suffering from #lungcancer #lcsm need support from you all. We are also planning to setup #lungcancerawareness meetings in our neighbourhood"
    text = tweet
    nmf_topics = model.transform(vectorizer.transform([text]))[0]
    topic_idx = 0
    json_res = {}
    nmf_map = {'Topic 0':'Lung Cancer',
          'Topic 1':'Breast Cancer and Women',
          'Topic 2':'Diabetes and heart realted',
          'Topic 3':'Early Stage Lung Cancer',
          'Topic 4':'Epilepsy and Seizures',
          'Topic 5':'Heart Stroke'}
    for topic in nmf_map:
        print(topic+' '+nmf_map[topic]+' '+str(nmf_topics[topic_idx]))
        json_res[nmf_map[topic]] = nmf_topics[topic_idx]
        topic_idx+=1
    return str(json_res)

