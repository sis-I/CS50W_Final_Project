echo "Install Dependencies"

pip install -r requirements.txt


echo "Model migrations into database"

python3.12 manage.py makemigrations
python3.12 manage.py migrate


echo "Collect all static files" 

python3.12 manage.py collectstatic