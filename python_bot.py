import discord
from discord import app_commands
from discord.ext import commands
import json
import os

# --- SETUP BOT ---
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

DB_FILE = "database.json"

# --- DEFAULT CHARACTER TEMPLATE ---
def get_default_profile(user_name):
    return {
        "name": user_name,
        "hp": 28,
        "max_hp": 28,
        "fp": 90,
        "max_fp": 90,
        "int": 28,
        "dex": 18,
        "right_hand": "Carian Glintstone Sword",
        "left_hand": "Main-Gauche (Frost)",
        "memory_slots": [
            "Carian Slicer",
            "Carian Piercer",
            "Adula's Moonblade",
            "Miriam's Vanishing"
        ]
    }

# --- DATABASE HANDLERS ---
def load_db():
    if not os.path.exists(DB_FILE):
        with open(DB_FILE, "w") as f:
            json.dump({}, f)
        return {}
    with open(DB_FILE, "r") as f:
        return json.load(f)

def save_db(data):
    with open(DB_FILE, "w") as f:
        json.dump(data, f, indent=4)

def get_player(user_id, user_name):
    db = load_db()
    uid = str(user_id)
    if uid not in db:
        db[uid] = get_default_profile(user_name)
        save_db(db)
    return db, db[uid]

# --- EVENTS ---
@bot.event
async def on_ready():
    await bot.tree.sync()
    print(f"✨ Royal Carian Engine is online as {bot.user}!")

# --- COMMANDS ---

@bot.tree.command(name="status", description="Check your current character status.")
async def status(interaction: discord.Interaction):
    _, player = get_player(interaction.user.id, interaction.user.display_name)
    spells = "\n• " + "\n• ".join(player["memory_slots"])

    embed = discord.Embed(title=f"⚔️ {player['name']} - Carian Spell-Fencer", color=0x3498db)
    embed.add_field(name="❤️ HP", value=f"{player['hp']}/{player['max_hp']}", inline=True)
    embed.add_field(name="🔷 FP", value=f"{player['fp']}/{player['max_fp']}", inline=True)
    embed.add_field(name="📊 Stats", value=f"INT: `{player['int']}` | DEX: `{player['dex']}`", inline=True)
    embed.add_field(name="🗡️ Right Hand", value=f"`{player['right_hand']}`", inline=False)
    embed.add_field(name="🛡️ Left Hand", value=f"`{player['left_hand']}`", inline=True)
    embed.add_field(name="📜 Memorized Spells", value=spells, inline=False)

    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="swap", description="Toggle Right Hand between Staff and Sword.")
async def swap(interaction: discord.Interaction):
    db, player = get_player(interaction.user.id, interaction.user.display_name)
    
    if player["right_hand"] == "Carian Glintstone Sword":
        player["right_hand"] = "Carian Academy Staff"
    else:
        player["right_hand"] = "Carian Glintstone Sword"
        
    db[str(interaction.user.id)] = player
    save_db(db)
    await interaction.response.send_message(f"🔄 **{interaction.user.display_name}** swapped Right Hand to: **{player['right_hand']}**!")

@bot.tree.command(name="slicer", description="Cast Carian Slicer (2 FP).")
async def slicer(interaction: discord.Interaction):
    db, player = get_player(interaction.user.id, interaction.user.display_name)

    cost = 2
    if player["fp"] < cost:
        await interaction.response.send_message("❌ Not enough FP!", ephemeral=True)
        return

    player["fp"] -= cost
    
    # Damage calculation
    base_dmg = 8 + (player["int"] // 2)
    bonus = ""
    if player["right_hand"] == "Carian Glintstone Sword":
        base_dmg = int(base_dmg * 1.2)
        bonus = " *(+20% Carian Sword Affinity)*"

    db[str(interaction.user.id)] = player
    save_db(db)

    embed = discord.Embed(
        title="🗡️ Carian Slicer!", 
        description=f"**{interaction.user.display_name}** slashes with a conjure glintstone blade!\n"
                    f"💥 **Damage:** `{base_dmg}` Magic Damage{bonus}\n"
                    f"🔷 **Remaining FP:** `{player['fp']}/{player['max_fp']}`",
        color=0x00a8ff
    )
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="rest", description="Rest at a Site of Grace to restore HP and FP.")
async def rest(interaction: discord.Interaction):
    db, player = get_player(interaction.user.id, interaction.user.display_name)
    player["hp"] = player["max_hp"]
    player["fp"] = player["max_fp"]
    
    db[str(interaction.user.id)] = player
    save_db(db)
    await interaction.response.send_message(f"✨ **{interaction.user.display_name}** rested at a Site of Grace. HP and FP are fully restored!")

# Put your bot token here
bot.run("MTU1MjA0Nzg1MzkxOTE1MDE4Mg.GEd86_.I6rGKZ8OXiFEdFDm49MsrEvOLvdIucYlngvLt4")