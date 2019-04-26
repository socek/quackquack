"""
Simple Application
------------------

About this project

This project will help starting an application, which needs to have initialization
step at the beginning (for example: for gathering settings) and use them in many
places/endpoints.
For example, normally you would need to use two separate mechanism for settings
in celery application and web application, because you should not use web
application startup in the celery app. This package provide sollution for this
problem.

More info on GitHub: https://github.com/socek/sapp
"""

from setuptools import find_packages
from setuptools import setup

setup(
    name='sapp',
    version='0.3',
    description='Simple Application',
    packages=find_packages(),
    tests_require=['coverage', 'pytest', 'pytest-cov', 'WebTest'],
    long_description=__doc__,
    author='Dominik "Socek" Długajczyk',
    author_email='msocek@gmail.com',
    license='MIT',
    zip_safe=True,
    url='https://github.com/socek/sapp',
    keywords=['application', 'settings'],
    entry_points={},
    classifiers=[
        'Development Status :: 4 - Beta', 'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent', 'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7'
    ], )


