import json
from pprint import pprint as pprint
import networkx as nx

def ref_cleaner(path):
    new = None
    with open(path) as file:
        for line in file:
            new = line.replace("}{", "}, {")

    new_2 = '[' + new + ']'
    clean_articles = json.loads(new_2)

    
    return clean_articles

clean_list = ref_cleaner("path to cleaned data")

#this is the graph making part

fn_graph = nx.DiGraph()

for article in clean_list:
    for key, value in article.items():
        
        if key == 'article_doi':
            node = value
            fn_graph.add_node(value, type="article_doi")
            
        if key == 'reference_doi':
            if len(value) > 0:
                for element in value:
                    fn_graph.add_edge(node, element, type="reference_doi")
        
        if key == 'reference_urls':
            if len(value) > 0:
                for element in value:
                    fn_graph.add_edge(node, element, type="reference_url")
                

nx.write_graphml(fn_graph, "/home/alok/Documents/citizen_lab/python_scripts/literature_review/network_graph/graph_test_jul_1.graphml")
