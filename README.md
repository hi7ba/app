git clone https://github.com/hi7ba/app.git
cd app
#Create and activate a virtual environment
python -m venv env
env\Scripts\activate
 pip install -U django-jazzmin
 pip install fpdf
python manage.py runserver
