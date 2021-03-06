# bt-protocol-processing

## Requirements

- pipenv (tested with version 2021.5.29)

## Setup

1. In the projects root folder run:
```
pipenv install
```

2. Assuming you have set the environment variable `PIPENV_VENV_IN_PROJECT="enabled"`, in the projects root folder run:

- For Windows:
```
.\.venv\Scripts\python.exe -m spacy download de_core_news_sm
```

- For Unix:
```
.\.venv\bin\python -m spacy download de_core_news_sm
```

3. Setup Neo4j Graph Data Science Library by following https://neo4j.com/docs/graph-data-science/current/installation/neo4j-server/

## Run

In the projects root folder run:
```
pipenv run python main.py
```
