# ГДПБЗН - Оперативен център за управление на произшествия

Система за управление на инциденти на Главна дирекция "Пожарна безопасност и защита на населението". Уеб базиран оперативен център с API и PWA поддръжка за мобилни устройства.

## Архитектура

```
                    +-----------------+
                    |   Браузър/PWA   |
                    +--------+--------+
                             |
                    HTTP / WebSocket
                             |
              +--------------+--------------+
              |              |              |
         Flask REST     Socket.IO      Статични
         API (JWT)      Push/чат       файлове
              |              |              |
              +-------+------+--------------+
                      |
              +--------+--------+
              |                  |
         SQLite/PostgreSQL    Redis (опц.)
              |                  |
         SQLAlchemy         Канал за
          модели           съобщения
```

## Бърз старт

```bash
# 1. Инсталирайте зависимости
pip install -r requirements.txt

# 2. Инициализирайте базата данни със примерни данни
python seed.py

# 3. Стартирайте сървъра
python start_server.py
```

Сървърът работи на **http://localhost:5000**

## Вход

| Акаунт          | Имейл                        | Парола    | Роля         |
|-----------------|------------------------------|-----------|--------------|
| Администратор   | admin@gdpbzn.bg              | admin123  | admin        |
| Диспечер        | dispatcher@gdpbzn.bg         | admin123  | dispatcher   |
| Командир        | commander@gdpbzn.bg          | admin123  | commander    |
| Пожарникар 1    | firefighter1@gdpbzn.bg       | ff123     | firefighter  |
| Пожарникар 2    | firefighter2@gdpbzn.bg       | ff123     | firefighter  |
| ...             | firefighter3-15@gdpbzn.bg   | ff123     | firefighter  |

## API Endpoints

Всички защитени endpoints изискват хедър: `Authorization: Bearer <token>`

### Auth
| Метод | Път                    | Описание              |
|-------|------------------------|-----------------------|
| POST  | /api/auth/login        | Вход                  |
| POST  | /api/auth/register     | Регистрация           |
| GET   | /api/auth/me           | Профил                |

### Произшествия
| Метод | Път                            | Описание                       |
|-------|--------------------------------|--------------------------------|
| GET   | /api/incidents                 | Списък произшествия            |
| POST  | /api/incidents                 | Създаване                      |
| GET   | /api/incidents/stats           | Статистики                     |
| GET   | /api/incidents/types           | Типове произшествия            |
| PUT   | /api/incidents/{id}            | Обновяване                     |
| POST  | /api/incidents/{id}/photos     | Качване на снимка              |
| POST  | /api/incidents/{id}/sos        | SOS сигнал                     |

### Екипи и автопарк
| Метод | Път                              | Описание                 |
|-------|----------------------------------|--------------------------|
| GET   | /api/teams                       | Списък екипи             |
| GET   | /api/teams/fleet                 | Автопарк                 |
| PUT   | /api/teams/fleet/{id}            | Обновяване автомобил     |
| POST  | /api/teams/fleet/{id}/photo      | Качване снимка на авто   |

### Задачи
| Метод | Път                              | Описание                 |
|-------|----------------------------------|--------------------------|
| POST  | /api/tasks                       | Създаване                |
| GET   | /api/tasks/incident/{id}         | Задачи за произшествие   |
| PUT   | /api/tasks/{id}                  | Обновяване               |
| GET   | /api/tasks/my                    | Моите задачи             |

### Карта
| Метод | Път                              | Описание                 |
|-------|----------------------------------|--------------------------|
| GET   | /api/map/markers/all             | Всички маркери           |
| POST  | /api/map/{incident_id}/markers   | Добавяне маркер          |

### Чат
| Метод | Път                              | Описание                 |
|-------|----------------------------------|--------------------------|
| GET   | /api/chat/channels               | Канали                   |
| POST  | /api/chat/ai-chat                | AI асистент (Gemini)     |

## PWA (мобилно приложение)

Отворете http://localhost:5000 от телефон и използвайте:
- **Android**: Chrome → меню → "Add to Home screen"
- **iOS**: Safari → Share → "Add to Home Screen"

След инсталиране работи като самостоятелно приложение с офлайн кеш.

## Конфигурация

### Google Maps API ключ
1. Отидете на https://console.cloud.google.com/apis/credentials
2. Създайте API ключ за "Maps JavaScript API"
3. В dashboard-а, секция "Карта" → бутон "⚙️" → въведете ключа

### Gemini AI ключ
- Безплатен ключ от https://aistudio.google.com/apikey
- Задайте като променлива на средата: `GEMINI_API_KEY=<вашият ключ>`
- Или сменете директно в `config.py`

## Структура на проекта

```
gdpbzn-system/
├── app/
│   ├── __init__.py          # Flask app factory
│   ├── auth_middleware.py   # JWT декоратор
│   ├── models/              # SQLAlchemy модели
│   │   ├── user.py
│   │   ├── incident.py
│   │   ├── team.py
│   │   ├── task.py
│   │   ├── map_marker.py
│   │   ├── chat.py
│   │   └── ...
│   ├── routes/              # REST API маршрути
│   │   ├── auth.py
│   │   ├── incidents.py
│   │   ├── teams.py
│   │   ├── tasks.py
│   │   ├── map.py
│   │   ├── chat.py
│   │   └── ...
│   ├── services/            # Бизнес логика
│   │   ├── ai_provider.py
│   │   ├── ai_chat_service.py
│   │   ├── notification_service.py
│   │   └── navigation_service.py
│   ├── websocket.py         # Socket.IO handlers
│   ├── static/
│   │   ├── uploads/         # Качени снимки
│   │   └── icon.svg         # PWA икона
│   └── templates/
│       └── index.html       # SPA dashboard
├── config.py                # Конфигурация
├── seed.py                  # Начални данни
├── start_server.py          # Стартиране
├── add_workers.py           # Добавяне на пожарникари
├── add_fleet.py             # Добавяне на автомобили
├── requirements.txt
└── README.md
```

## Разработка

### Добавяне на нови пожарникари
```bash
python add_workers.py
```

### Добавяне на нови автомобили
```bash
python add_fleet.py
```

### Изисквания
- Python 3.10+
- SQLite (вграден) или PostgreSQL
- Redis (опционално, за Socket.IO мащабиране)
