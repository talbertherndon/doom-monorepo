import requests
import os
import uuid
import sys
import glob
import json
import re
import csv
import shutil
try:
    import pyktok as pyk
except ImportError:
    print("PyKTok not installed. Installing...")
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "pyktok"])
    import pyktok as pyk

invoke_url = "https://ai.api.nvidia.com/v1/vlm/nvidia/vila"
stream = False
query = '''
"You are an AI assistant providing **concept-driven video summaries** designed for integration into a Graph RAG database. "
    "Your task is to **extract and synthesize key themes, cognitive patterns, and conceptual relationships** from the video while ensuring that dialogue, if present, is incorporated when meaningful.\n\n"

    "**🔹 Summary Requirements:**\n"
    "- Identify and articulate the **main topics, symbolic themes, and underlying cognitive patterns** presented in the video.\n"
    "- Capture **essential spoken dialogue when relevant**, prioritizing statements that shape the video's conceptual significance.\n"
    "- Focus on **neurosymbolic insights, emergent motifs, and systemic relationships** rather than surface-level descriptions of people or visuals.\n"
    "- Detect and highlight **recurring symbolic structures, behavioral cues, and decision-making frameworks** conveyed in the content.\n"
    "- If dialogue contributes to meaning, integrate it in a way that enriches semantic analysis and conceptual understanding.\n"
    "- Avoid unnecessary references to personal attributes (e.g., gender, pronouns) unless explicitly relevant to the content.\n"
    "- **Do not use generic labels like 'the speaker' or 'the person' unless their identity is contextually important.**\n"
    "- Maintain a **natural, coherent narrative format** rather than structured bullet points.\n\n"

    "**🔹 Additional Research-Oriented Insights:**\n"
    "- Map **aesthetic preferences, behavioral patterns, and social reinforcement loops** reflected in the video's themes.\n"
    "- Analyze **how symbolic representations connect to broader cognitive biases, social media trends, or algorithmic influences**.\n"
    "- Identify potential **predictive indicators** that could inform future aesthetic shifts or behavioral tendencies.\n"
    "- Capture insights that support **multi-modal analysis**, linking visual, textual, and conceptual elements for cross-modal reasoning.\n\n"

    "Ensure each response delivers a **concise yet multi-layered conceptual summary**, optimizing it for retrieval, neuro-symbolic reasoning, and knowledge graph expansion in a 3D Graph RAG system."
'''
kApiKey = "NVAPI_KEY"
# API key
kNvcfAssetUrl = "https://api.nvcf.nvidia.com/v2/nvcf/assets"
# ext: {mime, media}
kSupportedList = {
    "png": ["image/png", "img"],
    "jpg": ["image/jpg", "img"],
    "jpeg": ["image/jpeg", "img"],
    "mp4": ["video/mp4", "video"],
}

def get_extention(filename):
    _, ext = os.path.splitext(filename)
    ext = ext[1:].lower()
    return ext

def mime_type(ext):
    return kSupportedList[ext][0]
def media_type(ext):
    return kSupportedList[ext][1]

def _upload_asset(media_file, description):
    ext = get_extention(media_file)
    assert ext in kSupportedList
    data_input = open(media_file, "rb")
    headers={
        "Authorization": f"Bearer {kApiKey}",
        "Content-Type": "application/json",
        "accept": "application/json",
    }
    assert_url = kNvcfAssetUrl
    authorize = requests.post(
        assert_url,
        headers = headers,
        json={"contentType": f"{mime_type(ext)}", "description": description},
        timeout=30,
    )
    authorize.raise_for_status()

    authorize_res = authorize.json()
    print(f"uploadUrl: {authorize_res['uploadUrl']}")
    response = requests.put(
        authorize_res["uploadUrl"],
        data=data_input,
        headers={
            "x-amz-meta-nvcf-asset-description": description,
            "content-type": mime_type(ext),
        },
        timeout=300,
    )

    response.raise_for_status()
    if response.status_code == 200:
        print(f"upload asset_id {authorize_res['assetId']} successfully!")
    else:
        print(f"upload asset_id {authorize_res['assetId']} failed.")
    return uuid.UUID(authorize_res["assetId"])

def _delete_asset(asset_id):
    headers = {
        "Authorization": f"Bearer {kApiKey}",
    }
    assert_url = f"{kNvcfAssetUrl}/{asset_id}"
    response = requests.delete(
        assert_url, headers=headers, timeout=30
    )
    response.raise_for_status()

