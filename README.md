# Demostore

### Описание

Backend для бота-магазина в telegram. Реализована админка и API на djangorestframework

Проект пока еще сырой и находится в стадии разработки. Демо магазина - @demostoretelegrambot

Для связи с разработчиком в телеграм - [@paracosm17](https://t.me/paracosm17)

### Возможности API

##### GET

| Адрес                    | Ответ                                                              |
| ----------------------------- | ----------------------------------------------------------------------- |
| /api/categories/              | Все категории                                               |
| /api/users/                   | Все юзеры                                                       |
| /api/users/?user_id=          | Юзер по его *telegram id*                                    |
| /api/products/                | Все товары, количество которых больше 0 |
| /api/products/?id=            | Товар по id                                                      |
| /api/products/?all=           | Все товары                                                     |
| /api/products/?category=      | Все товары по id категории                          |
| /api/products/?category=&all= | См. 2 предыдущих                                            |
| /api/purchases/               | Все покупки                                                   |
| /api/purchases/?user_id=      | Все покупки юзера по его*telegram id*             |
| /api/purchases/?product_id=   | Все покупки по id товара                              |
| /api/purchases/?category_id=  | Все покупки по id категории                        |

##### POST

| Адрес              | Data                                                                                       |
| ----------------------- | ------------------------------------------------------------------------------------------ |
| /api/categories/create/ | По модели                                                                          |
| /api/users/create/      | По модели                                                                          |
| /api/products/create/   | По модели. Для указания категории {"category": {"name": name}} |
| /api/purchases/create/  | По модели. Для указания покупателя {"buyer": telegram id}     |

##### Update

| Адрес        | Data                                                                                                                                                                                                 |
| ----------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| api/users/update/ | phone, email - номер телефона, почта<br />increase_bal - на сколько увеличить баланс юзера<br />decrease_bal - на сколько уменьшить |