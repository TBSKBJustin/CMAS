# Installation Guide

## Prerequisites

- Python 3.8 or higher
- Node.js 18 or higher
- Git

## Step 1: Clone the Repository

```bash
git clone <repository-url>
cd church-media-automation
```

## Step 2: Python Dependencies

```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate  # On macOS/Linux
# or
venv\Scripts\activate  # On Windows

# Install Python packages
pip install -r requirements.txt
pip install fastapi uvicorn[standard] pydantic
```

## Step 3: Check and Install System Dependencies

The system includes an interactive dependency manager that will check for required tools and help you install them:

```bash
python utils/dependency_manager.py setup
```

This will:
1. Check if FFmpeg, whisper.cpp, Ollama, and OBS are installed
2. Prompt you to install missing dependencies
3. Guide you through downloading Whisper models

### Manual Installation (if needed)

#### FFmpeg (Required)
```bash
# macOS
brew install ffmpeg

# Ubuntu/Debian
sudo apt-get install ffmpeg

# Windows
# Download from https://ffmpeg.org/download.html
```

#### whisper.cpp (Recommended for subtitles)
```bash
# macOS
brew install whisper-cpp

# Linux
git clone https://github.com/ggerganov/whisper.cpp
cd whisper.cpp
make

# Download a model
./models/download-ggml-model.sh base
```

#### Ollama (Optional, for AI character generation)
```bash
# macOS
brew install ollama

# Linux
curl -fsSL https://ollama.com/install.sh | sh

# After installation
ollama pull llama2
```

#### OBS Studio (Optional, for recording)
```bash
# macOS
brew install --cask obs

# Ubuntu/Debian
sudo apt-get install obs-studio

# Windows
# Download from https://obsproject.com/download
```

## Step 4: Frontend Setup

```bash
cd frontend
npm install
```

## Step 5: Configuration

```bash
# Copy example configuration
cp config/config.yaml config/config.local.yaml

# Edit configuration (optional)
nano config/config.local.yaml
```

Update paths in the configuration:
- OBS recording folder path
- Asset paths
- YouTube credentials (if using)
- Website repository path (if using)

## Step 6: Add Assets

Place your church-specific assets:

```bash
# Background images for thumbnails
cp your-background.jpg assets/backgrounds/

# Church logo
cp your-logo.png assets/logos/

# Pastor portraits
cp pastor-photo.png assets/pastor/

# Fonts
cp your-font-bold.ttf assets/fonts/bold.ttf
cp your-font-regular.ttf assets/fonts/regular.ttf
```

## Step 7: Start the System

### Terminal 1: Start API Server
```bash
source venv/bin/activate  # If not already activated
python api_server.py
```

The API will be available at http://localhost:5000

### Terminal 2: Start Frontend
```bash
cd frontend
npm run dev
```

The web interface will be available at http://localhost:3000

## Verification

1. Open http://localhost:3000 in your browser
2. Check the Dependencies page - all required tools should show as "Installed"
3. Create a test event to verify the system is working

## Troubleshooting

### Port already in use
If port 5000 or 3000 is already in use:

**API Server:**
```bash
python api_server.py --port 5001
```

**Frontend:**
Edit `frontend/vite.config.js` and change the port number.

### Dependencies not detected
Run the dependency checker manually:
```bash
python utils/dependency_manager.py check
```

### Whisper model not found
Download models manually:
```bash
mkdir -p models
cd models
wget https://huggingface.co/ggerganov/whisper.cpp/resolve/main/ggml-base.bin
```

### Frontend build errors
```bash
cd frontend
rm -rf node_modules package-lock.json
npm install
```

## Next Steps

- Read the [Quick Start Guide](QUICKSTART.md) for usage examples
- Configure YouTube API credentials (see config/youtube_credentials.example.json)
- Set up OBS for automatic recording detection
- Explore the web interface and create your first event!
