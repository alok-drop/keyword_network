#!/usr/bin/env python
# coding: utf-8

# In[ ]:


# this is the consumer script

from bs4 import BeautifulSoup
from fuzzywuzzy import fuzz
import json
from kafka import KafkaConsumer
from operator import itemgetter
import random
import requests
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import NoSuchElementException
import time


class Title_Consumer():

    def __init__(self):

        self.consumer = KafkaConsumer('jul_13_test',
        bootstrap_servers=['localhost:9092'],
        auto_offset_reset='latest',
        enable_auto_commit=False,
        group_id='my-group',
        max_poll_interval_ms=100000,
        value_deserializer=lambda x: json.loads(x.decode('utf-8')))

        self.driver = webdriver.Firefox()
        self.print_file = open('failed_news_results.txt', 'a')


    def search_function(self):
        for message in self.consumer:
            print("\n producer message received \n")
            structure = {
                            'article_doi' : 'DOI',
                            'reference_doi' : [],
                            'reference_urls' : []
                                    }
            for key, value_ in message.value.items():

                if key == 'article_doi_og':
                    structure['article_doi'] = value_

                if key == 'reference_doi_og':
                    structure['reference_doi'].extend(value_)

                if key == 'reference_titles_og':
                    # search part of the function
                    for title in value_:
                        try:
                            self.driver.get(f"https://google.com/search?q={title}")
                            soup1 = BeautifulSoup(self.driver.page_source, 'html.parser')
                            title_tag = soup1.find_all('h3', {'class': 'LC20lb'})[0].get_text().replace("&", " and ")
                            query = f"\nhttps://api.crossref.org/works?query.title='{title_tag}'&rows=3&offset=0&select=DOI,title&mailto=alokherath@gmail.com" #change to string formatting
                            print(query, '\nhas been sent to crossref api')

                            # turning response into a parsable json
                            response = requests.get(query)
                            print("response received\n")
                            data_str = json.dumps(response.json())
                            crossref_json = json.loads(data_str)

                            #cross ref yields the metadata of a list of three articles
                            crossref_list = crossref_json['message']['items']

                            #check if crossref titles are a good match for producer title
                            title_list = []

                            for article in crossref_list:
                                cref_fuzz_ratio = fuzz.partial_token_sort_ratio(article['title'], title)
                                if cref_fuzz_ratio > 75:
                                    title_list.append((str(article['title']), cref_fuzz_ratio))

                            if title_list:
                                most_likely_title = max(title_list, key = itemgetter(1))[0]
                                structure['reference_doi'].append(article['DOI'])
                                print("crossref chosen! ", most_likely_title, article['DOI'] + "\n")

                            else:
                                if fuzz.partial_token_sort_ratio(str(title_tag), title) > 60:

                                    url_tags = soup1.find_all('div', "r") #returns a resultset (list of bs4 tags)
                                    url = url_tags[0].find('a')['href'] #finds first url
                                    structure['reference_urls'].append(url)
                                    print("url chosen instead!", url, "\n")
                                else:
                                    print("title cannot be found!\n")
                                    print(str(title_tag), title, file=self.print_file)

                            time.sleep(random.uniform(1.00, 5.00))
                        except (IndexError, NoSuchElementException, KeyError) as e:
                            pass

                print(structure['reference_urls'])

            with open('fake_news_jul_13.json', 'a') as outfile:
                json.dump(structure, outfile)

consumer_object = Title_Consumer()
consumer_object.search_function()
