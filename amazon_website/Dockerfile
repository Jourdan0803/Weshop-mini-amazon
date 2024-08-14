FROM python:3
ENV PYTHONUNBUFFERED 1

WORKDIR /code
ADD requirements.txt /code/
RUN pip install -r requirements.txt
ADD . /code/
RUN mkdir -p /code/amazon/static/media/user_images && \
    chmod -R 777 /code/amazon/static/media/user_images
RUN chmod 777 run_amazon.sh
# EXPOSE 34521
# CMD ["python3", "manage.py", "runserver","0.0.0.0:8000", "--noreload"]