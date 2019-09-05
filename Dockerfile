# start from an official image
FROM python:3.7

# ADD ./config/nginx/conf.d/nginx.conf /etc/nginx/sites-enabled/nginx.conf

# arbitrary location choice: you can change the directory
RUN mkdir -p /aiohttp
WORKDIR /aiohttp

RUN pip install --upgrade pip
COPY requirements.txt /aiohttp/
RUN pip install -r requirements.txt

# install our dependencies
# we use --system flag because we don't need an extra virtualenv
COPY Pipfile Pipfile.lock /aiohttp/
RUN pip install pipenv && pipenv install --system

# copy our project code
COPY . /aiohttp

# expose the port 8080
EXPOSE 8080

# define the default command to run when starting the container
# CMD ["gunicorn", "entry:crapp", "--bind", ":8080", "--worker-class", "aiohttp.GunicornUVLoopWebWorker"]


