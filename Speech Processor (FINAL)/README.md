# Speech Processor Summary
The `speechpi.py` script is responsible for **voice command processing** in the Nightwatcher system. It enables hands-free control of the system, allowing users to activate, deactivate, or modify settings using **spoken commands**.

The script listens for a **wake phrase** (e.g., *"Hey Watcher"*) and then processes subsequent commands to control Nightwatcher's subsystems.


# How to Run the Speech Processor

## Install Dependencies
Run the following command to install the required Python libraries:
```bash
pip install speechrecognition requests edge-tts langchain langchain_groq groq pydantic
```

## Hardware Setup
Ensure that both the **microphone and speaker** are connected to the Raspberry Pi before running the speech processor unit.

## API Keys and installation setup 
Visit the website https://console.groq.com/login to make an account and create an API Key to use the necessary models that Groq supplies for speech recognition.
After that is complete then it is viable that you update the speechpi.py file accordingly to include your necessary API keys. This would be the only modification necessary if a user wants to utilize our scripts. Beyond that it will fully be funcitonal.
![image](https://github.com/user-attachments/assets/920a568f-bf75-4221-bad3-2a225b967b5f)

## Running the Speech Processor
```bash
python speechpi.py
```

## Code Origin and Design 
### **1. Source of Code**
- The speech recognition functionality is built using the **SpeechRecognition** library in Python.
- It integrates **GroqCloud** for remote speech-to-text transcription.
- The wake-word detection and command parsing system are inspired by **existing AI voice assistants** but adapted for **low-power Raspberry Pi 4**.

### **2. Overall Design Considerations**
- **Wake Phrase Implementation**:
  - The system remains idle until it detects *"Hey Watcher"* to prevent unnecessary processing.
  - This reduces **false activations** from ambient noise or unrelated speech.
- **Cloud-Based Recognition**:
  The the system uses **GroqCloud**, which provides **faster and more accurate transcription**.
- **Command Handling**:
  - Uses **Distil-Whisper** (lightweight language model) to parse commands.
  - Supported commands include:
    - `"Activate System"` – Turns on Nightwatcher monitoring.
    - `"Deactivate System"` – Disables alerts and tracking.
    - `"Status Update"` – Reports current system status.
- **Noise Filtering & Microphone Sensitivity**:
  - Adjusted for **low-light, nighttime operation** to filter out background sounds.
  - Uses an **adaptive threshold** to distinguish between voice commands and ambient noise.



## Known Issues 
The system relies on a internet connection. Unfortunately the API Keys are rate-limited so it is advised to make more than one Groq account if possible to have a few API keys for continous running. When one key becomes rate-limited when switch over to another key until the cooldown ends.

## Future Improvements
Potentially looking into better API services that has more lenient rates for running the speech processsing. As of now Groq seemed to fit the needs of this project best.

##Notes 
This subfolder is part of the larger NigthWatcher system and is only on the speech processor component that would be installed on the wearable device.

---
