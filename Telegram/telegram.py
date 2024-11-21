import requests

class TelegramBot:
    def __init__(self, token):
        """
        Initializes the Telegram Bot with the provided token.
        :param token: The bot token from @BotFather
        """
        self.base_url = f"https://api.telegram.org/bot{token}/"

    def send_message(self, chat_id, message):
        """
        Sends a message to the specified chat ID.
        :param chat_id: The chat ID to send the message to
        :param message: The text message to send
        """
        url = f"{self.base_url}sendMessage"
        payload = {
            "chat_id": chat_id,
            "text": message
        }
        response = requests.post(url, data=payload)
        if response.status_code == 200:
            print("Message sent successfully.")
        else:
            print(f"Failed to send message: {response.text}")

    def send_photo(self, chat_id, photo_path):
        """
        Sends a photo to the specified chat ID.
        :param chat_id: The chat ID to send the photo to
        :param photo_path: The file path of the photo to send
        """
        url = f"{self.base_url}sendPhoto"
        with open(photo_path, 'rb') as photo_file:
            files = {'photo': photo_file}
            payload = {'chat_id': chat_id}
            response = requests.post(url, data=payload, files=files)
            if response.status_code == 200:
                print("Photo sent successfully.")
            else:
                print(f"Failed to send photo: {response.text}")

    def get_updates(self):
        """
        Retrieves the latest messages sent to the bot.
        :return: A list of updates (messages)
        """
        url = f"{self.base_url}getUpdates"
        response = requests.get(url)
        if response.status_code == 200:
            updates = response.json()
            return updates.get("result", [])
        else:
            print(f"Failed to get updates: {response.text}")
            return []

    def handle_messages(self):
        """
        Polls for new messages and responds to commands.
        Handles '/Hello' with a text response and '/Picture' with an image.
        """
        last_update_id = None
        while True:
            updates = self.get_updates()
            for update in updates:
                # Skip messages we've already processed
                update_id = update["update_id"]
                if last_update_id is not None and update_id <= last_update_id:
                    continue

                # Extract chat ID and message text
                chat_id = update.get("message", {}).get("chat", {}).get("id")
                message = update.get("message", {}).get("text", "")

                if chat_id and message:
                    print(f"Chat ID: {chat_id}, Received message: {message}")
                    if message.strip() == "/Hello":
                        self.send_message(chat_id, "Hello World")
                    elif message.strip() == "/Picture":
                        # Path to the image to be sent
                        image_path = "image.jpeg"
                        self.send_photo(chat_id, image_path)

                last_update_id = update_id


if __name__ == "__main__":
    TOKEN = "8130916663:AAHJCc60c8y6N-U4SPlf4GgJT04d5z8tFdA"
    bot = TelegramBot(TOKEN)

    # Start handling messages
    bot.handle_messages()
