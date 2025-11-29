import os
import time
import wave
import pyaudio
import keyboard
from openai import OpenAI
from dotenv import load_dotenv
from collections import deque
import pvporcupine
import struct
from utils import visualize_path

# Configuration
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
PORCUPINE_API_KEY = os.getenv("PORCUPINE_API_KEY")
AUDIO_FILE = "Recorded.wav"
CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 1  # Changed to mono for better compatibility
RATE = 44100

# Initialize OpenAI client
client = OpenAI(api_key=OPENAI_API_KEY)

def porcupine_trigger_loop(record_callback):
    """Continuously listen for 'start' and 'stop' using Porcupine, record using your own settings."""
    # === Porcupine: for low-rate trigger detection only ===
    porcupine = pvporcupine.create(
        access_key=PORCUPINE_API_KEY,
        keywords=["alexa", "terminator"]  # use built-in triggers or your own .ppn files
    )
    pa_trigger = pyaudio.PyAudio()
    trigger_stream = pa_trigger.open(
        rate=porcupine.sample_rate,
        channels=1,
        format=pyaudio.paInt16,
        input=True,
        frames_per_buffer=porcupine.frame_length
    )

    # === Your original settings for command recording ===
    pa_audio = pyaudio.PyAudio()

    print("🎙️ Say 'alexa' to begin recording, 'terminator' to stop.")

    is_recording = False
    frames = []

    audio_stream = None

    try:
        while True:
            pcm = trigger_stream.read(porcupine.frame_length, exception_on_overflow=False)
            pcm_unpacked = struct.unpack_from("h" * porcupine.frame_length, pcm)
            keyword_index = porcupine.process(pcm_unpacked)

            if keyword_index == 0 and not is_recording:  # "alexa"
                print("✅ Trigger: 'alexa' detected.")
                is_recording = True
                frames = []
                # open new stream for high-quality recording
                audio_stream = pa_audio.open(format=FORMAT,
                                             channels=CHANNELS,
                                             rate=RATE,
                                             input=True,
                                             frames_per_buffer=CHUNK)

            elif keyword_index == 1 and is_recording:  # "terminator"
                print("🛑 Trigger: 'terminator' detected.")
                is_recording = False
                audio_stream.stop_stream()
                audio_stream.close()

                # Save high-quality audio to file
                with wave.open(AUDIO_FILE, 'wb') as wf:
                    wf.setnchannels(CHANNELS)
                    wf.setsampwidth(pa_audio.get_sample_size(FORMAT))
                    wf.setframerate(RATE)
                    wf.writeframes(b''.join(frames))

                print(f"📁 Audio saved to {AUDIO_FILE}")
                record_callback()  # trigger transcription + LLM

            # During recording, read from high-quality stream
            if is_recording and audio_stream is not None:
                data = audio_stream.read(CHUNK, exception_on_overflow=False)
                frames.append(data)

    except KeyboardInterrupt:
        print("Interrupted.")
    finally:
        trigger_stream.stop_stream()
        trigger_stream.close()
        pa_trigger.terminate()
        if audio_stream is not None:
            audio_stream.close()
        pa_audio.terminate()
        porcupine.delete()

def transcribe_audio():
    """Convert speech to text using Whisper"""
    with open(AUDIO_FILE, "rb") as audio_file:
        transcription = client.audio.transcriptions.create(
            model="whisper-1", 
            file=audio_file
        )
    return transcription.text

# Remove the separate check_clarity function

memory = {"current_structure": "nose"}

