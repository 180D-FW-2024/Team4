import threading
import time
from camera import Camera
from telegram_bot import TelegramBotHandler, TOKEN
from alarm import ring_alarm
from speech_recognition_data import Speech_Recognition_Data
from stepcounter_data import StepCounterReceiver
from fall_detection_receiver import FallDetectionReceiver
from video_rover_receiver import VideoRoverReceiver

class SystemManager:
    """
    Manages the camera system, Telegram bot, step counter, and other subsystems in a multi-threaded environment.
    """
    def __init__(self, telegram_token):
        self.system_active = False
        self.system_lock = threading.Lock()

        # Pass self to all components
        self.speech_recog_data = Speech_Recognition_Data(
            system_manager=self,
            udp_ip="0.0.0.0",
            udp_port=5200
        )
        self.telegram_bot = TelegramBotHandler(telegram_token, self)
        self.camera = Camera(system_manager=self)
        self.step_counter = StepCounterReceiver(system_manager=self, udp_ip="0.0.0.0", udp_port=5005)  # Modified
        self.fall_detection = FallDetectionReceiver(system_manager=self, udp_ip="0.0.0.0", udp_port=5001)  # Modified
        self.video_receiver = VideoRoverReceiver(udp_ip="0.0.0.0", udp_port=5055)
    
    def start_video_receiver(self):
        self.video_receiver.run()
        
    def get_video_frame(self):
        return self.video_receiver.get_latest_frame()

    def set_system_active(self, value):
        with self.system_lock:
            self.system_active = value

    def get_system_active(self):
        with self.system_lock:
            return self.system_active

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

    def start_step_counter(self):
        """
        Start the step counter UDP receiver system.
        """
        self.step_counter.run()

    def start_fall_detection_data(self):
        """
        Start the fall detection UDP receiver system
        """
        self.fall_detection.run()

    def get_annotated_frame(self):
        """
        Get the latest annotated frame from the Camera.
        """
        return self.camera.get_annotated_frame()

    def run(self):
        # Keep original thread creation (remove daemon=True)
        threads = [
            threading.Thread(target=self.start_camera, name="CameraThread"),
            threading.Thread(target=self.start_telegram_bot, name="BotThread"),
            threading.Thread(target=self.start_speech_recog_data, name="SpeechRecogDataThread"),
            threading.Thread(target=self.start_step_counter, name="StepCounterThread"),
            threading.Thread(target=self.start_fall_detection_data, name="FallDetectionThread"),
            threading.Thread(target=self.start_video_receiver, name="VideoRoverReceiverThread")
        ]

        # Start threads normally
        for t in threads:
            t.start()

        # Graceful shutdown handling
        try:
            while any(t.is_alive() for t in threads):
                time.sleep(0.5)
        except KeyboardInterrupt:
            print("\nShutting down...")
            self.set_system_active(False)  # Signal components to stop
        finally:
            for t in threads:
                t.join(timeout=1)
            print("All threads terminated")

if __name__ == "__main__":
    system_manager = SystemManager(telegram_token=TOKEN)
    system_manager.run()
