# MetaQA
Scripts for the interrogation of multiple QA Systems on the Unica University network. Tested on Ubuntu WSL.

Install the requirements with
```pip install requirements.txt```
before running the script (you need to have pip installed).

Usage: ```python3 metaqa.py system_name data_source language question```

- system_name: ```qanswer``` or ```tebaqa```;

- data_source: ```dbpedia``` or ```wikidata``` (TeBaQA only supports DBpedia and will use it in any case);

- language: ```en```, ```de```, ```fr```, ```it```, ```es```, ```pt```, ```nl```, ```zh```, ```ar```, ```ja```, ```ru``` (TeBaQA will only accept english questions);

- question: your question within quotation marks.

Example: ```python3 metaqa.py qanswer dbpedia en "who is the president of the united states?"```

Notes:

- You will need a token to query QAnswer; you can find the instructions on how to get it here: https://doc.qanswer.ai/Tutorial-API/register-login.
After you get the token you need to go to line 41 inside ```queryQAnswer.py``` and put it inside the quotation marks.

- In order to query TeBaQA you will need to have it installed and running. You can find the system here: https://github.com/dice-group/TeBaQA.
Before running the system you should edit the port on the first line of ```/tebaqa-controller/src/main/resources/application.properties``` (from inside the TeBaQA folder)
to ```9080```, alternatively you can just change the port at line 28 of ```queryTeBaQA.py``` in ```8080``` before making a query.
