import requests
from tinydb import TinyDB, Query

# Replace 'YOUR_TOKEN' with your bot's token
TOKEN = "7869468711:AAEYBHKlHDJIknZ2yvV3TtP9GPD8A60YnPY"
BASE_URL = f"https://api.telegram.org/bot{TOKEN}"

# Initialize TinyDB
db = TinyDB("user_data.json")

# Handle /start command
def handle_start(chat_id, user):
    user_id = user["id"]

    # Check if user already exists
    User = Query()
    if not db.contains(User.user_id == str(user_id)):
        db.insert({"user_id": str(user_id)})
        send_message(chat_id, "You are now subscribed to notifications!")
    else:
        send_message(chat_id, "You are already subscribed.")

# Handle broadcast message from admin
def handle_broadcast(chat_id, user_id, text):
    ADMIN_ID = 1235929407  # Replace with your admin/owner ID

    if user_id == ADMIN_ID:
        for user in db.all():
            try:
                send_message(user["user_id"], text)
            except Exception as e:
                print(f"Failed to send message to {user['user_id']}: {e}")
        send_message(chat_id, "Broadcast sent to all users!")
    else:
        send_message(chat_id, "You are not authorized to use this command.")

# Send a message to a user
def send_message(chat_id, text):
    url = f"{BASE_URL}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text,
    }
    requests.post(url, json=payload)

# Main function to process updates
def process_update(update):
    message = update.get("message", {})
    chat_id = message.get("chat", {}).get("id")
    user = message.get("from", {})
    user_id = user.get("id")
    text = message.get("text", "")

    if text == "/start":
        handle_start(chat_id, user)
    elif text.startswith("/broadcast"):
        # Extract the message to broadcast
        broadcast_message = text.replace("/broadcast", "").strip()
        if broadcast_message:
            handle_broadcast(chat_id, user_id, broadcast_message)
        else:
            send_message(chat_id, "Usage: /broadcast <message>")

# Poll for new updates
def poll_updates():
    offset = 0
    while True:
        url = f"{BASE_URL}/getUpdates?offset={offset}&timeout=10"
        response = requests.get(url).json()

        if response.get("ok"):
            for update in response.get("result", []):
                process_update(update)
                offset = update.get("update_id") + 1

if __name__ == '__main__':
    poll_updates()
