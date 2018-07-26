## BASIC

#### Heroku CLI and GIT setup 

Install heroku-cli from  
`https://devcenter.heroku.com/articles/heroku-cli`

Authenticate  
`$ heroku login`

Add git remote by appending it to ./.git/config  
```
[remote "heroku-prod"]
    url = https://git.heroku.com/pp-prod.git
    fetch = +refs/heads/*:refs/remotes/heroku-prod/*
[remote "heroku-dev1"]
    url = https://git.heroku.com/pp-dev1.git
    fetch = +refs/heads/*:refs/remotes/heroku-dev1/*
```

#### Deployment environment vars

Current heroku deployment assumes below var to exist:  
`DJANGO_SETTINGS_MODULE=settings.[prod|dev]_heroku`

And additionally database configuration exposed using url format as var (heroku automatically sets this var and rotes it periodically for the sake of safety):  
`DATABASE_URL=`

Django's secret key, used for security-related issues like cryptography:     
`PP_SECRET_KEY=`


#### Deploying

Push changes to heroku from you local prod-heroku branch to master on heroku  
`$ git push heroku-[prod|dev1] my-local-branch:master`

Migrate database if necessary  
`$ heroku run python manage.py migrate`



## Advanced

##### Moving/coping particular deployment 

Heroku plugin is required:  
`heroku plugins:install heroku-fork` 


Move/copy deployment with all add-ons (eg. databases) and settings (excluding domains)  
`$ heroku fork --from pp-deploy --to pp-deploy-copy1`


Use `--region` arg to move between data centers  
`$ heroku fork --from pp-deploy --to pp-deploy-copy1 --region eu`