def chat_with_media_nvcf(infer_url, media_files, query: str, stream: bool = False):
    asset_list = []
    ext_list = []
    media_content = ""
    assert isinstance(media_files, list), f"{media_files}"
    print("uploading {media_files} into s3")
    has_video = False
    for media_file in media_files:
        ext = get_extention(media_file)
        assert ext in kSupportedList, f"{media_file} format is not supported"
        if media_type(ext) == "video":
            has_video = True
        asset_id = _upload_asset(media_file, "Reference media file")
        asset_list.append(f"{asset_id}")
        ext_list.append(ext)
        media_content += f'<{media_type(ext)} src="data:{mime_type(ext)};asset_id,{asset_id}" />'
    if has_video:
        assert len(media_files) == 1, "Only single video supported."
    asset_seq = ",".join(asset_list)
    print(f"received asset_id list: {asset_seq}")
    headers = {
        "Authorization": f"Bearer {kApiKey}",
        "Content-Type": "application/json",
        "NVCF-INPUT-ASSET-REFERENCES": asset_seq,
        "NVCF-FUNCTION-ASSET-IDS": asset_seq,
        "Accept": "application/json",
    }
    if stream:
        headers["Accept"] = "text/event-stream"
    response = None

    messages = [
        {
            "role": "user",
            "content": f"{query} {media_content}",
        }
    ]
    payload = {
        "max_tokens": 1024,
        "temperature": 0.2,
        "top_p": 0.7,
        "seed": 50,
        'num_frames_per_inference': 8,
        "messages": messages,
        "stream": stream,
        "model": "nvidia/vila",
    }

    response = requests.post(infer_url, headers=headers, json=payload, stream=stream)
    result = ""
    if stream:
        for line in response.iter_lines():
            if line:
                line_text = line.decode("utf-8")
                print(line_text)
                result += line_text + "\n"
    else:
        response_json = response.json()
        print(response_json)
        # Extract the text content from the response
        if 'choices' in response_json and len(response_json['choices']) > 0:
            result = response_json['choices'][0]['message']['content']
        else:
            result = str(response_json)

    print(f"deleting assets: {asset_list}")
    for asset_id in asset_list:
        _delete_asset(asset_id)
    
    return result

def get_tiktok_metadata(url):
    """Fetches metadata from a TikTok video URL."""
    try:
        video_json = pyk.alt_get_tiktok_json(url)
        metadata = video_json.get('__DEFAULT_SCOPE__', {}).get('webapp.video-detail', {}).get('shareMeta', None)

        if not metadata:
            return None

        return metadata

    except Exception as e:
        print(f"Error fetching TikTok metadata: {e}")
        return None

def extract_tiktok_id_from_filename(filename):
    """Extract TikTok video ID from filename."""
    # Assuming filenames follow pattern like "share_video_7462823628783095047_.mp4"
    match = re.search(r'share_video_(\d+)_', filename)
    if match:
        return match.group(1)
    return None

def get_tiktok_url_from_id(video_id):
    """Construct TikTok URL from video ID."""
    if not video_id:
        return None
    return f"https://www.tiktok.com/@user/video/{video_id}"

def save_to_csv(file_path, payload):
    """Appends data to a CSV file, creating it if it doesn't exist."""
    os.makedirs(os.path.dirname(file_path), exist_ok=True)  # Ensure the directory exists

    file_exists = os.path.isfile(file_path)  # Check if the file exists

    # Extract field names from the payload (assuming payload is a dictionary)
    field_names = list(payload.keys())

    # Open the file in append mode and write data
    with open(file_path, mode="a", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=field_names)

        if not file_exists:
            writer.writeheader()  # Write header only if file does not exist

        writer.writerow(payload)  # Append new row

    print(f" Data saved to {file_path}")

