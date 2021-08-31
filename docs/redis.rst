Redis
=====

This plugin connects to the Redis database. It will return ``redis.Redis`` connection
to the context.

In order to use it, you need to add these settings:

.. code-block:: python

   def redis(settings):
       return {
           "host": "redis",
           "port": 6379,
           "db": 0,
       }


Second step is to add the plugin, like any other plugins:

.. code-block:: python


   class MyApplication(Application):
       def create_plugins(self):
           self.plugins[REDIS_PLUGIN_KEY] = RedisPlugin()


The ctx_key is 'redis' by default. Now you can use it in your application:

.. code-block:: python

   with Context(app) as ctx:
       print(ctx[REDIS_PLUGIN_KEY])
       assert type(ctx[REDIS_PLUGIN_KEY]) == redis.Redis


