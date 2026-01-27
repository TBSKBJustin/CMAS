# Quick Start Guide

## Installation

### 1. Setup Python Environment

```bash
cd /path/to/church-media-automation

# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install Python dependencies
pip install -r requirements.txt
```

### 2. Install System Dependencies

Run the interactive setup:

```bash
python utils/dependency_manager.py setup
```

This will:
- ✓ Check for FFmpeg, whisper.cpp, Ollama, OBS
- ✓ Guide you through installing missing tools
- ✓ Help download Whisper models

Or check manually:

```bash
python utils/dependency_manager.py check
```

### 3. Frontend Setup

```bash
cd frontend
npm install
```

### 4. Configuration

```bash
# Copy example configuration (optional)
cp config/config.yaml config/config.local.yaml
```

Edit if needed:
- Set OBS recording folder path
- Configure asset paths
- Add YouTube credentials

### 5. Add Assets

```bash
# Add your church assets
cp your-background.jpg assets/backgrounds/
cp your-logo.png assets/logos/
cp pastor-photo.png assets/pastor/
```

## Running the System

### Option 1: Web Interface (Recommended)

**Terminal 1 - API Server:**
```bash
python api_server.py
```

**Terminal 2 - Frontend:**
```bash
cd frontend
npm run dev
```

Open http://localhost:3000 in your browser.

### Option 2: Command Line

```bash
# Create an event
python -c "
from controller.event_manager import EventManager
manager = EventManager()
event_id = manager.create_event(
    title='Sunday Service',
    speaker='Pastor John',
    scripture='John 3:16'
)
print(f'Created: {event_id}')
"

# Run workflow
python controller/workflow_controller.py run --event <event-id>
```

## Module-by-Module Testing

### Test thumbnail generation
```bash
python modules/thumbnail/composer_pillow.py \
  --title "Miracles and Wonders" \
  --scripture "Acts 15:12" \
  --output test_thumbnail.jpg
```

### Test subtitle generation
```bash
python modules/subtitles/engine_whispercpp.py \
  --video /path/to/video.mp4 \
  --output-dir ./output \
  --model models/ggml-base.bin
```

### Test YouTube upload (requires credentials)
```bash
python modules/publish/youtube_uploader.py \
  --video /path/to/video.mp4 \
  --title "Sunday Service" \
  --description "..." \
  --thumbnail thumbnail.jpg
```

## Common Workflows

### Typical Sunday Service
1. Create event with full metadata
2. Let OBS monitor detect recording OR manually attach video
3. Enable: thumbnail, subtitles, YouTube, website
4. Run workflow
5. Review outputs
6. Publish

### Youth Meeting (Quick Upload)
1. Create event
2. Manually attach video
3. Enable: subtitles, YouTube only
4. Run workflow

### Re-run with Better AI
1. Select existing event
2. Disable all modules except thumbnail_ai + thumbnail_compose
3. Run again (it will regenerate thumbnail only)

## Troubleshooting

### Video not found
- Check that video file path is correct
- Ensure file has proper permissions

### Subtitle generation fails
- Ensure ffmpeg is installed: `brew install ffmpeg`
- Check whisper.cpp model path
- Try fallback to audio extraction

### Thumbnail looks wrong
- Verify asset paths in config
- Check that fonts are installed
- Ensure images are correct dimensions

### YouTube upload fails
- Verify credentials file exists
- Check OAuth token is valid
- Ensure video meets YouTube requirements

## Next Steps

- Set up OBS monitor for automatic detection
- Configure YouTube API credentials
- Set up website git repository
- Create custom profiles for different event types
- Explore module replacements (WhisperX, different AI generators, etc.)

For more details, see the main README.md
