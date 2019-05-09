from setuptools import find_packages
from setuptools import setup

setup(
    name='sappexample',
    version='0.1',
    description='Simple Application Example',
    packages=find_packages(),
    tests_require=['coverage', 'pytest', 'pytest-cov', 'WebTest'],
    long_description=__doc__,
    author='Dominik "Socek" Długajczyk',
    author_email='msocek@gmail.com',
    license='MIT',
    zip_safe=True,
    url='https://github.com/socek/sapp',
    keywords=['application', 'settings'],
    entry_points={
        "paste.app_factory": ["main = example.application.startpoints:wsgi"]
    },
    classifiers=[
        'Development Status :: 4 - Beta', 'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent', 'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7'
    ], )


