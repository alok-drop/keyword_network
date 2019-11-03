import json
import random

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
    
    def random_sample(self, sample_size):
        if sample_size < len(self.file_object):
            return (random.sample(self.file_object, sample_size))
        else:
            print("Sample size has to be less than population")


test_unit = LiteratureTest("./fixed_citations.json")
random_sample = test_unit.random_sample(5)
