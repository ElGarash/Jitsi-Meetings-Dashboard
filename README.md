[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)



## Setup

Setup a virtual environment with python.

`python -m virtualenv venv`

Then activate the virtual environment depending on your operating system.

Windows `./venv/Scripts/activate`

Linux/MacOS `source venv/bin/activate`

Install the required packages.

`pip install -r requirements.txt`

Start the flask application.

Powershell
```
$env:FLASK_APP="app.py"
$env:FLASK_ENV="development" 
flask run --reload
```
CMD
```
set FLASK_APP=app.py
set FLASK_ENV=development
flask run --reload
```
Bash
```
export FLASK_APP=app.py
export FLASK_ENV=development
flask run --reload
```

The meeting can be accessed on `localhost:5000` and the dashboard can be accessed `localhost:5000/dashboard`

