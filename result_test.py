import json
import random
import csv

"""This script aims to provide all the testing tools to validate data"""

class LiteratureTest:

    def __init__(self, path_to_file):

        with open(path_to_file) as file:
            self.file_object = json.load(file)

    def summary(self):
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
        # this function can parse both post results as well as url results
        # to make this function work with post results change the key names in the script
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


test_unit = LiteratureTest("November_5_post/nov_5_url_fixed_citations.json")
random_sample = test_unit.random_sample(50, guarantee='url')

random_sample


import csv

with open('dict.csv', 'w') as csv_file:
    writer = csv.writer(csv_file)
    for article in random_sample:
        for keys1, values1 in article.items():
            if keys1 == 'resolved_titles':
                #returns a list of dictionaries
                for citation in values1:
                    for key, value in citation.items():
                        writer.writerow([key, value])

