import json

path = "/home/alok/Documents/citizen_lab/python_scripts/json_dumps/fake_news_titles_update.json"


"""goal is to find before and after node counts = article doi 
+ reference doi + reference titles"""

big_count = 0
with open(path) as file:
    json_file = (json.load(file))

    doi_sum = 0
    title_sum = 0

    for article in json_file:
        doi_sum += len(article['reference_doi_og'])
        title_sum += len(article['reference_titles_og'])
        
    #     for key,value in article.items():

    #         if key == 'reference_doi_og':
    #             for ref in value:
    #                 doi_sum += 1
            
    #         if key == 'reference_titles_og':
    #             for ref in value:
    #                 title_sum += 1

            

    print(doi_sum)
    print(title_sum)

        