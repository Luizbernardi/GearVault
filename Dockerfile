ARG PYTHON_VERSION=3.11-slim-bullseye
FROM python:${PYTHON_VERSION}

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN mkdir -p /code

WORKDIR /code

COPY requirements.txt /tmp/requirements.txt
RUN set -ex && \
    pip install --upgrade pip && \
    pip install -r /tmp/requirements.txt && \
    rm -rf /root/.cache/

COPY . /code

# Criar diretórios necessários
RUN mkdir -p /code/media /code/staticfiles

# Tornar o script executável
RUN chmod +x /code/start.sh

ENV SECRET_KEY "MaOkwTU3Ec2QkEqU6kSoYeeiSvCbOrL4eBU0JdwEOCdFod5POe"
ENV DEBUG "False"
RUN python manage.py collectstatic --noinput

EXPOSE 8000

# Usar o script de inicialização
ENTRYPOINT ["/code/start.sh"]
CMD ["gunicorn","--bind",":8000","--workers","2","core.wsgi"]
