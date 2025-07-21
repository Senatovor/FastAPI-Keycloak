# Фреймворк на FastAPI для быстрого старта

## В комплекте идет:  
1. Готовая OAuth2, JWT, Bearer авторизация  
2. Логирование через loguru  
3. Докер  
4. Модуль для работы с базой данных  

## Алгоритм развертки:
1. Заполнить .env
2. Заполнить .env.keycloak файл (кроме: CLIENT_SECRET, REALM, CLIENT_ID, PUBLIC_KEY_KEYCLOAK)
3. ```docker-compose up -d```
4. ```docker-compose exec app_keycloak bash```
5. ```alembic revision --autogenerate -m "create  user"```
6. ```alembic upgrade head```
7. ```exit```
8. Переходите в контейнер keycloak, создаете новый realm и client
9. Заполняете до конца .env.keycloak  

P.S: CLIENT_SECRET, REALM, CLIENT_ID найдете в разделе вашего нового realm и client,  
PUBLIC_KEY_KEYCLOAK(он же PUBLIC_KEY) найдете в разделе realm settings -> keys -> rsa256 public key