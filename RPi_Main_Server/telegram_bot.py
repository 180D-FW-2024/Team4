import os
import requests
import io
import cv2
import time
from alarm import ring_alarm

# Initialize CHAT_ID from file or default
def load_chat_id():
    """Load chat ID with error handling and file creation"""
    try:
        with open("chat_id.txt", "r") as f:
            return int(f.read().strip())
    except (FileNotFoundError, ValueError):
        # Create file with default if missing or invalid
        default_id = 6655795833
        with open("chat_id.txt", "w") as f:
            f.write(str(default_id))
        return default_id

TOKEN = "8130916663:AAHJCc60c8y6N-U4SPlf4GgJT04d5z8tFdA"
CHAT_ID = load_chat_id()

def send_message(message, token=TOKEN, chat_id=None):
    """
    Sends a message to the specified chat ID.
    """
    global CHAT_ID
    if chat_id is None:
        chat_id = CHAT_ID  # Dynamic lookup
    base_url = f"https://api.telegram.org/bot{token}/"
    url = f"{base_url}sendMessage"
    payload = {"chat_id": chat_id, "text": message}
    response = requests.post(url, data=payload)
    if response.status_code == 200:
        print("Message sent successfully.")
    else:
        print(f"Failed to send message: {response.text}")

def send_frame(frame, token=TOKEN, chat_id=None):
    """
    Sends a photo (from np.array) to the specified chat ID.
    """
    global CHAT_ID
    if chat_id is None:
        chat_id = CHAT_ID  # Dynamic lookup

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

    def save_chat_id(self, new_id):
        """Atomic save with error handling"""
        global CHAT_ID
        try:
            # Atomic file write
            temp_path = "chat_id.txt.tmp"
            with open(temp_path, "w") as f:
                f.write(str(new_id))
            os.replace(temp_path, "chat_id.txt")
            CHAT_ID = new_id
        except Exception as e:
            print(f"Error saving chat ID: {str(e)}")

    def run(self):
        global CHAT_ID

        """
        Polls for new messages and responds to commands.
        """
        while True:
            updates = self.get_updates()
            for update in updates:
                # Extract the update ID
                update_id = update.get("update_id")

                # Skip updates we've already processed
                if self.last_update_id and update_id <= self.last_update_id:
                    continue

                # Extract chat ID and message text
                chat_id = update.get("message", {}).get("chat", {}).get("id")
                message = update.get("message", {}).get("text", "")

                self.last_update_id = update_id  # Add this line
                
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
                    elif message.strip() == "/SetChatID":
                        self.save_chat_id(chat_id)
                        self.send_message(chat_id, 
                            f"Global notification target updated to this chat\n"
                            f"New persistent Chat ID: {chat_id}")

                        # Update the last update ID after processing
                        self.last_update_id = update_id
                        time.sleep(0.5)
                    elif message.strip() == "/GetCamRover":
                        frame = self.system_manager.get_video_frame()
                        if frame is None:
                            self.send_message(chat_id, "No output camera frame yet")
                        else:
                            self.send_frame(chat_id, frame)
                            self.send_message(chat_id, "Rover camera frame sent")