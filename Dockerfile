FROM python:3.9-slim

WORKDIR /worker

COPY . /worker/NLP_Analyzer

RUN test ! -e /worker/NLP_Analyzer/requirements.txt || pip install --no-cache-dir -r /worker/NLP_Analyzer/requirements.txt

ENTRYPOINT [ "python", "/worker/NLP_Analyzer/NLP_Analyzer.py" ]
