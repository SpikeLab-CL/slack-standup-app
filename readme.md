### Google AppEngine Slack Standup Application

 **GAE Standup App** is a small application developed to help our team in the stand-up meetings. The bot send messages to the users in the workspace with questions defined by your team.

![Alt text](images/usage1.png?raw=false "Usage1")

Then post the results into **Slack** making them available for the rest of the team.

![Alt text](images/usage2.png?raw=false "Usage2")

#### Motivation

We were inspired by the work done by [Standup Alice](https://www.standupalice.com/). We wanted to create our version in which we could add more features and customize in the future, **this is a first version that we made in a few hours, so it's not perfect, but works pretty well**.

##### Requisites
This was made to work on [Google Cloud Platform](https://cloud.google.com/gcp/), but you can adapt the code to make it run in any server. The only limitation is that by default use [Datastore](https://cloud.google.com/datastore/docs/concepts/overview) to store the data, if you want you can modify `datastore.py` and make a connection to a MongoDB server or MySQL and adapt by your infrastructure.

#### Instalation
##### Set the bot in Slack
This is going to be a bit tricky, but with time and pacience the results are great.

First you need to create an **app** in [Slack](https://api.slack.com), and select the workspace in which your app is going to live, then you have to create a **Bot User**, and give the name that you want, ours is called `spike-bot`. ~~yes, the name is pretty boring~~

Now, we have to give the necesary permissions to our bot, go to the section **Basic Information** in your Slack App page and copy the `Verification Token` for your app. After that click on **Add features and functionality**, and go to the box **Permissions**, and here you need to copy the `Bot User OAuth Access Token`. In the same page in **Scopes** you need to add the following scopes:

1. channels:read
2. chat:write:bot
3. chat:write:user
4. im:read
5. im:write
6. bot
7. users:read

This is all the scopes that the bot needs.

##### Prepare and configure our bot

Now you have to clone this repo, you will find a file called `config_template.py`, rename it to just `config.py`, and you have to fill it with the neccesary information:

```
config = {
    "verification_token":"slack_verification_token",
    "oauth_bot_token":"xoxb--your-slack-bot-token",
    "channel":"agenda",
    "account_service":"path/to/your_account_service.json"
    "questions":[
        "Cómo estás? con qué estado de ánimo andas?",
        "En qué temas estuviste trabajando ayer (o en tu último día laboral)?",
        "Qué tienes pensado hacer hoy?",
        "Necesitas ayuda de alguien del equipo? (Indica quién y qué ayuda necesitas en particular)"
    ]
}
```
The `channel` is the name of the `channel` in which the bot is going to post the daily standup.
In  `account_service` you need to pass the path of the service account file from Google Cloud Platform, this is only necesary if you want to run the app locally.
In the `questions` section, you have to add the daily standup questions for your team.

In the repo, you will find a `cron.yaml` file, in this file you have to configure in which hour the bot is going to send a message to the users, which hour is going to post the daily standup in Slack, and other processes. Notice that we have weird hours because the timezone (UTC-3)

```
cron:
- description: Ask to each user what is going to do today
  url: /postDaily
  target: spikebot-standup
  schedule: every mon,tue,wed,thu,fri 12:00

- description: Post the daily standup message in slack
  url: /postDailyStandUp
  target: spikebot-standup
  schedule: every mon,tue,wed,thu,fri 14:00

- description: create every day entry
  url: /createDailyEntry
  target: spikebot-standup
  schedule: every mon,tue,wed,thu,fri 04:10

- description: update members from the workspace
  url: /addMembers
  target: spikebot-standup
  schedule: every mon,tue,wed,thu,fri,sat,sun 04:00

- description: warm the machine before the daily standup
  url: /warm
  target: spikebot-standup
  schedule: every mon,tue,wed,thu,fri 11:55
```
Now we have to install the neccesary libraries, first create a `virtualenv` typing:
```
virtualenv env --python=python3.7
source env/bin/activate
pip install -r requirements.txt
pip install -t lib -r requirements.txt
```
With all this ready, you just simply deploy it into AppEngine with the command:
```
gcloud app deploy app.yaml cron.yaml
```
Once is ready, copy the `url` that allows to access to your service, which should be something like `https://name-of-your-service-dot-name-of-the-gcp-project.appspot.com/`

#### Configure the Slack Events API.

Now, we have to go back to the Slack API page, go back to the section **Basic Information** in the section **Add features and functionality** click on **Event Subscriptions**, and add the `url` of your GAE service. If everything is ok, the `Request URL` should say `Verified`.
Then you have to subscribe your bot to the event `message.im`. If everythin is ok, all should like this:


![Alt text](images/usage3.png "Usage3")

The last thing we need to do is invite our bot to the channel defined in the `config.py`, to do that you just have to mention the bot in the channel, and follow the Slack instructions, **once you have that ready you have a new bot member in your team!**.