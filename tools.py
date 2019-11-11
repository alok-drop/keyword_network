import json
import random
import csv
import networkx as nx
import heapq
import requests
import os
import re

"""This file contains a set of tools required to carry out an automated literature review. 

    CrossrefSearch:

    - __init__ method creates working directory
    - make_query() makes the Crossref API query and returns a JSON 
    - clean_combine_dataset() cleans the data returned from make_query() and combines multiple JSONs,
    if present. It returns the list of articles and citation data that is passed to the producer script

    FixJson:

    - ref_cleaner() takes the malformed output of the consumer script and modifies it so that it can be 
    processed. This class will be depreciated once a cleaner workaround is formed within the consumer script.

    GraphCreate:

    - __init__ method instatiates a networkx directed graph.
    - create_graph() populates the DiGraph object with nodes (articles) and edges (citation relationships)

    LiteratureTest:

    - __init__ method instantiates the results JSON file that you are testing
    - summary() provides high-level summary statistics on the dataset
    - random_sample() generates a random sample of data that can be manually reviewed for accuracy. Current
    testing options include:
        - verifying if the citation title fragment generated from CrossrefSearch.clean_combine_dataset() is 
        correctly resolved within the consumer script logic 

"""

class CrossrefSearch:

    #This class queries the Crossref API for an user submitted search request.

    def __init__(self, **kwargs):

        for key, value in kwargs.items():
            if str(key) == 'session_name':
                self.session_name = str(value).replace(' ', '_')
                if not os.path.exists(f"./{self.session_name}"):
                    os.mkdir(f"./{self.session_name}")
        
    
    def make_query(self, title, row_count, offset_count, email, **output):
        
        if int(row_count) <= 1000:
            query = f"\nhttps://api.crossref.org/works?query.bibliographic='{title}'&filter=from-pub-date:2008&rows={row_count}&offset={offset_count}&sort=relevance&order=desc&mailto={email}" 
            response = requests.get(query)
            print("Response received\n")
            data_str = json.dumps(response.json())
            crossref_json = json.loads(data_str)

            if crossref_json['message']['total-results'] < row_count:
                print(f"Row count is greater than results available. Total available results are {crossref_json['message']['total-results']}")
            
            if output.get('output_name'):
                try:
                    with open(f"./{self.session_name}/{output['output_name']}.json", 'w') as file:
                        json.dump(crossref_json, file)
                
                except (FileNotFoundError, AttributeError) as e:
                    with open(f"./{output['output_name']}.json", 'w') as file:
                        json.dump(crossref_json, file)

            return response.json()

        else:
            raise Exception('Row_count has to be an integer less than or equal to 1000. Offset_count has to be an integer ')

        
    
    def clean_combine_data(self, list_of_files, **output):
        
        # Clean: Crossref API data is messy. This script first parses malformed citation data to remove unsuitable 
        # data that hinders the accuracy of subsequent steps.

        # Combine: Crossref API returns 1000 rows on each call. Thus, if you want more than 1000 results in your final
        # data set, you will have to make multiple API queries. This function combines the results of multiple API
        # queries into a single json file.
        
        final_article_list = []

        for file in list_of_files:
            # Script iterates over a list of Crossref API JSONs. 
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
                                        no_url = re.sub(r'(https|http)?:\/\/(\w|\.|\/|\?|\=|\&|\%|\-)*\b', '', ref['unstructured'])
                                        no_white_space = ' '.join(no_url.split())
                                        two_long_list = heapq.nlargest(2, (no_white_space.split('.')), key=len)
                                        correct = [elt for elt in two_long_list if elt.count('/')==min([elt.count('/') 
                                                        for elt in two_long_list])]
                                        structure["reference_titles_og"].append(' '.join(correct))
                                
                                    if "DOI" and "unstructured" in ref:
                                        structure["reference_doi_og"].append(ref["DOI"])

                                except KeyError:
                                    next
                    
                    final_article_list.append(structure)
        
        if output.get('output_name'):
            try:
                with open(f"./{self.session_name}/{output['output_name']}_clean.json", 'w') as file:
                    json.dump(final_article_list, file)
            
            except (FileNotFoundError, AttributeError) as e:
                with open(f"./{output['output_name']}_clean.json", 'w') as file:
                    json.dump(final_article_list, file)
        
        return final_article_list

class FixJson:

    # This class fixes the malformed jsons from the consumer script. Will be replaced in the future.

    def ref_cleaner(self, path, output, **kwargs):
        self.path = path
        self.output = output
        
        new = None
        with open(self.path) as file:
            for line in file:
                new = line.replace("}{", "}, {")

        new_2 = '[' + new + ']'
        clean_articles = json.loads(new_2)
        
        with open(f'{self.output}_fixed_citations.json', 'w') as file:
            json.dump(clean_articles, file)
        
        return clean_articles


class GraphCreate:

    # This class creates a graphml file from the parsed json produced by the consumer script.

    def __init__(self):
        #create networkx di-graph object
        self.fn_graph = nx.DiGraph()
    
    def create_graph(self, path_to_list, **output_path):
        with open(path_to_list, 'r') as file:
            for article in json.load(file):
                for key, value in article.items():
                    
                    if key == 'article_doi':
                        node = value
                        self.fn_graph.add_node(value, type="article_doi")
                        
                    if key == 'reference_doi':
                        if len(value) > 0:
                            for element in value:
                                self.fn_graph.add_node(element, type="reference_doi")
                                self.fn_graph.add_edge(node, element, type="reference_doi")
                    
                    if key == 'reference_urls':
                        if len(value) > 0:
                            for element in value:
                                self.fn_graph.add_node(element, type="reference_url")
                                self.fn_graph.add_edge(node, element, type="reference_url")

        if output_path.get('output_path'):       
            nx.write_graphml(self.fn_graph, output_path['output_path'])
            return self.fn_graph

        else:
            return self.fn_graph



class LiteratureTest:

    # This class is to support the validation of this methodologies' outputs.

    def __init__(self, path_to_file):

        with open(path_to_file) as file:
            self.file_object = json.load(file)

    def summary(self):
        # Provides a high-level summary of the data.
        doi_sum = 0
        title_sum = 0

        for article in self.file_object:
            doi_sum += len(article['reference_doi'])
            title_sum += len(article['reference_urls'])
        
        return (print(
                f"Total number of citation DOIs {doi_sum}\n", 
                f"Total number of citation references {title_sum}")
                    )
    
    def random_sample(self, sample_size, **kwargs):

        # This function generates a random sample from the results dataset.
        # To make this function work with post results change the key names in the script

        if kwargs.get('guarantee') == 'url':
            url_guarantee = []
            for article in self.file_object:
                if len(article['resolved_titles']) > 1:
                    url_guarantee.append(article)
            
            return (random.sample(url_guarantee, sample_size))

        elif kwargs.get('guarantee') == 'doi':
            doi_guarantee = []
            for article in self.file_object:
                if len(article['resolved_doi']) > 1:
                    doi_guarantee.append(article)
            
            return (random.sample(doi_guarantee, sample_size))

        elif kwargs.get('guarantee') == 'both':
            both_guarantee = []
            for article in self.file_object:
                if (len(article['resolved_titles']) and len(article['reference_doi'])) > 1:
                    both_guarantee.append(article)
            
            return (random.sample(both_guarantee, sample_size))