# DjangoBudget
Manage your budgets and expenses with Django

# What is DjangoBudget?
DjangoBudget is a budget planing and expense tracking web application around the famous [Django web framework](https://www.djangoproject.com/) .

# Features
* Manage multiple budgets
* Manage your budget via individual accounts
* Group your expenses by custom categories
* Create accounts with read and or write permissions per budget

# How to

## Use with virtual environment (dev mode)
```shell
git clone https://github.com/h3nr1-g/djangobudget.git
cd djangobudget
virtualenv -p$(which pyhton3) venv && source venv/bin/activate
pip install -r dev_requirements.txt
python3 manage.py makemigrations budgets users common
python3 manage.py migrate
python3 manage.py createsuperuser
for file in $(ls common/res/lang); do
    python manage.py loadlang common/res/lang/$file
done
python3 manage.py loaddata budgets/res/sample.json
python3 manage.py runserver
```

## Use with docker
```shell
git clone https://github.com/h3nr1-g/djangobudget.git
cd djangobudget
docker-compose build
docker-compose up
```

## Customize configuration parameters for docker deployment
```shell
vim configuration.env 
```

## Add translations
1. Copy existing language file
```shell
cp common/res/lang/en-us.csv common/res/lang/mylang.csv
```

2. Replace the value of the second column with the ISO country code of the required language
```shell
sed "s|;en-us;|;de;|g" common/res/lang/mylang.csv
```

3. Open the copied file in a text editor and translate each item/line
4. Run manage.py to load new language
```shell
python3 manage.py loadlang common/res/lang/mylang.csv
```

5. Set the language code in djangobudget/settings/common.py or export environment variable DJANGOBUDGET_LANG with the ISO country code of the required language
```shell
export DJANGOBUDGET_LANG=de
```

6. Start application
```shell
python3 manage.py runserver
```

### Note
For docker deployments a rebuild of the application image is necessary. All CSV files in common/res/lang will be loaded automatically.