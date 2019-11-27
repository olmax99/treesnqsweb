FROM python:3.8

RUN pip install meinheld gunicorn

COPY ./entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

COPY ./start.sh /opt/start.sh
COPY ./manage.py /opt/manage.py
RUN chmod +x /opt/start.sh

COPY ./gunicorn_conf.py /gunicorn_conf.py

COPY ./app /opt/app
COPY ./blog /opt/blog
COPY ./users /opt/users
WORKDIR /opt/app/

COPY requirements.txt /opt/app/requirements.txt
RUN pip install -r requirements.txt


ENV PYTHONPATH=/opt/app

EXPOSE 8000

ENTRYPOINT ["/entrypoint.sh"]

# Run the start script, it will check for an /opt/app/prestart.sh script (e.g. for migrations)
# And then will start Gunicorn with Meinheld
CMD ["/opt/start.sh"]
