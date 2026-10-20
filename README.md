# Oayan AI PC Manager & System Utility 💻

A desktop management application built with **PyQt6** providing an all-in-one suite for system optimization, file conversions, media processing, and archive management.

---

## 🚀 Features

- **Media & File Conversion**: Convert videos, audio, images, and documents across various formats powered by `ffmpeg-python` and `Pillow`.
- **Archive Operations**: Compress, extract, and split archives (`.zip`, `.7z`) effortlessly using `py7zr`.
- **System Cleanup & Maintenance**:
  - One-click temporary file cleanup (`temp_clr`).
  - Automated maintenance and Recycle Bin cleanout.
- **Multithreaded Execution**: Fast asynchronous processing with `QThread` ensuring smooth, responsive UI interactions without freezes.
- **Sleek Modern UI**: Custom dark theme styled with clean gradients and typography.

---

## 🛠️ Installation & Setup

1. **Clone the repository**:
   ```bash
   git clone https://github.com/oyan2010/PC-Management-System.git
   cd PC-Management-System
   ```

2. **Set up a virtual environment (optional but recommended)**:
   ```bash
   python -m venv venv
   # On Windows:
   venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **FFmpeg requirement**:
   Make sure [FFmpeg](https://ffmpeg.org/download.html) is installed and available in your system `PATH`.

5. **Run the Application**:
   ```bash
   python main.py
   ```

---

## 📦 Tech Stack

- **GUI Framework**: PyQt6
- **Image Processing**: Pillow (PIL)
- **Media Engine**: FFmpeg
- **Compression**: py7zr, zipfile
- **Language**: Python 3.10+
