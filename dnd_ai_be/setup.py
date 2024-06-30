from setuptools import setup, find_packages

setup(
    name='dnd_ai_be',
    version='0.1',
    packages=find_packages(include=['dnd_ai_be', 'dnd_ai_be.*']),
    install_requires=[
        'Flask',
        'langchain>=0.0.354',
        'langchain_community',
        'langchain_chroma',
        'langchain_openai',
        'pymongo',
        'langchain_text_splitters',
        'flask-cors',
        'motor',
        'beautifulsoup4',
    ],
)