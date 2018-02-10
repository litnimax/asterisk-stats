FROM python:3-alpine

WORKDIR /app

COPY ./main.py .
COPY ./requirements.txt .
RUN pip3 install -r requirements.txt

ENV AMI_HOST=localhost AMI_USER=odoo AMI_SECRET=odoo PUSH_GATEWAY=localhost:9091

CMD ["python3", "main.py"]
