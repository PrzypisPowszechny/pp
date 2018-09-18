### Start the env

Install docker compose

`$ sudo apt install docker-compose`

Then start it all (it's almost done!)

`$ sudo docker-compose up`

Once previous step is complete, you just need to run the migrations

`$ sudo docker-compose run web python manage.py migrate`

Done!

### Daily operations

If you need to install anything, it is the same way as migrations 

`$ sudo docker-compose run web python manage.py migrate`

`$ sudo docker-compose run web pip install ...`

### Resources

Docker compose tutorial: https://docs.docker.com/compose/gettingstarted/

File docker-compose reference: https://docs.docker.com/compose/compose-file/

Dockerfile reference: https://docs.docker.com/engine/reference/builder


