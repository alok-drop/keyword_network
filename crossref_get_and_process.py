#!/usr/bin/env python
# coding: utf-8

# In[2]:

import json
import heapq
import requests
import os

class CrossrefSearch:

    def __init__(self, **kwargs):

        for key, value in kwargs.items():
            if str(key) == 'session_name':
                self.session_name = str(value).replace(' ', '_')
                if not os.path.exists(f"./{self.session_name}"):
                    os.mkdir(f"./{self.session_name}")
        
    
    def make_query(self, title, row_count, offset_count, output_name, email):
        
        if int(row_count) <= 1000:
            query = f"\nhttps://api.crossref.org/works?query.bibliographic='{title}'&filter=from-pub-date:2008&rows={row_count}&offset={offset_count}&sort=relevance&order=desc&mailto={email}" 
            response = requests.get(query)
            print("response received\n")
            data_str = json.dumps(response.json())
            crossref_json = json.loads(data_str)

            try:
                with open(f"./{self.session_name}/{output_name}.json", 'w') as file:
                    json.dump(crossref_json, file)
            
            except FileNotFoundError:
                with open(f"./{output_name}.json", 'w') as file:
                    json.dump(crossref_json, file)
        
        else:
            raise Exception('Row_count has to be an integer less than or equal to 1000. Offset_count has to be an integer ')

        return crossref_json
    
    def combine_data(self, list_of_files):
        final_article_list = []

        for file in list_of_files:
            with open(file) as article_file:
                crossref_json = json.load(article_file)
                article_list = crossref_json["message"]["items"]
        
                for article in article_list:
                    structure = {
                                'article_doi_og' : 'DOI',
                                'reference_doi_og' : [],
                                'reference_titles_og' : []
                                                    }
                    for key,value in article.items():
                        if key == 'DOI':
                            structure['article_doi_og'] = value
                        
                        if key == 'reference':
                            for ref in value:
                                try:
                                    if "DOI" and not "unstructured" in ref:
                                        structure["reference_doi_og"].append(ref["DOI"])
                    
                                    if "unstructured" and not "DOI" in ref:
                                        two_long_list = heapq.nlargest(2, (ref["unstructured"].replace("http://", '').split('.')), key=len)
                                        correct = [elt for elt in two_long_list if elt.count('/')==min([elt.count('/') 
                                                        for elt in two_long_list])]
                                        structure["reference_titles_og"].append(' '.join(correct))
                                        
                                
                                    if "DOI" and "unstructured" in ref:
                                        structure["reference_doi_og"].append(ref["DOI"])

                                except KeyError:
                                    next
                    
                    final_article_list.append(structure)
        
        return final_article_list

search_object = CrossrefSearch()

search_object.make_query('fake+news', 10, 0, 'fake_news_results_3','alokherath@gmail.com')

combined_data = search_object.combine_data(
            ['november3_crossref_results/fake_news_results_1.json', 
            'november3_crossref_results/fake_news_results_2.json']
            )

with open('fake_news_nov3.json', 'w') as outfile:
    json.dump(combined_data, outfile)

