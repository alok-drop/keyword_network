# Literature Review - Keyword Network Builder

## The purpose of this project:

The purpose of this project is to create a lay of the land on academic articles that references a given key word.
Using the Crossref citation database, keyword_network aims to build a network graph of articles that reference
a given keyword, allowing researchers to see the current state of academic thought on a specific subject.

## Code that is involved:

- crossref_get_and_process.py queries the crossref database for a given keyword and returns a JSON of citations to parse
- titles_producer.py parses the json — cleaning lazy citations from the json — and publishes article titles 
to a Kafka message queue. Sometimes only partial article titles can be extracted from the citation, which have to be processed 
in the next step.
- titles_consumer.py reads from the message queue and attempts to resolve a *complete* article title from 
the *partial* titles produced by the producer script. This resolving process uses Crossref and Google search to give a best guess
at the complete title.
