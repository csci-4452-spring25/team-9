import json
import os
import nacl.signing
from discord_interactions import verify_key, InteractionType, InteractionResponseType
from github import Github

# Get environment variables
DISCORD_PUBLIC_KEY = os.getenv("DISCORD_PUBLIC_KEY")
GH_TOKEN = os.getenv("GH_TOKEN")
GH_REPO = os.getenv("GH_REPO")
GH_BRANCH = os.getenv("GH_BRANCH", "main")
TFVARS_FOLDER = os.getenv("TFVARS_FOLDER", "MinecraftServer")

# GitHub setup
github = Github(GH_TOKEN)
repo = github.get_repo(GH_REPO)

# Verify Discord request signature
def verify_signature(event):
    signature = event['headers'].get('x-signature-ed25519')
    timestamp = event['headers'].get('x-signature-timestamp')
    body = event['body']
    
    if not verify_key(body, signature, timestamp, DISCORD_PUBLIC_KEY):
        raise Exception("Invalid request signature")

# Lambda handler function to handle Discord interactions
def lambda_handler(event, context):
    try:
        verify_signature(event)
    except Exception as e:
        return {
            "statusCode": 401,
            "body": "Invalid request"
        }

    body = json.loads(event['body'])

    if body['type'] == 1:  # Discord challenge response
        return {
            "statusCode": 200,
            "body": json.dumps({ "type": 1 })
        }

    if body['data']['name'] == 'create':  # Handle the /create slash command
        region = body['data'].get('options', [{}])[0].get('value', 'us-east-1')
        instance_type = body['data'].get('options', [{}])[1].get('value', 't2.small')
        mojang_server_url = body['data'].get('options', [{}])[2].get('value', 'https://piston-data.mojang.com/v1/objects/e6ec2f64e6080b9b5d9b471b291c33cc7f509733/server.jar')

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
            return {
                "statusCode": 200,
                "body": json.dumps({
                    "type": 4,
                    "data": {
                        "content": "✅ tfvars file pushed to GitHub!"
                    }
                })
            }
        except Exception as e:
            return {
                "statusCode": 500,
                "body": f"❌ Failed to push file: {str(e)}"
            }

    return {
        "statusCode": 400,
        "body": "Unhandled interaction"
    }
