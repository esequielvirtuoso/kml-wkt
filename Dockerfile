FROM ubuntu:bionic

COPY . /app
WORKDIR /app

# Work around para o problema de encoding utf-8
RUN chmod +x init.sh && ./init.sh

RUN sed -i -e 's/# en_US.UTF-8 UTF-8/en_US.UTF-8 UTF-8/' /etc/locale.gen && \
    locale-gen
ENV LANG en_US.UTF-8
ENV LANGUAGE en_US:en
ENV LC_ALL en_US.UTF-8
ENV PYTHONIOENCODING UTF-8
RUN cat /etc/default/locale
RUN locale-gen en_US.UTF-8

# Define default command.
CMD ["python3", "app.py"]