# 🔄 Item Cloner Advanced - Rust Plugin Documentation

## 📋 Overview

Item Cloner Advanced is a comprehensive Rust plugin that allows players to clone items with extensive configuration options including tiered permissions, cooldowns, resource costs, and detailed analytics tracking. This plugin provides server administrators with fine-grained control over what items can be cloned, who can clone them, how often, and at what cost.

## ✨ Key Features

- 🔐 **Tiered Permission System**: Configure different user tiers with varying clone limits, cooldowns, and costs
- 💰 **Resource Costs**: Set costs for cloning based on fixed values, item value percentage, or item tier
- ⏲️ **Flexible Cooldowns**: Set global, category-specific, or item-specific cooldown periods
- 🚫 **Item Restrictions**: Use blacklist or whitelist mode to control which items can be cloned
- 📊 **Detailed Analytics**: Track cloning statistics, resource usage, and more
- 📱 **User Interface**: Optional UI to display clone information and controls
- 📈 **Wipe Cycle Management**: Reset clone limits automatically with each server wipe
- 🔄 **Auto-Reload**: Configuration is automatically applied when the config file changes
- 📝 **Comprehensive Logging**: Records all clone actions to console and/or file

## 🔑 Permissions

- `itemcloneradvanced.use` - Base permission to use the cloning system
- `itemcloneradvanced.admin` - Bypass all restrictions, costs, and cooldowns
- `itemcloneradvanced.unlimited` - Unlimited cloning with no costs or cooldowns
- Tier-specific permissions:
  - `itemcloneradvanced.use.tier1` - Basic tier access
  - `itemcloneradvanced.use.tier2` - Advanced tier access
  - `itemcloneradvanced.use.tier3` - Elite tier access

## 💬 Chat Commands

- `/clone` - Clone the item currently held in your hands
- `/cloneui` - Toggle the clone information UI panel
- `/clonehelp` - Display help information and available commands

## 🖥️ Console Commands

- `itemcloneradvanced.reset <playerID|playerName|'all'|'analytics'|'wipe'>` - Reset clone data
  - `playerID|playerName` - Reset data for a specific player
  - `all` - Reset data for all players
  - `analytics` - Reset analytics data
  - `wipe` - Simulate a wipe reset
- `itemcloneradvanced.stats` - Display detailed cloning statistics
- `itemcloneradvanced.clearcooldown <playerID|playerName|'all'>` - Clear clone cooldowns
  - `playerID|playerName` - Clear cooldown for a specific player
  - `all` - Clear all active cooldowns

## ⚙️ Configuration

The plugin uses a comprehensive configuration system divided into several sections:

### 1. General Settings

```json
"1. General Settings": {
  "Enable Auto Reloading": true,
  "Data Save Interval (Minutes)": 10,
  "Log Cloning to Console": true,
  "Log Cloning to File": true,
  "Debug Mode": false
}
```

### 2. Command Settings

```json
"2. Command Settings": {
  "Chat Command: Clone Item": "clone",
  "Chat Command: Toggle Clone UI": "cloneui",
  "Chat Command: Help": "clonehelp",
  "Console Command: Reset Player/All/Analytics Data": "itemcloneradvanced.reset",
  "Console Command: Show Stats": "itemcloneradvanced.stats",
  "Console Command: Clear Player/All Cooldown": "itemcloneradvanced.clearcooldown"
}
```

### 3. Cloning Restrictions

```json
"3. Cloning Restrictions": {
  "Mode (Blacklist or Whitelist)": "Blacklist",
  "Item List (Shortnames)": ["rock", "torch", "hammer"],
  "Category Restrictions": {
    "Weapon": false,
    "Ammunition": false,
    "Construction": false,
    "Items": false,
    "Resources": false,
    "Attire": false,
    "Tool": false,
    "Medical": false,
    "Food": false,
    "Component": false
  }
}
```

### 4. Resource Costs

```json
"4. Resource Costs": {
  "Enable Resource Costs": false,
  "Cost Scaling Method (Fixed, PercentageOfValue, ItemTier)": "Fixed",
  "Fixed Costs (ItemShortname: Amount)": {
    "scrap": 10
  },
  "Value Percentage Cost": 10.0,
  "Scale by Item Rarity (Tier1: Percentage, Tier2: Percentage, etc)": {
    "0": 5.0,
    "1": 10.0,
    "2": 15.0,
    "3": 25.0,
    "4": 50.0
  },
  "Refund Percentage on Failure (0-100)": 50.0
}
```

### 5. Cooldown Settings

