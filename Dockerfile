FROM python:2.7
WORKDIR /app
ADD . .
RUN apt-get update
RUN apt-get -y install python-matplotlib python-numpy python-pip
RUN pip install --upgrade pip
RUN pip install -r requirements.txt -r test-requirements.txt -e .
RUN py.test tests
EXPOSE 8000
CMD python -m genetisnake.app
