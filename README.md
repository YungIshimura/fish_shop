# Fish Shop
Бот, взаимодействующий с [ElacticPath](https://www.elasticpath.com/). 

## Функции бота
Бот позволяет:
* Просматривать каталог товаров;
* Просматреть каждый отедельный товар с его описанием;
* Выбирать количество товара;
* Заказать товар.

## Как установить?
Во-первых, вам необходимо скачать этот репозиторий. Для этого нажмите зелёную кнопку Code в правом верхнем углу и выберите удобный для вас метод скачивания.![4](https://user-images.githubusercontent.com/83189636/210057712-e566c5ce-629c-4764-b4a6-8718d89bdf48.gif)

Во-вторых, создайте .env файл в папке проекта, в него нужно записать следующее:

**ELASTICPATH_CLIENT_ID**.  Необходимо запросить доступ [ на сайт ElacticPath](https://www.elasticpath.com/). Доступ можно запросить только у пользователя, у которого уже есть аккаунт.
Далее по гайду из документации необходимо создать каталог товаров. После, в личном кабинете, нужно взять ваш *CLIENT_ID*. Запишите его в ```.env``` файл.
```python
ELASTICPATH_CLIENT_ID = 'CLIENT_ID'
```

**TG_BOT_API_KEY**. Далее необходимо создать телеграм бота в [BotFather](https://telegram.me/BotFather) и получать API-ключ бота. Для этого папаше ботов нужно прописать команду ```/newbot ``` и придумать боту название и логин, заканчивающийся на bot. Записать его в ```.env``` аналогичным образом.
```python
TG_BOT_API_KEY = 'Ваш API-ключ'
```

В проекте используется [Redis](https://redis.com/). Вам необходимо перейти на сайт, зарегистрироваться и создать новую базу данных (если вы делаете это из РФ, то включите ВПН). После вам нужно ввести:
**REDIS_DB_HOST**. Хост находится в разделе ```Public endpoint``` (Всё, что до двоеточия). Запишите его в ```.env``` файл.
```python
REDIS_DB_HOST = 'Хост БД'
```
**REDIS_DB_PORT**. Хост находится в разделе ```Public endpoint``` (Всё, что после двоеточия). Запишите его в ```.env``` файл.
```python
REDIS_DB_PORT = 'Порт БД'
```
**REDIS_DB_PASSWORD**. Пароль находится в разделе ```Security/default_user_password```. Запишите его в ```.env``` файл.
```python
REDIS_DB_PASSWORD = 'Пароль от БД'
```

В проекте используется пакет [environs](https://pypi.org/project/environs/). Он позволяет загружать переменные окружения из файла ```.env``` в корневом каталоге приложения.
Этот ```.env``` файл можно использовать для всех переменных конфигурации.
Ну и естественно Python3 должен быть уже установлен. Затем используйте pip (или pip3,если есть конфликт с Python2) для установки зависимостей:
```python
pip install -r requirements.txt
```

## Как пользоваться 

Достаточно просто запустить необходимый скрипт при помощи команд:

**Telegram**
```bash 
python3 tg_bot.py
```
и запустить бота, отправив ему команду ```/start``` или нажать на кнопку ```start``` при первом запуске.