# Simple-Generic-ML-Model-Server

This is a python-flask application to open saved machine learning models to outer world prediction with rest calls. 

It has a watcher module which is written benefiting from os.stat module. Watcher module polls the model directory to observe and notify server when model files change. 

Before running project, be sure that the environment variable for $PROJECT_HOME is set to the python projects directory and this repo cloned in this directory as well. It should be set explicitly from command line while in environment:

- export PROJECT_HOME=/your_home_dir/your_python_workspace/

You can install dependencies for your virtual environment as follows:
- pip install -r requirements.txt

If bash commands are not the things that you are familier with you can edit the config.yaml to point right path for your model files.

Watcher and server are not hard-coupled. If one does not work the other keeps working. If watcher or server stops models will be reloaded. 

The application can be started with running following commands in project root dir:

- python app.py  
- python src/watcher.py

  
