#!/usr/bin/env python
# coding: utf-8

# In[ ]:


# this is the consumer script

from bs4 import BeautifulSoup
from fuzzywuzzy import fuzz
import json
from kafka import KafkaConsumer
from operator import itemgetter
import os
import random
import requests
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import NoSuchElementException
import time


class Title_Consumer():

    def __init__(self, session_name):

        self.consumer = KafkaConsumer('nov_3_test_1',
            bootstrap_servers=['localhost:9092'],
            auto_offset_reset='latest',
            enable_auto_commit=False,
            group_id='my-group',
            max_poll_interval_ms=100000,
            value_deserializer=lambda x: json.loads(x.decode('utf-8')))
        self.driver = webdriver.Firefox()
        self.session_name = str(session_name).replace(' ', '_')
        
        if not os.path.exists(f"./{self.session_name}"):
            os.mkdir(f"./{self.session_name}")

    def search_function(self):
        for message in self.consumer:
            print("\n producer message received \n")
            
            #populated with successful citation resolutions
            structure = {
                            'article_doi' : 'DOI',
                            'reference_doi' : [],
                            'reference_urls' : []
                                    }

            #populated with failed citation title fragments. Saved for logging and verification purposes.
            failed_structure = {
                                    'article_doi': 'DOI',
                                    'failed_title_fragments': []
                                        }
            #populated with successful citation title fragments to url resolutions. Saved for verification purposes.
            successful_url_structure = {
                                            'article_doi': 'DOI',
                                            'resolved_titles': []
                                                }


            for key, value_ in message.value.items():

                # populating structures with article doi
                if key == 'article_doi_og':
                    structure['article_doi'] = value_
                    failed_structure['article_doi'] = value_
                    successful_url_structure['article_doi'] = value_

                # populating structure with reference dois if they exist
                if key == 'reference_doi_og':
                    structure['reference_doi'].extend(value_)

                # to resolve a citation title fragment into a url, multiple steps are needed.
                # first, the script turns the title fragment into a 'cleaned' title fragment by running it through
                # google search.
                # next, the script passes the 'cleaned' title fragment to crossref api to try and find a doi match for
                # the title fragment.
                # if the crossref api returns a result that is similar, then that doi replaces the title fragment as its
                # unique identifier.
                # if the result is dissimilar, then the script attempts to resolve the title to a url as opposed to a doi.
                # to do this, the title fragment is passed through google search. if the title fragment is similar
                # to the google search results' title, then the google search title url is taken as the unique identifier.
                # else, the title fragment is discarded as a failed title.
                # in summary, a title fragment from the raw crossref metadata is converted to a doi, url, or discarded.

                if key == 'reference_titles_og':
                    # search part of the function
                    for title in value_:
                        try:
                            #take the title from crossref metadata and 'clean' it through google search to find doi/url
                            self.driver.get(f"https://google.com/search?q={title}")
                            soup1 = BeautifulSoup(self.driver.page_source, 'html.parser')
                            title_tag = soup1.find_all('h3', {'class': 'LC20lb'})[0].get_text().replace("&", " and ")
                            
                            #pass cleaned title to crossref database to try and find doi match
                            query = f"\nhttps://api.crossref.org/works?query.bibliographic='{title_tag}'&rows=3&offset=0&select=DOI,title&mailto=alokherath@gmail.com" #change to string formatting
                            print(query, '\nhas been sent to crossref api')
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
                                    successful_url_structure['resolved_titles'].append({str(url):str(title)})
                                    print("url chosen instead!", url, "\n")
                                
                                else:
                                    print("title cannot be found!\n")
                                    failed_structure['failed_title_fragments'].append(title)

                            time.sleep(random.uniform(1.00, 5.00))
                        except (IndexError, NoSuchElementException, KeyError) as e:
                            pass

                print(structure['reference_urls'])

            with open(f"./{self.session_name}/{self.session_name}_results.json", 'a') as outfile:
                json.dump(structure, outfile)
            
            with open(f"./{self.session_name}/{self.session_name}_urls.json", 'a') as outfile2:
                json.dump(successful_url_structure, outfile2)

            with open(f"{./{self.session_name}/self.session_name}_failed.json", 'a') as outfile3:
                json.dump(failed_structure, outfile3)

"""change selenium google search to use full title, not only google cleaned title! You are Losing
too many results. To confirm, see how many nodes you get in gephi

"""

consumer_object = Title_Consumer("November 3")
consumer_object.search_function()
