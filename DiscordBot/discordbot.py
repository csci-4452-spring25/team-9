import os
from discord import Intents
from discord.ext import commands
from discord import app_commands
from github import Github
import discord
import boto3
from dotenv import load_dotenv
load_dotenv()

# Get environment variables
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
GH_TOKEN = os.getenv("GH_TOKEN")
GH_REPO = os.getenv("GH_REPO")
GH_BRANCH = os.getenv("GH_BRANCH", "main")
TFVARS_FOLDER = os.getenv("TFVARS_FOLDER", "MinecraftServer")
AWS_REGION = "us-east-1"
INSTANCE_NAME = "Minecraft Server"

# GitHub setup
github = Github(GH_TOKEN)
repo = github.get_repo(GH_REPO)

# AWS setup
ec2 = boto3.client('ec2', region_name=AWS_REGION)

# Discord bot setup
intents = Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)
tree = bot.tree

# Create the tfvars file
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
        # Check if the file already exists
        try:
            existing_file = repo.get_contents(filename, ref=GH_BRANCH)
            sha = existing_file.sha  # Get the current SHA of the existing file
            
            # If it exists, update it
            repo.update_file(
                path=filename,
                message=f"Update tfvars file via Discord bot: {filename}",
                content=content,
                sha=sha,
                branch=GH_BRANCH
            )
            await interaction.response.send_message(f"✅ tfvars file updated.")
        except Exception:
            # If the file does not exist, create it
            repo.create_file(
                path=filename,
                message=f"Add tfvars file via Discord bot: {filename}",
                content=content,
                branch=GH_BRANCH
            )
            await interaction.response.send_message(f"✅ tfvars file created.")
    except Exception as e:
        await interaction.response.send_message(f"❌ Failed to push file: {str(e)}")
# /status command
@tree.command(name="status", description="Check the status of the Minecraft server")
async def status(interaction: discord.Interaction):
    try:
        instances = ec2.describe_instances(Filters=[{'Name': 'tag:Name', 'Values': [INSTANCE_NAME]}])
        instance = instances['Reservations'][0]['Instances'][0]
        state = instance['State']['Name']
        public_ip = instance.get('PublicIpAddress', 'N/A')

        status_message = f"✅ Server Status: {state.capitalize()}. "
        if public_ip != 'N/A':
            status_message += f"Public IP: {public_ip}"
        else:
            status_message += "No public IP assigned."

        await interaction.response.send_message(status_message)
    except Exception as e:
        await interaction.response.send_message(f"❌ Failed to retrieve server status: {str(e)}")

# /shutdown command
@tree.command(name="shutdown", description="Shutdown the Minecraft server")
async def shutdown(interaction: discord.Interaction):
    try:
        instances = ec2.describe_instances(Filters=[{'Name': 'tag:Name', 'Values': [INSTANCE_NAME]}])
        instance_id = instances['Reservations'][0]['Instances'][0]['InstanceId']
        ec2.stop_instances(InstanceIds=[instance_id])

        await interaction.response.send_message(f"✅ Minecraft server {INSTANCE_NAME} is shutting down.")
    except Exception as e:
        await interaction.response.send_message(f"❌ Failed to shutdown server: {str(e)}")

# /resume command
@tree.command(name="resume", description="Resume the Minecraft server")
async def resume(interaction: discord.Interaction):
    try:
        instances = ec2.describe_instances(Filters=[{'Name': 'tag:Name', 'Values': [INSTANCE_NAME]}])
        instance_id = instances['Reservations'][0]['Instances'][0]['InstanceId']
        ec2.start_instances(InstanceIds=[instance_id])

        await interaction.response.send_message(f"✅ Minecraft server {INSTANCE_NAME} is resuming.")
    except Exception as e:
        await interaction.response.send_message(f"❌ Failed to resume server: {str(e)}")

@bot.event
async def on_ready():
    print(f"Bot is ready as {bot.user}")
    try:
        synced = await tree.sync()
        print(f"Synced {len(synced)} command(s).")
    except Exception as e:
        print(f"Error syncing commands: {e}")

bot.run(DISCORD_TOKEN)
