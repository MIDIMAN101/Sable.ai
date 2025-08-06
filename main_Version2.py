import os
from google.cloud import storage
from googleapiclient.discovery import build
import vertexai
from vertexai.generative_models import GenerativeModel

# --- CONFIGURATION ---
DRIVE_FOLDER_ID = '1wcbvLrSl3fNyLxGWUwNKs6eeqndvIz1f' 
BUCKET_NAME = 'sableai'
PROJECT_ID = 'sable-ai-468204'
REGION = 'australia-southeast2' # Or another region where Vertex AI is available

# --- MAIN FUNCTION ---
def orchestrator(request):
    """The main entry point for the Cloud Function."""
    
    # Initialize the clients
    storage_client = storage.Client()
    drive_service = build('drive', 'v3')
    vertexai.init(project=PROJECT_ID, location=REGION)
    model = GenerativeModel("gemini-pro")

    bucket = storage_client.get_bucket(BUCKET_NAME)

    try:
        # Get list of files from Google Drive
        print(f"Accessing Google Drive folder: {DRIVE_FOLDER_ID}")
        results = drive_service.files().list(q=f"'{DRIVE_FOLDER_ID}' in parents").execute()
        items = results.get('files', [])

        if not items:
            return "No files found in the folder.", 200

        for item in items:
            file_id = item['id']
            file_name = item['name']
            
            print(f"Processing file: {file_name}")

            # 1. Download file content from Google Drive
            file_content = drive_service.files().get(fileId=file_id, supportsAllDrives=True).execute()

            # 2. Upload the file to Cloud Storage (optional but good practice)
            blob = bucket.blob(file_name)
            blob.upload_from_string(file_content)

            # --- Simplified Music Analysis (Placeholder) ---
            # NOTE: This is NOT real musical analysis. It's a placeholder.
            # In a real system, a custom model would analyze the file and generate this data.
            simplified_analysis = {
                "genre": "Extreme Metal/Hardcore",
                "tempo": "Fast, aggressive",
                "mood": "Chaotic, visceral",
                "vocal_sections": [
                    {"start": "0:30", "end": "0:55", "notes": "Build-up leading to a breakdown."},
                    {"start": "1:20", "end": "1:40", "notes": "Fast-paced, relentless section."}
                ]
            }

            # 3. Create the prompt for the generative AI
            prompt = f"""
            You are a professional extreme metal lyricist and vocal coach.
            Here is a simplified musical analysis of an instrumental track:
            Genre: {simplified_analysis['genre']}
            Tempo: {simplified_analysis['tempo']}
            Mood: {simplified_analysis['mood']}
            Vocal Sections:
            {simplified_analysis['vocal_sections']}
            
            The lyrical themes are: "carnage in the moshpit," "draw blood," and "bliss in the copper taste."
            The vocal style should emulate a collaboration between Aiden from Dealer and Damien from Diesect.
            
            Write a lyrical draft for this song, matching the described musical sections.
            For each vocal segment, include the start and end timestamps and a description of the vocal delivery.
            """

            # 4. Call the Generative AI Model
            print(f"Sending prompt to Gemini for lyric generation...")
            response = model.generate_content(prompt)
            
            # 5. Print the result (this will appear in the Cloud Function logs)
            print(f"\n--- Lyrics for {file_name} ---\n")
            print(response.text)
            print("\n--------------------------\n")
            
        return "Lyric generation process completed for all files.", 200
    
    except Exception as e:
        print(f"An error occurred: {e}")
        return str(e), 500