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

---
