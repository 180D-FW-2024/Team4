import requests
import io
import cv2
import time
from alarm import ring_alarm

TOKEN = "8130916663:AAHJCc60c8y6N-U4SPlf4GgJT04d5z8tFdA"
CHAT_ID = 6655795833

def send_message(message, token=TOKEN, chat_id=CHAT_ID):
    """
    Sends a message to the specified chat ID.
    """
    base_url = f"https://api.telegram.org/bot{token}/"
    url = f"{base_url}sendMessage"
    payload = {"chat_id": chat_id, "text": message}
    response = requests.post(url, data=payload)
    if response.status_code == 200:
        print("Message sent successfully.")
    else:
        print(f"Failed to send message: {response.text}")

def send_frame(frame, token=TOKEN, chat_id=CHAT_ID):
    """
    Sends a photo (from np.array) to the specified chat ID.
    """
    base_url = f"https://api.telegram.org/bot{token}/"
    url = f"{base_url}sendPhoto"

    # Convert the frame (np.array) to an image
    _, buffer = cv2.imencode('.jpg', frame)
    image_io = io.BytesIO(buffer)

    # Send the image to Telegram
    files = {'photo': ('frame.jpg', image_io, 'image/jpeg')}
    payload = {'chat_id': chat_id}
    response = requests.post(url, data=payload, files=files)

    if response.status_code == 200:
        print("Photo sent successfully.")
    else:
        print(f"Failed to send photo: {response.text}")

class TelegramBotHandler:
    def __init__(self, token, system_manager):
        """
        Initializes the Telegram Bot with the provided token and SystemManager instance.
        """
        self.base_url = f"https://api.telegram.org/bot{token}/"
        self.last_update_id = None  # Track the last processed update ID
        self.system_manager = system_manager  # Store reference to SystemManager

    def send_message(self, chat_id, message):
        """
        Sends a message to the specified chat ID.
        """
        url = f"{self.base_url}sendMessage"
        payload = {"chat_id": chat_id, "text": message}
        response = requests.post(url, data=payload)
        if response.status_code == 200:
            print("Message sent successfully.")
        else:
            print(f"Failed to send message: {response.text}")

    def send_frame(self, chat_id, frame):
        """
        Sends a photo (from np.array) to the specified chat ID.
        """
        url = f"{self.base_url}sendPhoto"

        # Convert the frame (np.array) to an image
        _, buffer = cv2.imencode('.jpg', frame)
        image_io = io.BytesIO(buffer)

        # Send the image to Telegram
        files = {'photo': ('frame.jpg', image_io, 'image/jpeg')}
        payload = {'chat_id': chat_id}
        response = requests.post(url, data=payload, files=files)

        if response.status_code == 200:
            print("Photo sent successfully.")
        else:
            print(f"Failed to send photo: {response.text}")

    def get_updates(self):
        """
        Retrieves the latest messages sent to the bot, filtered by `last_update_id`.
        """
        url = f"{self.base_url}getUpdates"
        params = {"offset": self.last_update_id + 1} if self.last_update_id else {}
        response = requests.get(url, params=params)
        if response.status_code == 200:
            updates = response.json()
            return updates.get("result", [])
        else:
            print(f"Failed to get updates: {response.text}")
            return []

    def run(self):
        """
        Polls for new messages and responds to commands.
        """
        while True:
            updates = self.get_updates()
            for update in updates:
                # Extract the update ID
                update_id = update.get("update_id")

                # Skip updates we've already processed
                if self.last_update_id is not None and update_id <= self.last_update_id:
                    continue

                # Extract chat ID and message text
                chat_id = update.get("message", {}).get("chat", {}).get("id")
                message = update.get("message", {}).get("text", "")

                if chat_id and message:
                    print(f"Chat ID: {chat_id}, Received message: {message}")
                    if message.strip() == "/Hello":
                        self.send_message(chat_id, "Hello World")
                    elif message.strip() == "/MainCam":
                        # Fetch the latest annotated frame from the Camera
                        frame = self.system_manager.get_annotated_frame()
                        if frame is None:
                            self.send_message(chat_id, "No output camera frame yet")
                        else:
                            self.send_frame(chat_id, frame)
                            self.send_message(chat_id, "Main camera frame sent")
                    elif message.strip() == "/SoundAlarm":
                        ring_alarm()
                        self.send_message(chat_id, "Alarm rang test")

                # Update the last update ID after processing
                self.last_update_id = update_id
            time.sleep(0.5)
