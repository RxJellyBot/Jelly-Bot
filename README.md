# Jelly Bot

I am a bot centralized around auto-reply with a lot of useful side features!

These side features include:

- Image uploading 

    - Simply send an image to the bot

- Sticker downloading

    - Utilize the command series `JC STK`
    
    - Check [here][stk-doc] for the documentation

- Activity tracking

    - Call `JC ID ME` in a channel where the bot exists
    
    - More info visible on the website

- Keyword notification ([awaiting implementation][JB-5])

### See [this page](https://github.com/RxJellyBot/Jelly-Bot/releases/latest) for the latest features list!

[JB-5]: http://jira.raenonx.cc/browse/JB-5

[stk-doc]: http://bot.raenonx.cc/doc/botcmd/stk/

Note that the frontend links may go invalid or redirect you to the other pages 
once the [new frontend][JB-3] has been done. 

[JB-3]: http://jira.raenonx.cc/browse/JB-3

----

#### GitHub Actions

[![Jelly Bot - CI Test](https://github.com/RxJellyBot/Jelly-Bot/workflows/Jelly%20Bot%20-%20CI%20Test/badge.svg)](https://github.com/RxJellyBot/Jelly-Bot/actions)

#### Master Branch - `master`

[![CodeFactor](https://www.codefactor.io/repository/github/raenonx/jelly-bot/badge/master)](https://www.codefactor.io/repository/github/raenonx/jelly-bot/overview/master)
[![Codacy](https://app.codacy.com/project/badge/Grade/ca77557007884126985561b06c5ec384?branch=master)](https://www.codacy.com/manual/RxJellyBot/Jelly-Bot)

#### Development Branch - `dev`

[![CodeFactor](https://www.codefactor.io/repository/github/raenonx/jelly-bot/badge/dev)](https://www.codefactor.io/repository/github/raenonx/jelly-bot/overview/dev)
[![Codacy](https://app.codacy.com/project/badge/Grade/ca77557007884126985561b06c5ec384?branch=dev)](https://www.codacy.com/manual/RxJellyBot/Jelly-Bot)

#### Coding timer since Aug. 24, 2020
[![Wakatime](https://wakatime.com/badge/github/RxJellyBot/Jelly-Bot.svg)](https://wakatime.com/badge/github/RxJellyBot/Jelly-Bot)

#### Coding activity in 30 days
[![Wakatime](https://wakatime.com/share/@RaenonX/dba9dda8-9ea7-40d3-98c1-be4ebfb8eb48.svg)](https://wakatime.com/badge/github/RxJellyBot/Jelly-Bot)

Supported on Discord and LINE. Feel free to add it to your group!

LINE Bot: http://rnnx.cc/Line

Discord Bot: http://rnnx.cc/Discord

Website: http://rnnx.cc/Website

----

### Links

Welcome to visit the [JIRA][JIRA-dash] of this bot!

List of the current known bugs can be found [here][JIRA-bugs].

[JIRA-dash]: http://jira.raenonx.cc/secure/Dashboard.jspa
[JIRA-bugs]: http://jira.raenonx.cc/browse/JB-107?jql=project%20%3D%20JB%20AND%20resolution%20%3D%20Unresolved%20AND%20issuetype%20%3D%20Bug

----

### Timeline

`May 17 2019` - Website Started.

`Sep 11 2019` - LINE/Discord bot started.

`Nov 27 2019` - Formal release. Only advertised in the developer-owned main active groups.

`Dec 30 2019` - Shutdown the stable build and merge the beta build to be the stable build.

- Because the user count of the stable build is significantly less than beta build.

### Miscellaneous information

#### Code quality checker

- `flake8`

- `pylint`

- `pydocstyle`

#### Docstring framework

`reStructuredText`

#### MongoDB Deployment

Clustered. Replica set enabled.

### Useful Links used in this repository

<details><summary>Documentations</summary>
<p>

- [reST syntax cheatsheet](https://thomas-cokelaer.info/tutorials/sphinx/rest_syntax.html)

- [reST syntax cheatsheet 2](https://docutils.sourceforge.io/docs/user/rst/quickref.html#section-structure)

- [MongoDB Standalone to Replica Set](https://docs.mongodb.com/manual/tutorial/convert-standalone-to-replica-set/)

</p>
</details> 

<details><summary>Online Tools</summary>
<p>

- [Json Schema Validator](https://www.jsonschemavalidator.net/)

- [`ObjectId` converter](https://steveridout.github.io/mongo-object-time/)

</p>
</details> 
