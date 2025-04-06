import os
from dotenv import load_dotenv
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

# Load environment variables
load_dotenv()

# Get tokens from environment
SLACK_BOT_TOKEN = os.getenv("SLACK_BOT_TOKEN")
SLACK_APP_TOKEN = os.getenv("SLACK_APP_TOKEN")
SLACK_CHANNEL_ID = os.getenv("SLACK_CHANNEL_ID")

def test_slack_connectivity():
    """Test basic Slack API connectivity."""
    print("Testing Slack connectivity...")
    print(f"Using bot token: {SLACK_BOT_TOKEN[:5]}...{SLACK_BOT_TOKEN[-5:] if SLACK_BOT_TOKEN else None}")
    print(f"Using app token: {SLACK_APP_TOKEN[:5]}...{SLACK_APP_TOKEN[-5:] if SLACK_APP_TOKEN else None}")
    
    # Initialize WebClient
    client = WebClient(token=SLACK_BOT_TOKEN)
    
    try:
        # Test 1: Get bot info
        print("\nTest 1: Getting bot info...")
        auth_test = client.auth_test()
        print(f"✅ Connected as: {auth_test['user']} to workspace: {auth_test['team']}")
        
        # Test 2: List channels
        print("\nTest 2: Listing accessible channels...")
        response = client.conversations_list(types="public_channel,private_channel")
        channels = response["channels"]
        print(f"✅ Bot can see {len(channels)} channels")
        
        # Print channels for debugging
        print("Channels accessible to the bot:")
        for channel in channels:
            channel_id = channel["id"]
            channel_name = channel["name"]
            is_member = channel.get("is_member", False)
            print(f"  - {channel_name} (ID: {channel_id}) {'✅ Bot is a member' if is_member else '❌ Bot is NOT a member'}")
            
            # Check if this is the configured channel
            if channel_id == SLACK_CHANNEL_ID:
                print(f"    ⭐ This is your configured channel (SLACK_CHANNEL_ID)")
        
        # Test 3: Try to post a message
        if SLACK_CHANNEL_ID:
            print(f"\nTest 3: Posting test message to channel ID: {SLACK_CHANNEL_ID}...")
            try:
                result = client.chat_postMessage(
                    channel=SLACK_CHANNEL_ID,
                    text="Hello! This is a connectivity test message."
                )
                print(f"✅ Message sent successfully: {result['ts']}")
            except SlackApiError as e:
                print(f"❌ Failed to post message: {e.response['error']}")
                print("   Possible reasons:")
                print("   - Bot is not in the channel")
                print("   - Bot doesn't have chat:write permission")
                print("   - Channel ID is incorrect")
        else:
            print("\nTest 3: Skipped posting test message (SLACK_CHANNEL_ID not set)")
            
    except SlackApiError as e:
        print(f"❌ Error: {e.response['error']}")
        if e.response["error"] == "invalid_auth":
            print("   This suggests your SLACK_BOT_TOKEN is invalid or expired")
        elif e.response["error"] == "not_authed":
            print("   This suggests you're missing the SLACK_BOT_TOKEN")

if __name__ == "__main__":
    test_slack_connectivity()
