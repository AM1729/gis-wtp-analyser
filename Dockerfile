FROM python:3.11-slim

WORKDIR /root
COPY . .
RUN pip install -r requirements.txt
RUN ls

ENTRYPOINT [ "streamlit", "run", "/root/survey_taker.py"]