Доска в miro
============
https://miro.com/app/board/uXjVPR-C8OQ=/?share_link_id=195409214334

События
=======
![image](https://user-images.githubusercontent.com/935751/193419696-04dd6c83-5bdc-4702-bf43-abc9ee1a843b.png)

Модель данных
=============
![data model](https://user-images.githubusercontent.com/935751/193419704-b206cb0b-9e01-4932-bca1-c7dd428e07cd.jpg)

CUD-события
===========

1. Создание пользователя (`UserCreated`)
3. Создание задачи (`TaskCreated`)

Для `UserCreated` producer'ом является `auth`, для `TaskCreated` - `task tracker`. 
Консьюмерами `UserCreated` являются все сервисы, `TaskCreated` - все, кроме `auth`.

