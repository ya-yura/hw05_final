# hw05_final

[![CI](https://github.com/yandex-praktikum/hw05_final/actions/workflows/python-app.yml/badge.svg?branch=master)](https://github.com/yandex-praktikum/hw05_final/actions/workflows/python-app.yml)


# Yatube Social Network



Blog engine. Allows you to write posts and publish them in individual groups, subscribe to posts, add and delete entries and comment on them.

Subscriptions to your favorite bloggers.



## Installation instructions.

***- Clone the repository:***

```

git clone git@github.com:ya-yura/hw05_final.git

```



***- Install and activate virtual environment:***

- for MacOS

```

python3 -m venv venv

```

- for Windows

```

python -m venv venv

source venv/bin/activate

source venv/Scripts/activate

```



***- Install the dependencies from the requirements.txt file:***

```

pip install -r requirements.txt

```



***- Apply the migrations:***

```

python manage.py migrate

```



***- In the folder with the file manage.py run the command:***

```

python manage.py runserver

```
