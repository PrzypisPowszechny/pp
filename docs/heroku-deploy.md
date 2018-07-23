## BASIC

#### Heroku CLI and GIT setup 

Install heroku-cli from  
`https://devcenter.heroku.com/articles/heroku-cli`

Authenticate  
`$ heroku login`

Add git remote by appending it to ./.git/config  
```
[remote "heroku"]
    url = https://git.heroku.com/damp-headland-12387.git
    fetch = +refs/heads/*:refs/remotes/heroku/*
```

#### Deployment environment vars

Current heroku deployment assumes below var to exist:  
`DJANGO_SETTINGS_MODULE=settings.prod_heroku`

And additionally database configuration exposed using url format as var:  
`DATABASE_URL=`

Django's secret key, used for security-related issues like cryptography:     
`PP_SECRET_KEY=`


#### Deploying

Push changes to heroku from you local prod-heroku branch to master on heroku  
`$ git push heroku prod-heroku:master`

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