def generate_action(command):
    """Generate robotic action or request clarification using GPT-4 in a single call"""

    memory_note = f"\nCURRENT CONTEXT:\nThe current structure is: {memory['current_structure']}\n"
    
    system_prompt = """You are a surgical robotic assistant specializing in nasal endoscopy navigation.

ANATOMY GRAPH - Nasal Structure Connections (BIDIRECTIONAL):
* nose ⟷ nasal_meatus
* nasal_meatus ⟷ superior_nasal_meatus, middle_nasal_meatus, inferior_nasal_meatus
* middle_nasal_meatus ⟷ concha_nasalis_media
* concha_nasalis_media ⟷ sinus_maxillaris, bulla_ethmoidalis, sinus_ethmoidalis
* sinus_ethmoidalis ⟷ sinus_sphenoidalis

YOUR TASK - TWO-STEP PROCESS:
- Each time, you will receive a command to navigate between nasal structures.
- The current structure is given in the context, and you need to identify the endpoint users want to reach from the command.
- Find the path between the current structure and the endpoint, return the path and the updated current structure in a certain format.
- If the command is unclear or no path exists, ask for clarification.

PATH FINDING RULES:
- Paths must follow the connections defined in the ANATOMY GRAPH
- IMPORTANT: Connections are BIDIRECTIONAL - you can traverse in EITHER direction
- Return the complete path from start to destination
- Find the shortest valid path between structures

HANDLING SPEECH RECOGNITION ERRORS:
- Common transcription errors to anticipate:
  - "nasal meatus" might appear as "naso meters," "nasal meatless," etc.
  - "sinus maxillaris" might appear as "sinus, maxillary," "sign is maximalis," etc.
- Use medical knowledge to identify the correct anatomical terms despite transcription errors
- "Terminator" is used as a trigger word for stopping the recording, not as a command.

EVALUATION CRITERIA FOR CLARITY:
- Are the anatomical structures mentioned recognizable as nasal structures? But if it appears as speech recognition errors, you should be able to identify the correct anatomical terms.
- Is the intent to find a path clear? It's ok the user say duplicated phrases, but as long as the command is clear, you should be able to identify the correct anatomical terms.

OUTPUT FORMAT - ALWAYS RETURN BOTH FIELDS:
1. If command is CLEAR:
   PATH: [start] -> [...] -> [end]
   MEMORY: [current_structure]

2. If command is UNCLEAR:
   CLARIFY: [reason]
   MEMORY: null

Examples:
- Command: "Go to middle nasal meatus" (Memory = nose)
  → PATH: nose -> nasal_meatus -> middle_nasal_meatus
    MEMORY: middle_nasal_meatus

- Command: "From nose to concha nasalis media"
  → PATH: nose -> nasal_meatus -> middle_nasal_meatus -> concha_nasalis_media
    MEMORY: concha_nasalis_media

- Command: "Go to sign the Spanoidalys Terminator"
  → PATH: [previous structure] -> ... -> sinus_sphenoidalis
    MEMORY: sinus_sphenoidalis

- Command: "What is nasal meatus?"
  → CLARIFY: This is an anatomical question, not a path request
    MEMORY: null
""" + memory_note

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": command}
        ]
    )
    return response.choices[0].message.content

def main():
    global memory
    print("=== Voice-Controlled Robotic System ===")
    print("Instructions:")
    print("- Press SPACE to start/stop recording")
    print("- Say 'exit' or 'quit' to terminate")
    
    def process_command():
        start_time = time.time()
        command = transcribe_audio()
        print(f"\n🗣️ Command: {command}")
        if command.lower() in ['exit', 'quit']:
            raise KeyboardInterrupt

        print("🤖 Processing...")
        response = generate_action(command)
        if response.startswith("PATH:"):
            path_line, memory_line = response.split("MEMORY:")
            print(f"Generated path: {path_line[5:].strip()}")
            new_memory = memory_line.strip()
            if new_memory.lower() != "null":
                memory["current_structure"] = new_memory
            print("Updated memory:", memory["current_structure"])
            print(f"⏱️ Total latency: {time.time() - start_time:.2f} sec")

            visualize_path(path_line[5:].strip())
        elif response.startswith("CLARIFY:"):
            reason = response[9:].strip()  # Remove "CLARIFY: " prefix
            print(f"\n⚠️ Your command needs clarification: {reason}")
            print("Please try again with more specific details.")
            print(f"⏱️ Total latency: {time.time() - start_time:.2f} sec")


    print("=== Porcupine Voice-Controlled Robot ===")
    porcupine_trigger_loop(process_command)

if __name__ == "__main__":
    main()