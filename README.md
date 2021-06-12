# Quick Sales

## Instrucciones de instalacion

1. Instalar liberias:
   
    `pip install -Ur requirements.txt`


2. Configuracion BD: En el archivo `salesproject/settings.py` 
modificar la configuracion de conexion con la base de datos
   
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': '[DATABASE_NAME]',
        'USER': '[USER_DATABASE]',
        'PASSWORD': '[PASSWORD]',
        'HOST': '[HOST]',
        'PORT': '[PORT]',
    }
}
```
3. Correr migraciones:
   
    `python manage.gy migrate`
   

4. Ejecutar la aplicacion:
    
    `python manage.py runserver`
    
    La aplicacion correrá en http://127.0.0.1:8000/


    
    
