# Development

## Setting up development environment (ASSUMING WINDOWS)
1. Set up IDE...
    1. Add virtual environment for IDE
        - PyCharm -> python interpreter
1. Add virtual environment for shell (WSL)
    - Linux: 
        - `pip -m venv venv_linux`
        - `. venv_linux/bin/activate`
        - `. env.sh`
        - `pip install -r requirements.txt`
    - Windows:
        - Just use IDE virtual environment
        - `venv/Scripts/activate.bat`
        - `env.bat`
        - `pip install -r requirements.txt`
1. Set up Docker...
    1. Open Docker Hub
    1. Open shell connected to Docker Hub (WSL)
    1. run `docker-compose up -d`
    1. run `docker-compose stop reels`
    1. run `docker-compose stop worker`
1. Open shell window (WSL) to run server request handler locally (reels)
    1. run `python manage.py migrate` (set up django default database info)
    1. run `python manage.py shell` (setting up reels database info) and in the shell...
        1. run `from reels.sql.sql import get_sql_handler`
        1. run `get_sql_handler().init_database()`
        1. exit with `exit()`
    1. run `python manage.py runserver`
1. Open shell window (WSL) to run server worker for serving compilation requests
    1. run `celery -A pegasus worker -l info`