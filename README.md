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

<img width="600" alt="Screenshot 2024-11-18 at 17 18 12" src="https://github.com/user-attachments/assets/78a2234b-8c43-436f-91f9-69c79f420217">


You also need to remember the token you generated, and this will be your `SLACK_APP_TOKEN`.

After this step, you need to ensure that the bot is connecting through **Socket Mode** and also enable these features under Socket Mode.

<img width="600" alt="Screenshot 2024-11-18 at 17 21 25" src="https://github.com/user-attachments/assets/56cac955-91ed-412d-b678-e9ab92b7ab5d">


After completing these steps, you can proceed to install the application. Remember to store your OAuth Token as this should be the `SLACK_BOT_TOKEN` that you will need later.
<img width="600" alt="Screenshot 2024-11-18 at 17 22 19" src="https://github.com/user-attachments/assets/b6acb51a-8bcf-4005-9f78-c431b2af5b36">


Go to `OAuth & Permissions` and make sure you have all these permissions enabled.
<img width="850" alt="Screenshot 2024-11-18 at 17 24 46" src="https://github.com/user-attachments/assets/449c9a15-f9e7-413e-abfe-6cdb49ed336e">


Also, you need to enable `Event Subscriptions` right after the OAuth section.

Finally, go to `Slash Commands`, and create all these commands shown in the picture.
<img width="600" alt="Screenshot 2024-11-18 at 17 27 04" src="https://github.com/user-attachments/assets/b5e697b4-5cf8-48ba-9383-5078b5e8ebfd">


After completing all the procedures mentioned above, you need to install the `requirements.txt` and run `bot.py` in an appropriate environment.

##### Troubleshooting

- Try reinstalling the slack app in the slack app webpage
  
- Use `/test` command to check whether you can properly interact with the bot
  
- Add the bot to the correct channel and ensure that all your names are consistent
  
- There might be new updates or changes that render this whole application obsolete.
