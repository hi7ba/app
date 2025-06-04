git clone https://github.com/hi7ba/app.git
cd app
#Create and activate a virtual environment
python -m venv env
venv\Scripts\activate
pip install -r requirements.txt
python manage.py runserver
