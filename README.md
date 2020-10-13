# slackbot-api

The TodoListAPI provides the following features to send messages to slack workplace

## Here is a description of all the endpoints in brief


### 1. /events
This endpoint is used to authenticate our endpoint with events API
``` returns the data it gets ```

### 2. /events/auth
This endpoint provides the user_token in exchange for code 
``` query_param: code ```

### 3. POST : /events/message
This endpoint is used to send message to a channel 
``` payload: message, channel, user_token, time(optional), accept(user/bot) ```

### 4. GET : /events/message
This endpoint returns all the scheduled messages 
``` payload: user_token ```

### 5. POST : events/deletemessage
This endpoint deletes the scheduled message and returns scheduled messages 
``` payload: user_token, id, channel_id```

### 6. GET : events/channels
This endpoint returns list of all channels 
``` payload: user_token```

### 7. POST : events/channels
This endpoint is used to make a new channel 
``` payload: user_token, name```
