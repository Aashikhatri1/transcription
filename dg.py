# connecting to mongo for status
from deepgram import Deepgram
import asyncio, os, sys, shutil
from pymongo import MongoClient
from dotenv import load_dotenv
load_dotenv()
# Your Deepgram API Key
DEEPGRAM_API_KEY = os.environ.get('DEEPGRAM_API_KEY')

# MongoDB setup
MONGO_DB_URI = os.environ.get("MONGO_DB_URI")
MONGO_DB_NAME = os.environ.get("MONGO_DB_NAME")
MONGO_DB_COLLECTION = os.environ.get("MONGO_DB_COLLECTION")

# Folders for storing recordings and transcripts
FOLDER_PATH = 'recordings'
TRANSCRIPTIONS_FOLDER = 'transcriptions'
COMPLETED_FOLDER = 'recordings_processed'

# Function to save transcript to text file in the transcriptions folder
def save_transcript(filename, transcript):
    if not os.path.exists(TRANSCRIPTIONS_FOLDER):
        os.makedirs(TRANSCRIPTIONS_FOLDER)
    with open(os.path.join(TRANSCRIPTIONS_FOLDER, f"{filename}.txt"), "w") as file:
        file.write(transcript)

# Function to move the processed audio file
def move_processed_file(filename):
    if not os.path.exists(COMPLETED_FOLDER):
        os.makedirs(COMPLETED_FOLDER)
    shutil.move(os.path.join(FOLDER_PATH, filename), os.path.join(COMPLETED_FOLDER, filename))

# Function to update MongoDB entry
def update_mongodb_entry(filename, client):
    db = client[MONGO_DB_NAME]
    collection = db[MONGO_DB_COLLECTION]
    result = collection.update_one({'file_name': filename}, {'$set': {'status': 'processed'}})
    print(f"Updated MongoDB entry for {filename}: {result.modified_count} document(s) updated.")

# Async main function
async def main():
    deepgram = Deepgram(DEEPGRAM_API_KEY)
    client = MongoClient(MONGO_DB_URI)

    # Iterating over each file in the folder
    for filename in os.listdir(FOLDER_PATH):
        if filename.endswith('.wav'):  # Check if the file is a WAV file
            file_path = os.path.join(FOLDER_PATH, filename)
            print(f"Transcribing {filename}...")

            with open(file_path, 'rb') as audio:
                source = {
                    'buffer': audio,
                    'mimetype': 'audio/wav'
                }

                try:
                    # Sending the audio for transcription
                    response = await asyncio.create_task(
                        deepgram.transcription.prerecorded(
                            source,
                            {'smart_format': True}
                        )
                    )

                    # Extracting the transcript
                    transcript = response["results"]["channels"][0]["alternatives"][0]["transcript"]

                    # Saving the transcript
                    save_transcript(os.path.splitext(filename)[0], transcript)

                    # Move the processed file
                    move_processed_file(filename)

                    # Update MongoDB entry
                    update_mongodb_entry(filename, client)

                except Exception as e:
                    print(f"Error transcribing {filename}: {e}")

    client.close()

try:
    asyncio.run(main())
except Exception as e:
    exception_type, exception_object, exception_traceback = sys.exc_info()
    line_number = exception_traceback.tb_lineno
    print(f'line {line_number}: {exception_type} - {e}')
