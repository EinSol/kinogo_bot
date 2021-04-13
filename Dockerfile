FROM python:3

COPY requirements.txt /kinogo_bot/requirements.txt

WORKDIR /kinogo_bot

RUN pip install --no-cache-dir -r requirements.txt

COPY . /kinogo_bot

RUN chmod a+x run.sh

CMD ["./run.sh" ]