```json
"5. Cooldown Settings": {
  "Enable Cooldowns": true,
  "Global Cooldown (Seconds)": 60.0,
  "Per Item Type Cooldowns (ItemShortname: Seconds)": {
    "rifle.ak": 300.0,
    "rifle.lr300": 300.0,
    "rifle.bolt": 300.0
  },
  "Cooldown by Item Category (Category: Seconds)": {
    "Weapon": 180.0,
    "Ammunition": 30.0,
    "Construction": 60.0
  }
}
```

### 6. UI Settings

```json
"6. UI Settings": {
  "Enable UI": true,
  "Show Clone Count": true,
  "Show Cooldown": true,
  "Show Cost": true,
  "UI X Position (0.0-1.0)": 0.5,
  "UI Y Position (0.0-1.0)": 0.85
}
```

### 7. Tiered Permissions

```json
"7. Tiered Permissions": {
  "basic": {
    "Permission Suffix": "tier1",
    "Clone Limit Per Wipe": 10,
    "Cooldown Multiplier (0.0-1.0, lower is faster)": 1.0,
    "Cost Multiplier (0.0-1.0, lower is cheaper)": 1.0,
    "Allowed Item Categories": ["Tool", "Construction", "Resources"],
    "Cloning Quality (0.0-1.0, higher is better condition)": 0.9
  },
  "advanced": {
    "Permission Suffix": "tier2",
    "Clone Limit Per Wipe": 25,
    "Cooldown Multiplier": 0.75,
    "Cost Multiplier": 0.75,
    "Allowed Item Categories": ["Tool", "Construction", "Resources", "Medical", "Food", "Component", "Attire"],
    "Cloning Quality": 0.95
  },
  "elite": {
    "Permission Suffix": "tier3",
    "Clone Limit Per Wipe": 50,
    "Cooldown Multiplier": 0.5,
    "Cost Multiplier": 0.5,
    "Allowed Item Categories": ["Tool", "Construction", "Resources", "Medical", "Food", "Component", "Attire", "Weapon", "Ammunition"],
    "Cloning Quality": 1.0
  }
}
```

## 📝 Logging and Data Storage

### Logging Options

- Console logging (configurable)
- File logging (configurable)
- Log file: `ItemClonerAdvanced-Logs.txt`

### Data Storage

The plugin maintains two separate data files:

1. **Player Data** (`ItemClonerAdvanced_Data.json`):
   - Tracks individual player clone usage
   - Records clone history per player
   - Stores wipe cycle information

2. **Analytics Data** (`ItemClonerAdvanced_Analytics.json`):
   - Tracks most frequently cloned items
   - Records resource spending patterns
   - Monitors permission tier usage
   - Logs common errors and success/failure rates

### Clone Record Tracking

For each clone operation, the plugin records:
- Item shortname and display name
- Amount cloned
- Item condition
- Skin ID
- Timestamp
- Resource costs

## 🔄 Cloning Process

The plugin performs the following checks before cloning:
1. Permission verification
2. Active item validation
3. Item restriction checks
4. Cooldown verification
5. Clone limit validation
6. Resource cost calculation
7. Resource availability check

If all checks pass:
1. Resources are deducted
2. Item is cloned with appropriate quality based on tier
3. Cooldown is applied
4. Clone record is saved
5. Analytics are updated

## 🌐 Localization

The plugin includes a comprehensive localization system that can be customized for different languages. All user-facing messages can be translated through the language file.

## 🔄 Auto-Reload System

The configuration auto-reload feature monitors the config file for changes and automatically reloads the plugin when changes are detected. This allows for live configuration updates without server restarts.

## 🔄 Wipe Detection

The plugin automatically detects server wipes and resets clone limits accordingly. It uses a combination of server startup time and last wipe timestamp to determine if a wipe has occurred.

## ⚡ Performance Considerations

- Data is saved periodically (configurable interval)
- UI is updated efficiently only when needed
- Configuration loading is optimized for performance
- Error handling ensures plugin stability

## 🛠️ Advanced Features

### Item Quality Control

Different tiers can have different quality multipliers, affecting the condition of cloned items. Higher tiers can produce higher quality clones.

### Complex Item Cloning

The plugin properly handles:
- Items with condition
- Items with contents (containers, weapons with attachments)
- Weapons with ammo
- Items with instance data (blueprints, skins)

### Analytics Dashboard

Administrators can access detailed statistics on:
- Most cloned items
- Resource usage patterns
- User tier distribution
- Common errors and success rates

## 📄 License and Credits

Created by pkeffect (v1.0.0)

---

For more plugins and updates, check out the developer's GitHub profile.
