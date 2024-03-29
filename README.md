# Literature Review - Keyword Network Builder

## The purpose of this project:

The purpose of this project is to create a lay of the land on academic articles that reference a given keyword.
Using the Crossref citation database, keyword_network aims to build a network graph of articles that reference
a given keyword, allowing researchers to see the current state of academic thought on a specific subject.

## Problems this project faced:

The Crossref database has a wealth of citation information, but that information is user submitted, and sometimes, highly inconsistent. To overcome this, significant data-cleaning had to take place before any literature network map is generated. I initially struggled with coming up with a solution that was good enough at parsing out inconsistent citations from the API response. After linking together several algorithms, I came up with a solution that used fuzzy wuzzy and regex methods to remove most
of the egregious citation offenders.

## Code that is involved:

- tools.py contains a number of tools required to make the Crossref API query, clean and combine the data, and create a network graph from the title_consumer.py results.
- titles_producer.py parses the json — cleaning lazy citations from the json — and publishes article titles 
to a Kafka message queue. Sometimes only partial article titles can be extracted from the citation, which have to be processed 
in the next step.
- titles_consumer.py reads from the message queue and attempts to resolve a *complete* article title from 
the *partial* titles produced by the producer script. This resolving process uses Crossref and Google search to give a best guess
at the complete title.
