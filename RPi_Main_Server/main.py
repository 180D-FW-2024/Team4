import threading
from camera import Camera
from telegram_bot import TelegramBotHandler, TOKEN
from alarm import ring_alarm
from speech_recognition_data import Speech_Recognition_Data

class SystemManager:
    """
    Manages the camera system, Telegram bot, and alarm system in a multi-threaded environment.
    """
    def __init__(self, telegram_token):
        self.telegram_bot = TelegramBotHandler(telegram_token, self)
        self.camera = Camera()
        self.speech_recog_data = Speech_Recognition_Data(udp_ip="0.0.0.0", udp_port=5200)

    def start_camera(self):
        """
        Start the camera detection system.
        """
        self.camera.run()

    def start_telegram_bot(self):
        """
        Start the Telegram bot to handle user messages.
        """
        self.telegram_bot.run()

    def start_speech_recog_data(self):
        """
        Start the speech recognition data UDP communication system.
        """
        self.speech_recog_data.run()

    def get_annotated_frame(self):
        """
        Get the latest annotated frame from the Camera.
        """
        return self.camera.get_annotated_frame()

    def run(self):
        """
        Start all components in separate threads.
        """
        # Threads for each component
        camera_thread = threading.Thread(target=self.start_camera, name="CameraThread")
        bot_thread = threading.Thread(target=self.start_telegram_bot, name="BotThread")
        speech_recog_data_thread = threading.Thread(target=self.start_speech_recog_data, name="SpeechRecogDataThread")

        # Start threads
        camera_thread.start()
        bot_thread.start()
        speech_recog_data_thread.start()

        # Join threads to ensure the main program waits for them to complete
        camera_thread.join()
        bot_thread.join()
        speech_recog_data_thread.join()

if __name__ == "__main__":
    system_manager = SystemManager(telegram_token=TOKEN)
    system_manager.run()
