@echo off
chcp 65001
set PYTHONIOENCODING=utf-8
set PGCLIENTENCODING=UTF8
set LC_ALL=en_US.UTF-8
set LANG=en_US.UTF-8

echo Encodage configure pour UTF-8
echo Lancement de Django avec PostgreSQL...

.venv\Scripts\activate && python manage.py runserver
