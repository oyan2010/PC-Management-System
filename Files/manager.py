import os
import shutil
from time import sleep
# Paths and extensions
download_dir = os.path.expanduser('~/Downloads')
Photo_dir = os.path.join(download_dir, "Photos")
Video_dir = os.path.join(download_dir, "Videos")
Documents_dir = os.path.join(download_dir, "Documents")
Programming_dir = os.path.join(download_dir, "Programming Files")
Compressed_dir = os.path.join(download_dir, "Compressed")
Applications_dir = os.path.join(download_dir, "Applications")
Audio_dir = os.path.join(download_dir, "Audio")
Other_dir = os.path.join(download_dir, "Other")

image_ex = ['.jpg', '.ico', '.png', '.gif', '.jpeg', '.webp']
video_ex = ['.mp4', '.mov', '.avi','mkv']
doc_ex = ['.pdf', '.docx', '.txt', '.xlsx']
compressed_ex = ['.tar', '.zip', '.gz', '.7z', '.ace', '.ini']
application_ex = ['.exe', '.msi', '.apk','.iso'".o", ".obj", ".exe", ".dll", ".so", ".a",
    ".pyo", ".pyc"]
audio_ex = ['.mp3', '.wav', '.m4a', '.dsd','.m4a']
programming_ex = [# General Purpose Languages
    ".py", ".pyc", ".pyo", ".pyw",
    ".c", ".h",
    ".cpp", ".cc", ".cxx", ".hpp", ".hh",
    ".cs",
    ".java", ".class", ".jar",
    ".kt", ".kts",
    ".swift",
    ".go",
    ".rs",
    ".rb", ".erb",
    ".pl", ".pm", ".t",
    ".lua",
    ".dart",
    ".jl",

    # Web Development
    ".html", ".htm",
    ".css",
    ".js", ".mjs", ".cjs",
    ".ts", ".tsx",
    ".jsx",
    ".php", ".phtml", ".php3", ".php4", ".php5", ".phps",
    ".aspx", ".ascx", ".ashx",
    ".sass", ".scss",
    ".less",

    # Data & Markup Languages
    ".json",
    ".xml",
    ".yaml", ".yml",
    ".toml",
    ".csv",
    ".ini",
    ".sql",

    # Scripts & Shell
    ".sh", ".bash", ".zsh",
    ".bat", ".cmd",
    ".ps1", ".psm1",
    ".mk",  # Makefile usually has no extension
    "Dockerfile",
    ".vbs",

    # Notebooks & Configs
    ".ipynb",
    ".conf", ".cfg", ".env",
    ".log",

    # Build & Project Files
    "CMakeLists.txt", ".cmake",
    ".gradle",
    "pom.xml",
    "package.json",
    ".code-workspace"]

# Ensure target folders exist
os.makedirs(Photo_dir, exist_ok=True)
os.makedirs(Video_dir, exist_ok=True)
os.makedirs(Documents_dir, exist_ok=True)
os.makedirs(Compressed_dir, exist_ok=True)
os.makedirs(Applications_dir, exist_ok=True)
os.makedirs(Audio_dir, exist_ok=True)
os.makedirs(Programming_dir, exist_ok=True)
os.makedirs(Other_dir, exist_ok=True)

# File manager function
def manager():
    all_files = os.listdir(download_dir)  # Re-scan each time
    for file_name in all_files:
        file_path = os.path.join(download_dir, file_name)

        # Skip directories and incomplete files
        if os.path.isdir(file_path) or file_name.startswith("~"):
            continue

        # Get the file extension
        ext = os.path.splitext(file_name)[1].lower()

        # Determine the destination folder
        if ext in image_ex:
            target_folder = Photo_dir
        elif ext in video_ex:
            target_folder = Video_dir
        elif ext in doc_ex:
            target_folder = Documents_dir
        elif ext in compressed_ex:
            target_folder = Compressed_dir
        elif ext in application_ex:
            target_folder = Applications_dir
        elif ext in audio_ex:
            target_folder = Audio_dir
        elif ext in programming_ex:
            target_folder = Programming_dir
        else:
            target_folder = Other_dir

        # Check if file already exists in target folder and rename if necessary
        target_file_path = os.path.join(target_folder, file_name)
        if os.path.exists(target_file_path):
            name, ext = os.path.splitext(file_name)
            file_name = f"{name}_Copy{ext}"
            target_file_path = os.path.join(target_folder, file_name)

        try:
            shutil.move(file_path, target_file_path)
            sleep(2)  # Wait for 2 seconds after moving the file
        except Exception as e:
            print(f"Error occurred while moving {file_name}: {e}")

# Call the manager function to start the process
