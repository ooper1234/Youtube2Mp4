import yt_dlp
import os
import shutil

# Check for FFmpeg
if not shutil.which("ffmpeg"):
    print("❌ FFmpeg not found. Install it and add to PATH: https://ffmpeg.org/download.html")
    exit(1)

# Ask for YouTube URL
url = input("Enter the YouTube URL: ").strip()
if not url:
    print("❌ No URL provided.")
    exit(1)

# Default to Downloads folder
default_download_folder = os.path.join(os.path.expanduser("~"), "Downloads")
output_folder = input(f"Enter folder to save the video (leave blank for Downloads folder): ").strip()
if not output_folder:
    output_folder = default_download_folder
else:
    output_folder = os.path.abspath(output_folder)

# Create folder if needed
try:
    os.makedirs(output_folder, exist_ok=True)
except Exception as e:
    print(f"❌ Error creating folder: {e}")
    exit(1)

# Fetch video info
print("🔍 Fetching video info...")
with yt_dlp.YoutubeDL({'quiet': True}) as ydl:
    try:
        info = ydl.extract_info(url, download=False)
    except Exception as e:
        print(f"❌ Failed to fetch video info: {e}")
        exit(1)

# Filter and deduplicate formats
video_formats = []
for f in info['formats']:
    if f.get('vcodec') != 'none' and f.get('acodec') == 'none' and f.get('ext') == 'mp4' and f.get('height'):
        video_formats.append(f)

# Deduplicate by height (resolution)
seen = {}
for f in sorted(video_formats, key=lambda x: (x['height'], -x.get('tbr', 0))):
    height = f['height']
    if height not in seen:
        seen[height] = f['format_id']

# List available resolutions
res_list = sorted(seen.items(), key=lambda x: x[0])  # (height, format_id)

if not res_list:
    print("❌ No MP4 video formats found.")
    exit(1)

print("\n📺 Available Resolutions:")
for i, (height, _) in enumerate(res_list, 1):
    print(f"{i}) {height}p")

# User selects resolution
choice = input("Choose resolution number: ").strip()
try:
    selected_format_id = res_list[int(choice)-1][1]
    selected_height = res_list[int(choice)-1][0]
except:
    print("❌ Invalid selection.")
    exit(1)

print(f"\n⬇️ Downloading in {selected_height}p...\n")

# Progress hook to show live status
def progress_hook(d):
    if d['status'] == 'downloading':
        percent = d.get('_percent_str', '').strip()
        speed = d.get('_speed_str', '').strip()
        eta = d.get('_eta_str', '').strip()
        total = d.get('_total_bytes_str', '') or d.get('_total_bytes_estimate_str', '')
        print(f"⏳ {percent} | {speed} | ETA: {eta} | Total: {total}", end='\r')
    elif d['status'] == 'finished':
        print("\n✅ Finished downloading. Merging...")

# yt_dlp download options
ydl_opts = {
    'format': f'{selected_format_id}+bestaudio[ext=m4a]',
    'outtmpl': os.path.join(output_folder, '%(title)s.%(ext)s'),
    'merge_output_format': 'mp4',
    'ffmpeg_location': shutil.which("ffmpeg"),
    'noplaylist': True,
    'progress_hooks': [progress_hook],
    'quiet': True,
    'no_warnings': True,
}

# Start download
try:
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])
    print(f"\n🎉 Video saved to: {output_folder}")
except Exception as e:
    print(f"❌ Download failed: {e}")
