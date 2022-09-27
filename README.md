<div align="center">
بسم الله الرحمن الرحيم
</div>

# Fasara

### Create `.env` files

- `cp .env.example .env`
- `cp api/app/.env.example api/app/.env`
- `cp ui/.env.example ui/.env`


### First start services

1. `docker-compose build`
2. `docker-compose up`

Then wait for the migration to complete (it will take ~15 minutes) and the services to start.


### Then check is all done correctly

1. Go to http://localhost:8080 and create first user. First user can be created with random invive.
Use python to generate first invite `python3 -c "import uuid; print(uuid.uuid4())"`
2. Create topic, and add response.


### Wrap services to tor

1. Press `CTRL+C` to stop running services.
2. Uncomment tor service in `docker-compose.yml`
3. For more safety comment ports (8080, 8000) for ui and api services.
4. Turn on production mode for ui service, comment and uncomment lines in `ui/Dockerfile`
5. Rebuild services `docker-compose down && docker-compose build && docker-compose up`
6. Wait until tor is establish connection and stop services `CTRL+C`
7. Add permissions for tor service `chmod 777 var/tor`
7. Uncomment parameters in tor.conf
8. Rebuild services `docker-compose start`


### Update `.env` for ui service

After previous action and tor launching you will see new files in the var/tor folder.
You need get generated domain names and put them to `ui/.env` file.

1. `cat var/tor/ui/hostname` and update `VUE_APP_UI_URL`
2. `cat var/tor/api/hostname` and update `VUE_APP_API_URL`
3. `docker-copmse restart`
