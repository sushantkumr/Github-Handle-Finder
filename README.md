# Github-Handle-Finder
A webapp to search for GitHub handles. Authenticated using GitHub OAuth

## Steps to deploy
1. Clone the repository in your local machine and step into the root directory by running `cd Github-Handle-Finder`
2. Install `virtualenv` in your machine to create a Virtual Environment for this project by following instructions from [here](https://virtualenv.pypa.io/en/stable/installation/)
3. Create a virtual environment by running the following command `virtualenv -p python3 venv`
4. Activate the virtual env by running `source venv/bin/activate`
5. Install the dependencies by executing `pip install -r requirements.txt` at the root level of the repo.
6. Initialize the database by executing `python lib/devops/init_db.py`
7. Run the server by executing `python app.py` at the root level of the repo.
8. Access the application at this URL: [http://0.0.0.0:5000](http://0.0.0.0:5000)

### Tech Stack
- Python 3.6
- Flask
- SQLAlchemy
- Bootstrap 4
- jQuery
