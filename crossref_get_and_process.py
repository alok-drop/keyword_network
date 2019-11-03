#!/usr/bin/env python
# coding: utf-8

# In[2]:

import json
import requests

title_tag = 'fake news'
query = f"\nhttps://api.crossref.org/works?query.bibliographic='{title_tag}'&filter=from-pub-date:2008&rows=1000&mailto=alokherath@gmail.com" 

# turning response into a parsable json
response = requests.get(query)
print("response received\n")
data_str = json.dumps(response.json())
crossref_json = json.loads(data_str)

with open('fake_news_crossref_results_1.json', 'w') as file:
    json.dump(crossref_json, file)


# In[8]:

import heapq
import json

file_list = ["/home/alok/Documents/citizen_lab/python_scripts/json_dumps/fake_news_crossref_results_1.json", 
"/home/alok/Documents/citizen_lab/python_scripts/json_dumps/fake_news_crossref_results_2.json"]

final_article_list = []

for file in file_list:
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

print(len(final_article_list))
print(final_article_list)
            


# In[9]:


with open('/home/alok/Documents/citizen_lab/python_scripts/json_dumps/fake_news_titles_update.json', 'w') as outfile:
    json.dump(final_article_list, outfile)



#%%
