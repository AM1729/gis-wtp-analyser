FROM python:3.11-slim

WORKDIR /root
COPY ./requirements.txt ./requirements.txt
RUN pip install -r requirements.txt
COPY . .

ENTRYPOINT [ "streamlit", "run", "/root/survey_taker.py"]