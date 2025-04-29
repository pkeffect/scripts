# 📊 Player Tracker Suite 📊

## 🌟 Overview

Player Tracker Suite is a comprehensive Oxide plugin for tracking and managing player data on your game server. It combines several tracking features into one unified plugin, allowing server administrators to monitor player activities, reward active players, and manage referrals.

## ✨ Features

- **📝 IP Address Tracking**: Log and query player IP addresses with configurable history limits
- **👤 Name Tracking**: Track name changes of players with configurable history limits
- **⏰ Time Tracking**: Record first connection and last seen times
- **🗺️ Position Tracking**: Save players' last positions on disconnect
- **⌛ Playtime Tracking**: Monitor active and AFK time separately
- **🏆 Playtime Rewards**: Automatically reward players based on active playtime
- **👥 Referral System**: Allow players to refer others and receive rewards
- **💰 Reward Integration**: Compatible with Economics and ServerRewards plugins

## 📋 Configuration

The configuration system is comprehensive and divided into logical sections:

### 🛠️ IP Address Tracking
```json
"IP Address Tracking": {
  "Enabled": true,
  "Max IP Logs Per Player": 10,
  "Permission To View (/lastips, /ipowners)": "playertrackersuite.ips.view",
  "Required Auth Level (View - Rust Only)": 1
}
```

### 👤 Player Name Tracking
```json
"Player Name Tracking": {
  "Enabled": true,
  "Max Name Logs Per Player": 10,
  "Permission To View (/lastnames)": "playertrackersuite.names.view",
  "Required Auth Level (View - Rust Only)": 1
}
```

### ⏰ Connection Time Tracking
```json
"Connection Time Tracking": {
  "Log First Connection Time": true,
  "Permission To View (/firstconnection)": "playertrackersuite.firstseen.view",
  "Required Auth Level (FirstSeen - Rust Only)": 1,
  "Log Last Seen Time": true,
  "Permission To View (/lastseen)": "playertrackersuite.lastseen.view",
  "Required Auth Level (LastSeen - Rust Only)": 1
}
```

### 🗺️ Position Tracking
```json
"Position Tracking": {
  "Log Last Position On Disconnect": true,
  "Permission To View (/lastposition)": "playertrackersuite.lastpos.view",
  "Required Auth Level (View - Rust Only)": 1
}
```

### ⌛ Playtime and AFK Tracking
```json
"Playtime and AFK Tracking": {
  "Enabled": true,
  "Track AFK Time Separately": true,
  "AFK Check Interval (Seconds)": 60.0,
  "Permission To View Own Playtime (/playtime)": "",
  "Permission To View Others Playtime (/playtime <name/id>)": "playertrackersuite.playtime.viewothers",
  "Permission To View Top Playtime (/playtime top)": "playertrackersuite.playtime.viewtop",
  "Required Auth Level (View Others/Top - Rust Only)": 0,
  "Number of entries in Top Playtime list": 10,
  "Top List Update Interval (Seconds)": 300.0
}
```

### 💰 Reward System Integration
```json
"Reward System Integration": {
  "Reward Plugin Name (Requires 'ServerRewards' or 'Economics')": "Economics",
  "Custom Reward Multipliers (Permission: Multiplier)": {
    "playertrackersuite.vip1": 1.5,
    "playertrackersuite.vip2": 2.0
  }
}
```

### 🏆 Playtime Rewards
```json
"Playtime Rewards": {
  "Enabled": true,
  "Reward Interval (Seconds of Active Playtime)": 3600,
  "Reward Amount": 5.0,
  "Permission Required To Receive Rewards (Optional, leave empty if none)": ""
}
```

### 👥 Referral System
```json
"Referral System": {
  "Enabled": true,
  "Reward Referrer On Successful Referral": true,
  "Referrer Reward Amount": 5.0,
  "Reward Referee On Successful Referral": true,
  "Referee Reward Amount": 3.0,
  "Permission Required To Use /refer Command (Optional, leave empty if none)": ""
}
```

## 🔑 Permissions

- `playertrackersuite.ips.view` - Access to IP tracking commands
- `playertrackersuite.names.view` - Access to name tracking commands
- `playertrackersuite.firstseen.view` - Access to first connection time command
- `playertrackersuite.lastseen.view` - Access to last seen time command
- `playertrackersuite.lastpos.view` - Access to last position command
- `playertrackersuite.playtime.viewothers` - Ability to view other players' playtime
- `playertrackersuite.playtime.viewtop` - Ability to view top playtime list
- `playertrackersuite.vip1` - 1.5x reward multiplier (customizable)
- `playertrackersuite.vip2` - 2.0x reward multiplier (customizable)

## 💬 Commands

### 🔍 IP Tracking
- `/lastips <steamid|name>` - Shows last IPs used by a player
- `/ipowners <IP.Address>` - Shows players who used a specific IP

### 👤 Name Tracking
- `/lastnames <steamid|name>` - Shows last names used by a player

### ⏰ Time Tracking
- `/firstconnection <steamid|name>` - Shows when a player first connected
- `/lastseen <steamid|name>` - Shows when a player was last online

### 🗺️ Position Tracking
- `/lastposition <steamid|name>` - Shows the last known position of a player

### ⌛ Playtime Tracking
- `/playtime` - Shows your playtime statistics
- `/playtime <name|id>` - Shows playtime for another player
- `/playtime top` - Shows the top players by playtime

### 👥 Referral System
- `/refer <name|id>` - Refer a player who invited you (one-time use)

### ❓ Help
- `/ptshelp` or `/playerhelp` or `/trackersuitehelp` - Shows available commands based on permissions

## 📋 Dependencies

- **Required**: PlayerDatabase plugin
- **Optional**: Economics or ServerRewards plugin (for rewards functionality)

## 🧠 Technical Details

### 🗄️ Data Storage
The plugin uses PlayerDatabase to store all player data, including:
- IP history (as JSON list)
- Name history (as JSON list)
- First seen timestamp
- Last seen timestamp
- Last position (as JSON object)
- Total playtime (in seconds)
- Total AFK time (in seconds)
- Referral information

### ⚙️ AFK Detection
The plugin detects AFK status by monitoring player position changes at regular intervals configured in the settings. If a player's position doesn't change between checks, they're considered potentially AFK.

### 🔄 Session Handling
Active sessions are tracked in memory with the following data:
- Session start time
- Last active time
- Last position
- AFK status flag

## 🚀 Installation

1. Ensure you have the PlayerDatabase plugin installed
2. Upload PlayerTrackerSuite.cs to your oxide/plugins directory
3. Configure the plugin in oxide/config/PlayerTrackerSuite.json
4. Set up permissions as needed

## 💡 Tips

- Set appropriate AFK check intervals based on your server performance needs
- Configure reward intervals and amounts to match your server economy
- Use multipliers to reward VIP players with extra benefits
- Regularly check playtime statistics to identify your most active players

---

*Player Tracker Suite v1.0.4 by pkeffect*
