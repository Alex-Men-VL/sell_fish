# Телеграм бот для продажи морепродуктов

Бот позволяет автоматизировать процесс продажи морепродуктов. В боте интегрирована API
[Elasticpath](https://euwest.cm.elasticpath.com/).

Есть возможность просмотреть список морепродуктов с их описанием, ценой и доступным количеством на складе.
Можно добавлять товар в корзину, удалять из корзины и оплачивать (запрос email с занесением в базу).

[Пример рабочего бота](https://t.me/ALMenTestBot).

## Как запустить

- Скачайте код:
```shell
    $ git clone https://github.com/Alex-Men-VL/sell_fish.git
    $ cd sell_fish
```
- Установите зависимости:
```shell
$ pip install -r requirements.txt
```
- Запустите бота:
```shell
$ python3 tg_bot.py
```

## Переменные окружения

Часть данных берется из переменных окружения. Чтобы их определить, создайте файл `.env` в корне проекта и запишите 
туда данные в таком формате: `ПЕРЕМЕННАЯ=значение`

Доступно 5 обязательных переменных:

- `TG_BOT_TOKEN` - токен телеграм бота;
  - Чтобы его получить, напишите в Telegram специальному боту: [BotFather](https://telegram.me/BotFather)
- `TG_DEV_CHAT_ID` - id пользователя в телеграм, кому будут приходить сообщения с ошибками;
- `TELEGRAM_DEV_BOT_TOKEN` - токен телеграм бота, который будет присылать сообщения с логами пользователю, 
id которого указан в переменной `TG_DEV_CHAT_ID`.
- Настройки для [ElasticPath](https://euwest.cm.elasticpath.com/):
  - `CLIENT_ID` - id клиента [ElasticPath](https://euwest.cm.elasticpath.com/)
  - `CLIENT_SECRET` - секретный ключ клиента [ElasticPath](https://euwest.cm.elasticpath.com/)

## Пример работы бота

![tg](.github/tg.gif)

## Цель проекта

Код написан в образовательных целях на онлайн-курсе для веб-разработчиков [dvmn.org](https://dvmn.org/)
