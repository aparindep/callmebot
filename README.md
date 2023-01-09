# callmebot
Send emails periodically with Call Me Bot!

## How to use

1. Clone the repository:

```
git clone git@github.com:aparinelli/callmebot.git
```

2. Go into the repo directory and create an environment file named `.env`:

```
DATABASE_URL='postgresql://callmebot:callmebot@db/callmebot'
SECRET_KEY='yoursecretkey'
MAIL_USERNAME= 'youremail'
MAIL_PASSWORD= 'yourpassword'
```

3. Set an APP_ENV variable to `development` or `production`:

```
export APP_ENV=development
```

4. Spin up the docker containers with docker-compose (which you can get by installing Docker Desktop).

```
docker-compose up -d --build
```

To see logs, execute:

```
docker-compose logs -f
```

To stop the containers, execute:

```
docker-compose down
```

5. Go to http://localhost:5010 to use the website!

## Testing

1. Set `APP_ENV` to `testing` and spin up the containers with docker-compose.
   
2. List containers that are running:

```
docker container list
```

3. Look for the web container, named `callmebot_web`. Copy its container ID to your clipboard.

4. Run `test_client.py` inside the web container:

```
docker exec -it containerid python3 test_client.py
```