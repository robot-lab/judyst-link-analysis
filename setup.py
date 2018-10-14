from setuptools import setup, find_packages
from os.path import join, dirname
import link_analysis

setup(
    name='link_analysis',
    version=link_analysis.__version__,
    packages=find_packages(),
    long_description=open(join(dirname(__file__), 'README.md')).read(),
    install_requires=[
        'networkx==2.2',
        'matplotlib==3.0.0',
        'python-dateutil==2.7.3',
        'web_crawler==0.1'
    ],
    dependency_links=[
        r'https://github.com/robot-lab/judyst-web-crawler/tree/secondIteration/dist/\
        web_crawler-0.1-py3-none-any.whl#egg=web_crawler-0.1'
    ],
    entry_points={
        'console_scripts':
            ['link_analysis = link_analysis.__main__:main']
        }
)
