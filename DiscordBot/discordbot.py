import os
from discord import Intents
from discord.ext import commands
from discord import app_commands
from github import Github
import discord

# Get environment variables
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
GH_TOKEN = os.getenv("GH_TOKEN")
GH_REPO = os.getenv("GH_REPO")
GH_BRANCH = os.getenv("GH_BRANCH", "main")
TFVARS_FOLDER = os.getenv("TFVARS_FOLDER", "MinecraftServer")

# GitHub setup
github = Github(GH_TOKEN)
repo = github.get_repo(GH_REPO)

# Discord bot setup
intents = Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)
tree = bot.tree

@tree.command(name="create", description="Create a new tfvars file in GitHub")
@app_commands.describe(
    region="AWS region (default: us-east-1)",
    instance_type="EC2 instance type (default: t2.small)",
    mojang_server_url="Minecraft server JAR URL (default: Mojang vanilla server)"
)
async def push_tfvars(
    interaction: discord.Interaction,
    region: str = "",
    instance_type: str = "",
    mojang_server_url: str = ""
):
    # Apply defaults if blank
    region = region or "us-east-1"
    instance_type = instance_type or "t2.small"
    mojang_server_url = mojang_server_url or "https://piston-data.mojang.com/v1/objects/e6ec2f64e6080b9b5d9b471b291c33cc7f509733/server.jar"

    content = (
        f'region = "{region}"\n'
        f'instance_type = "{instance_type}"\n'
        f'mojang_server_url = "{mojang_server_url}"\n'
    )

    filename = f"MinecraftServer/terraform.tfvars"

    try:
        repo.create_file(
            path=filename,
            message=f"Add tfvars file via Discord bot: {filename}",
            content=content,
            branch=GH_BRANCH
        )
        await interaction.response.send_message(f"✅ tfvars file pushed to `{filename}` in `{GH_REPO}`.")
    except Exception as e:
        await interaction.response.send_message(f"❌ Failed to push file: {str(e)}")

@bot.event
async def on_ready():
    print(f"Bot is ready as {bot.user}")
    try:
        synced = await tree.sync()
        print(f"Synced {len(synced)} command(s).")
    except Exception as e:
        print(f"Error syncing commands: {e}")

bot.run(DISCORD_TOKEN)
