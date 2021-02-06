# django_be


## Some prerequisites:
Docker should be installed in the system

### Steps to run:

1. Clone git repository - git clone https://github.com/yuvraj2112/django_be.git
2. python3 -m venv env
3. source env/bin/activate
4. docker run --rm --name redis -p 6379:6379 -d redis
5. docker run --name postgres -e POSTGRES_PASSWORD=passowrd -d postgres
6. Go to your postgres installation and create a new db called 'dukaan'
7. cd django_be
8. pip install -r requirements.txt
9. python manage.py makemigrations seller
10. python manage.py makemigrations buyer
11. python manage.py migrate
12. python manage.py runserver
13. Now you may go ahead and use the 'Postman API collection' or start making API calls as you see fit!