def export_text_to_csv():
    """Process the tiktok_descriptions.txt file and convert to CSV format."""
    txt_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "tiktok_descriptions.txt")
    csv_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "tiktok_descriptions.csv")
    
    # Remove existing CSV file if it exists to avoid duplicated entries
    if os.path.exists(csv_file):
        os.remove(csv_file)
    
    if not os.path.exists(txt_file):
        print(f"Text file {txt_file} not found.")
        return
    
    with open(txt_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Split the content by video entries (each starts with "--- share_video...")
    video_entries = re.split(r'\n\n--- share_video_', content)
    if video_entries[0].strip() == '':
        video_entries = video_entries[1:]  # Remove empty first entry if exists
    else:
        # Fix the first entry if it doesn't start with the marker
        video_entries[0] = video_entries[0].lstrip('\n')
        if not video_entries[0].startswith('--- share_video_'):
            video_entries[0] = '--- share_video_' + video_entries[0]
    
    # Process each entry
    for entry in video_entries:
        if not entry.strip():
            continue
            
        # Reattach the prefix that was removed in the split
        if not entry.startswith('--- share_video_'):
            entry = '--- share_video_' + entry
            
        # Extract metadata
        title_match = re.search(r'Title: (.+?)\n', entry)
        desc_match = re.search(r'Description: (.+?)\n', entry)
        source_match = re.search(r'Source: (.+?)\n', entry)
        
        # Extract video analysis (everything after "Video Analysis:" until the next entry or end of text)
        analysis_match = re.search(r'Video Analysis:\n(.*?)(?=\n\n---|$)', entry, re.DOTALL)
        
        # Prepare payload with only the requested fields
        payload = {
            'analysis': analysis_match.group(1).strip() if analysis_match else 'N/A',
            'title': title_match.group(1) if title_match else 'N/A',
            'description': desc_match.group(1) if desc_match else 'N/A',
            'source': source_match.group(1) if source_match else 'N/A'
        }
        
        # Save to CSV
        save_to_csv(csv_file, payload)
    
    print(f"Exported data from {txt_file} to {csv_file}")

def process_videos_folder():
    # Create videos folder if it doesn't exist
    videos_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "videos")
    
    # Ensure videos directory exists
    os.makedirs(videos_dir, exist_ok=True)
    
    # Define the single output file
    output_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "tiktok_descriptions.txt")
    
    # Find all video files in the videos folder
    video_files = []
    for ext in ["mp4"]:  # Add other video formats if needed
        pattern = os.path.join(videos_dir, f"*.{ext}")
        video_files.extend(glob.glob(pattern))
    
    if not video_files:
        print(f"No video files found in {videos_dir}")
        return
    
    print(f"Found {len(video_files)} video files to process")
    
    # Process each video file and append to a single file
    for video_file in video_files:
        filename = os.path.basename(video_file)
        print(f"Processing video: {filename}")
        
        # Try to get TikTok metadata if available
        tiktok_id = extract_tiktok_id_from_filename(filename)
        tiktok_metadata = None
        if tiktok_id:
            tiktok_url = get_tiktok_url_from_id(tiktok_id)
            if tiktok_url:
                print(f"Fetching TikTok metadata for video ID: {tiktok_id}")
                tiktok_metadata = get_tiktok_metadata(tiktok_url)
        
        # Process the video and get the description
        result = chat_with_media_nvcf(invoke_url, [video_file], query, stream)
        
        # Append the description to the single output file
        with open(output_file, "a", encoding="utf-8") as f:
            f.write(f"\n\n--- {filename} ---\n\n")
            
            # Include TikTok metadata if available
            if tiktok_metadata:
                f.write("TikTok Metadata:\n")
                f.write(f"Title: {tiktok_metadata.get('title', 'N/A')}\n")
                f.write(f"Description: {tiktok_metadata.get('desc', 'N/A')}\n")
                f.write(f"Author: {tiktok_metadata.get('author', 'N/A')}\n")
                f.write(f"Source: {tiktok_url}\n")
                f.write("\nVideo Analysis:\n")
            
            f.write(result)
        
        print(f"Appended description for {filename} to {output_file}")
    
    # After processing all videos, export to CSV
    export_text_to_csv()

def download_tiktok_videos():
    """Download TikTok videos from Favorite_Videos.txt to the videos folder."""
    # Define the input and output paths
    favorites_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "Favorite_Videos.txt")
    videos_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "videos")
    
    # Ensure videos directory exists
    os.makedirs(videos_dir, exist_ok=True)
    
    if not os.path.exists(favorites_file):
        print(f"Favorites file {favorites_file} not found.")
        return False
    
    # Read the favorites file
    with open(favorites_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Extract dates and links using regex
    pattern = r"Date:\s(.+?)\nLink:\s(.+)"
    videos = re.findall(pattern, content)
    
    if not videos:
        print("No videos found in the favorites file.")
        return False
    
    print(f"Found {len(videos)} videos to download.")
    
    # Change to the videos directory as the working directory
    original_dir = os.getcwd()
    os.chdir(videos_dir)
    
    # Download each video
    for date, url in videos:
        print(f"Processing URL: {url} (Date: {date})")
        try:
            # Extract video ID from the URL if possible
            video_id = None
            if "video/" in url:
                video_id = url.split("video/")[-1].strip("/")
            
            if video_id:
                # Check if video already exists in the videos folder
                existing_file = glob.glob(f"share_video_{video_id}_*")
                if existing_file:
                    print(f"Video {video_id} already exists: {existing_file[0]}")
                    continue
            
            # Download the video - use None for directory to use current directory
            print(f"Downloading: {url}")
            video = pyk.save_tiktok(url, True, 'video_data.csv', None, True)
            if not video or 'video_fn' not in video:
                print(f"❌ Error: Video download failed for {url}")
                continue
            
            video_file = video['video_fn']
            print(f"✅ Downloaded: {video_file}")
            
        except Exception as e:
            print(f"⚠️ Exception downloading {url}: {e}")
    
    # Change back to the original directory
    os.chdir(original_dir)
    
    print("Video download process completed.")
    return True

if __name__ == "__main__":
    """ First download TikTok videos from Favorite_Videos.txt,
        then process all videos in the 'videos' folder and 
        save descriptions to text and CSV files.
        
        Alternative usage with direct file arguments:
        python VLMapitest.py sample.mp4
    """
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "--export-csv-only":
            # Just export existing text file to CSV
            export_text_to_csv()
        else:
            # Process specific video files
            media_samples = list(sys.argv[1:])
            chat_with_media_nvcf(invoke_url, media_samples, query, stream)
    else:
        # Default workflow: skip downloading and just process videos
        # print("Step 1: Downloading TikTok videos from favorites file...")
        # download_tiktok_videos()  # Skip video downloading step
        
        print("Processing videos from the videos folder...")
        process_videos_folder()
