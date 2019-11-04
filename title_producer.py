#!/usr/bin/env python
# coding: utf-8

# In[18]:


# this is the producer title script

# it needs KafkaProducer, path, json

from kafka import KafkaProducer
import json
from time import sleep

class Production():
    def __init__(self,path):
        self.path = path
        self.producer = KafkaProducer(bootstrap_servers=['localhost:9092'],
                                     value_serializer=lambda x:
                                     json.dumps(x).encode('utf-8'))

    def send_json(self):
         with open(self.path) as file:
            json_file = (json.load(file))
            for message in json_file:
                self.producer.send('nov_4_test_1', value=message)
                print(message)

                if len(message['reference_doi_og']) + len(message['reference_titles_og']) == 0:
                    sleep(2)
                
                else:
                    sleep(40)


producer_object = Production('november3_crossref_results/fake_news_nov3_combined.json')
producer_object.send_json()


# In[ ]:
