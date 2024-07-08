from setuptools import setup, find_packages

setup(
    name='dnd_ai_be',
    python='3.10',
    version='0.1',
    packages=find_packages(include=['dnd_ai_be', 'dnd_ai_be.*']),
    install_requires=[
        'Flask',
        'langchain>=0.0.354',
        'langchain_community',
        'langchain_chroma',
        'langchain_openai',
        'langchain_text_splitters',
        'langchain_mongodb',
        'pymongo',
        'flask-cors',
        'motor',
        'beautifulsoup4',
    ],
)

# beautifulsoup4==4.12.3
# Flask==3.0.3
# Flask_Cors==4.0.1
# flask_swagger_ui==4.11.1
# langchain==0.2.6
# langchain_chroma==0.1.2
# langchain_community==0.2.6
# langchain_core==0.2.11
# langchain_mongodb==0.1.6
# langchain_openai==0.1.14
# langchain_text_splitters==0.2.2
# pymongo==4.8.0
# python-dotenv==1.0.1
# setuptools==69.5.1

# Flask
# langchain
# langchain_community
# langchain_chroma
# langchain_openai
# langchain_text_splitters
# flask-swagger-ui
# flask-cors
# psycopg2-binary
