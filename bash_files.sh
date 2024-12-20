echo "Install Dependencies"

pip install -r requirements.txt

echo "Collect all static files" 

python3.12 manage.py collectstatic