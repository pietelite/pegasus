# Development

## Setting up development environment (ASSUMING WINDOWS)
1. Set up IDE...
    1. Add virtual environment for IDE
        - PyCharm -> python interpreter
1. Add virtual environment for shell (WSL)
    - Linux: 
        - `pip -m venv venv_linux`
        - `. venv_linux/bin/activate`
        - `pip install -r requirements.txt`
    - Windows:
        - Just use IDE virtual environment
1. Set up Docker...
    1. Open Docker Hub
    1. Open shell connected to Docker Hub (WSL)
    1. run `docker-compose up -d`
    1. run `docker-compose stop reels`
    1. run `docker-compose stop worker`
1. Open shell window (WSL) to run server request handler locally (reels)
    1. run `python manage.py runserver`
1. Open shell window (WSL) to run server worker
    1. run `celery -A pegasus worker -l info`