#!/usr/bin/python

from pynt import task
import subprocess
import shutil
import os

CUR_DIR = os.getcwd()
BACKEND_DIR = CUR_DIR + "/backend"
FRONTEND_DIR = CUR_DIR + "/frontend"
SUPER_EMAIL = "superuser@email.com"
SUPER_PASSWORD = "superuser@123"


@task()
def clean():
    """Removes Cache and Coverage Output Files"""
    print("Start: Cleaning Project")
    deleteDirs = set(["__pycache__", ".pytest_cache", "coverage", "htmlcov", "items"])
    deleteFiles = set([".coverage", "coverage.xml", ".pyo", ".pyc"])
    ignoreDirs = set([".git", "venv", ".tox"])
    for root, dirs, files in os.walk(CUR_DIR, topdown=True):
        for dirName in ignoreDirs:
            if dirName in dirs:
                dirs.remove(dirName)
        for dirName in dirs:
            if dirName in deleteDirs:
                shutil.rmtree(f"{root}/{dirName}")
        for fileName in files:
            if fileName in deleteFiles:
                os.remove(f"{root}/{fileName}")
    print("Finish: Cleaning Project")


@task()
def install_backend():
    """Installs Backend Dependencies"""
    subprocess.run(
        args=["python3", "-m", "install", "--upgrade", "pip"], cwd=BACKEND_DIR
    )
    subprocess.run(args=["pip3", "install", "-r", "requirements.txt"], cwd=BACKEND_DIR)


@task()
def install_frontend():
    """Installs Frontend Dependencies"""
    subprocess.run(args=["npm", "install"], cwd=FRONTEND_DIR)


@task(install_backend, install_frontend)
def install_eveything():
    """Installs Dependencies for Backend + Frontend"""
    pass


@task()
def create_db_tables():
    """Builds the Django Backend for Testing"""
    print("Start: Building Backend")
    print(">>> Running Make Migrations")
    subprocess.run(
        args=["python3", "manage.py", "makemigrations", "api"], cwd=BACKEND_DIR
    )
    print(">>> Running Migrate")
    subprocess.run(args=["python3", "manage.py", "migrate"], cwd=BACKEND_DIR)
    print("Finish: Building Backend")


@task()
def reset_db():
    """Resets the Development Database with (Newer) Data + Models"""
    print("Start: Reset DB")
    print(">>> Deleting All Tables from Database")
    if os.path.exists(f"{BACKEND_DIR}/db.sqlite3"):
        os.remove(f"{BACKEND_DIR}/db.sqlite3")
    else:
        print(f"The file '{BACKEND_DIR}/db.sqlite3' does not yet exist.")

    print(">>> Deleting Migrations File to Ensure Updated Models")
    if os.path.isdir(f"{BACKEND_DIR}/api/migrations"):
        shutil.rmtree(f"{BACKEND_DIR}/api/migrations")
    else:
        print(f"The '{BACKEND_DIR}/api/migrations' directory does not yet exist.")
    print("Finish: Reset DB")


@task()
def add_data_to_db():
    """Creates Superuser and Adds Fixtures to DB"""
    print(">>> Uploading Fixtures to DB.")
    # the order below matters
    models = ["item", "store", "user", "association", "oauth_application", "oauth_accesstoken"]
    for model in models:
        subprocess.run(
            args=["python3", "manage.py", "loaddata", f"api/fixtures/{model}.json"],
            cwd=BACKEND_DIR,
        )
    print("Finish: Add Data to DB")


@task(install_backend, reset_db, create_db_tables, add_data_to_db)
def setup_backend():
    """Installs Dependencies, Resets DB, Recreates Tables, and Adds Data"""
    pass


@task(install_frontend)
def setup_frontend():
    """Installs Dependencies"""
    # [TODO] Add more frontend tasks if necessary
    pass


@task()
def test_backend():
    """Runs Backend Tests and Coverage via Tox"""
    subprocess.run(args=["coverage", "erase"], cwd=BACKEND_DIR)
    subprocess.run(args=["coverage", "run", "-m", "tox"], cwd=BACKEND_DIR)


@task()
def test_frontend():
    """Runs Frontend Tests and Coverage via Jest"""
    subprocess.run(
        args=["npm", "test", "--", "--watchAll=false", "--coverage"], cwd=FRONTEND_DIR
    )


@task()
def start_backend():
    """Runs Backend App"""
    subprocess.run(args=["python3", "manage.py", "runserver", "8000"], cwd=BACKEND_DIR)


@task()
def start_frontend():
    """Runs Frontend App"""
    subprocess.run(args=["npm", "start"], cwd=FRONTEND_DIR)


@task(setup_backend, setup_frontend)
def setup_everything():
    """Installs all Dependencies and Setups the Backend"""
    pass


@task(test_backend, test_frontend)
def test_everything():
    """Runs Tests on Backend + Frontend"""
    pass


__DEFAULT__ = start_backend
