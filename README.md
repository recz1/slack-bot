# slack-bot

##### Before the start

Firstly, you need to create `.env` file and store all these variables within it.

```textile
OPENAI_KEY=
SLACK_BOT_TOKEN=
SLACK_APP_TOKEN=
YOUTUBE_DEV_KEY=
GOOGLE_SEARCH_CX=
```

For `OPENAI_KEY`, you can obtain it from https://openai.com/index/openai-api/ and the YouTube and Google dev keys you can get them on **Google Developer Console** by creating a Google Developer account.

Slack APP and BOT tokens are a bit tricky here, and they require multiple setups, including the configuration of the slack application.

Go to https://api.slack.com/apps/ and make your own application. You can name the application whatever you want.

##### Setting up the Slack bot

Firstly, you need to generate a token and give the token proper scope that allows the application to function well. For this program, you need to enable the following scopes.

![Screenshot 20241118 at 171812png]((https://github.com/recz1/slack-bot/blob/main/readme/Screenshot%202024-11-18%20at%2017.18.12.png))

You also need to remember the token you generated, and this will be your `SLACK_APP_TOKEN`.

After this step, you need to ensure that the bot is connecting through **Socket Mode** and also enable these features under Socket Mode.

![Screenshot 20241118 at 172125png](file://readme/Screenshot%202024-11-18%20at%2017.21.25.png?msec=1731921700532)

After completing these steps, you can proceed to install the application. Remember to store your OAuth Token as this should be the `SLACK_BOT_TOKEN` that you will need later.

![Screenshot 20241118 at 172219png](file://readme/Screenshot%202024-11-18%20at%2017.22.19.png?msec=1731921804922)

Go to `OAuth & Permissions` and make sure you have all these permissions enabled.

![Screenshot 20241118 at 172446png](file://readme/Screenshot%202024-11-18%20at%2017.24.46.png?msec=1731921903158)

Also, you need to enable `Event Subscriptions` right after the OAuth section.

Finally, go to `Slash Commands`, and create all these commands shown in the picture.

![Screenshot 20241118 at 172704png](file://readme/Screenshot%202024-11-18%20at%2017.27.04.png?msec=1731922040544)

After completing all the procedures mentioned above, you need to install the `requirements.txt` and run `bot.py` in an appropriate environment.

##### Troubleshooting

- Try reinstalling the slack app in the slack app webpage
  
- Use `/test` command to check whether you can properly interact with the bot
  
- Add the bot to the correct channel and ensure that all your names are consistent
  
- There might be new updates or changes that render this whole application obsolete.
