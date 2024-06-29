from setuptools import setup, find_packages

setup(
    name='dnd_ai_be',
    version='0.1',
    packages=find_packages(include=['dnd_ai_be', 'dnd_ai_be.*']),
    install_requires=[
        'Flask',
        'langchain',
        'langchain_community',
        'flask-swagger-ui',
        'flask-cors',
    ],
)