## Usage

install requirements:

```pip install -r requirements.txt```

start redis server on standard port: `6379`

create `.env` file with enviroment variables:
```
MYSQL_HOST=
MYSQL_PORT=
MYSQL_USER=
MYSQL_PASSWORD=
MYSQL_DATABASE=
```

Scripts:

1. Cache database to redis:

```python -m scripts.collect_data```

2. Parse single title: (for testing)

```python -m scripts.run_single```

3. Parse and update database

```python -m scripts.update_data_tables```

