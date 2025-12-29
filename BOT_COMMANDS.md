# Telegram Bot Commands

Control your TikTok Live Monitor directly from Telegram!

## Available Commands

### `/start`
Show welcome message and list of available commands

### `/add @username` or `/add username`
Add a TikTok user to monitoring list

**Examples:**
```
/add charlidamelio
/add @khaby.lame
```

### `/remove @username` or `/remove username`
Remove a TikTok user from monitoring list

**Examples:**
```
/remove charlidamelio
/remove @khaby.lame
```

### `/list`
Show all TikTok users currently being monitored

### `/status`
Show current monitoring status:
- Whether monitoring is running or paused
- Total number of users being monitored
- Active recordings (users currently live)

### `/pause`
Temporarily pause monitoring (stops checking for new streams)
- Active recordings will continue
- No new streams will be detected until resumed

### `/resume`
Resume monitoring after pausing

### `/help`
Show list of available commands

## Usage Examples

### Adding Multiple Users
```
/add user1
/add user2
/add user3
```

### Checking What's Being Monitored
```
/list
```
Response:
```
📋 Monitored Users (3):

• @user1
• @user2
• @user3
```

### Checking Status
```
/status
```
Response:
```
📊 Monitoring Status

Status: ▶️ Running
Total users: 3
Active recordings: 1

Currently recording:
🔴 @user1
```

### Temporarily Pausing
```
/pause
```
Later:
```
/resume
```

## Features

✅ **Real-time Updates**: Changes take effect immediately
✅ **Persistent Storage**: Monitoring list saved to file
✅ **No Restart Needed**: Add/remove users without restarting the bot
✅ **Safe**: Only authorized users can control (configure in bot settings)

## Security Note

By default, anyone who can message your bot can control it. To restrict access:

1. Talk to [@BotFather](https://t.me/botfather)
2. Send `/setjoingroups`
3. Choose your bot
4. Select `Disable`

This prevents others from adding your bot to their groups.

For additional security, you can modify `monitor_bot.py` to check user IDs before executing commands.
