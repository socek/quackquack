Celery Plugin
=============

About
-----

This plugin allows to integrate Quack Quack with Celery_ - Distributed Task Queue.

.. _Celery: https://docs.celeryproject.org/en/stable/

Dependencies
------------

* SettingsPlugin

Integration & implementation
----------------------------

Celery is pretty straightforward, because this tool comes with it's own worker
and scheduler application and they both expect only the Celery app object. Quack
Quack needs only to configure this object.

So first, we need place to create the Celery app object, for example: `app/capp.py`

.. code-block:: python
    :caption: something/app/capp.py

    from celery import Celery

    celery_app = Celery("something")

Then, we need to add the Celery plugin to QQ application:

.. code-block:: python
    :caption: something/app/app.py

    from qq import Application
    from qq.plugins import SettingsPlugin
    from qq.plugins.celery.plugin import CeleryPlugin

    from something.app.capp import celery_app


    class SomethingApplication(Application):
        def create_plugins(self):
            self.plugins(SettingsPlugin("something.app.settings"))
            self.plugins(CeleryPlugin(celery_app))


    application = SomethingApplication()

And of course, the settings. All created settings will be passed to
celeryapp.conf.update method. You can read more here_.

.. _here: https://docs.celeryproject.org/en/stable/userguide/application.html#configuration

.. code-block:: python
    :caption: something/app/settings.py

    from qq.plugins.types import Settings
    from qq.plugins.celery.plugin import CeleryPlugin


    def default() -> Settings:
        return {CeleryPlugin.key: celerysettings()}


    def celerysettings() -> Settings:
        host = "localhost"
        user = "guest"
        password = "guest"
        vhost = ""
        port = 5672

        return {
            "broker_url": f"amqp://{user}:{password}@{host}:{port}/{vhost}/",
        }

So our QQ configuration code is ready. Now we need to start a worker and a scheduler.
For this purpose we need to:
- get the Celery app object
- import all tasks, so the Celery app will know of their existance
- start QQ application

.. code-block:: python
    :caption: cstart.py

    from qq.plugins.celery.finder import TaskFinder

    from something.app.app import application
    from qqe.capp import celery_app

    application.start("celery")
    TaskFinder(["something"], celery_app=celery_app).find()
    print("Starting celery")

`TaskFinder` is an ObjectFinder that will auto import thru all the modules in
the package and find all Celery tasks.

Now we can start a worker and a scheduler with this simple commands:

.. code-block:: bash
    :caption: Starting the worker

    celery -A cstart worker


.. code-block:: bash
    :caption: Starting the scheduler

    celery -A cstart beat

And that's pretty much it.

Example task
------------

In prevoius section we've created a simple Integration with the celery (please
remember, that if you need to have running broker in the background. For
more information please go to the Celery's tutorial_).

.. _tutorial: https://docs.celeryproject.org/en/stable/getting-started/first-steps-with-celery.html

Now we can create a simple task.

.. code-block:: python
    :caption: something/tasks.py

    from something.app.capp import celery_app

    @celery_app.task
    def celeryprint():
        print("This is a celery task:")


Now we can create a simple command that will start this task.

.. code-block:: python
    :caption: command.py

    from something.app.app import application
    from something.tasks import celeryprint

    if __name__ == "__main__":
        application.start("default")
        celeryprint.delay()
        print("Send task to queue...")

So after running this, the task will be sent to queue and will be executed by
the worker.
