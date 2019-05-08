FROM python:3.7

# Configuration
ENV PYTHONUNBUFFERED 1
ENV EGG_INFO_NAME sappexample
ENV APP_DIR /code
ENV USER_NAME user
ENV USER_DIR /home/${USER_NAME}

# Create dev user
RUN useradd -U $USER_NAME && mkdir -p $USER_DIR && chown $USER_NAME:$USER_NAME $USER_DIR && chmod 777 $USER_DIR

# Create code dir
WORKDIR $APP_DIR
RUN chmod 777 $APP_DIR

# Workaround for `python setup.py develop` and using volume /code.
# It creates symlink wich is outside of the volume /code, so the egg-info data will always be on the docker image.
RUN mkdir -p /app.egg-info && ln -s ../app.egg-info ${EGG_INFO_NAME}.egg-info && chown $USER_NAME:$USER_NAME /app.egg-info

# Install pipenv. Pipenv is a better then pip tool for managing packages.
RUN pip install pipenv

# Install dependencies
USER $USER_NAME
COPY --chown=user:user code/Pipfile $APP_DIR
COPY --chown=user:user code/Pipfile.lock $APP_DIR
RUN pipenv install

# Copy all the code and run setuo.py
COPY --chown=user:user code $APP_DIR
RUN pipenv run python setup.py develop

ENTRYPOINT ["pipenv", "run"]
