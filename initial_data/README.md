# Initial Data

Simple system for exporting and loading database fixtures.

## Export Data

Export all database data (except users, except admin):

```bash
python manage.py export_initial_data
```

This will:
- Export all tables from all apps
- Exclude all users except `admin@hishamos.com`
- Save fixtures to `initial_data/fixtures/`

## Load Data

Load all fixtures:

```bash
python manage.py load_initial_data
```

This will load all JSON files from `initial_data/fixtures/`.

## Manual Loading

You can also use Django's built-in command:

```bash
python manage.py loaddata initial_data/fixtures/*.json
```

## Notes

- All data is exported except users (admin user is included)
- Fixtures are saved as JSON files, one per app
- Empty fixtures are not created
