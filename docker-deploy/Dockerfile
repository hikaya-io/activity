# Set base image
FROM python:3.7-alpine

# Set working directory
WORKDIR /app

# Prevents Python from writing pyc files to disc
# and prevents Python from buffering stdout and stderr
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1 

# Update default packages and install application dependancies
RUN apk -U update --no-cache 

# https://github.com/pyca/cryptography/blob/main/docs/installation.rst#alpine
RUN apk add openssl-dev cargo

RUN apk add bash gcc musl-dev jpeg-dev zlib-dev libffi-dev cairo-dev pango-dev gdk-pixbuf && \
    apk add postgresql-dev gcc python3-dev musl-dev && \
    pip install --upgrade pip 
    
# Copy all project files
COPY . /app

# Make the start file executable and delete installation cache, reduces image size
RUN pip install -r requirements.txt && \
    chmod 777  docker-deploy/start_app.sh && \
    rm -rf /root/.cache && \
    sed -i "s/EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'/EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'/" activity/settings/local-sample.py && \
    mv /app/activity/settings/local-sample.py /app/activity/settings/local.py

# Set the entry point where the application can be started on
ENTRYPOINT ["docker-deploy/start_app.sh"]
