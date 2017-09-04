from setuptools import find_packages
from setuptools import setup

install_requires = [
    'pyramid>=1.9',
    'PyYAML>=3.12',
    'colander>=1.3.3',
    'morfdict>=0.4.6',
]

if __name__ == '__main__':
    setup(
        name='qapla',
        version='0.2.1',
        packages=find_packages(),
        install_requires=install_requires,
        license='Apache License 2.0',
    )
