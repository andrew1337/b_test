## Running the project:

export the environment variable before start: 
```bash 
export OMDB_API_KEY=b5b62e9
```

start the backend:
```bash
gunicorn backend.gunicorn:application
```

run tests:
```bash
python test.py
```
