# Events Directory

This directory stores all event data, including inputs, outputs, and logs.

## Structure

Each event gets its own directory with the following structure:

```
events/
└── 2026-01-26_0900_sunday-service/
    ├── event.json          # Event configuration and metadata
    ├── input/              # Input media files
    │   └── recording.mp4
    ├── output/             # Generated outputs
    │   ├── thumbnail.jpg
    │   ├── subtitles.srt
    │   └── subtitles.vtt
    └── logs/               # Module execution logs
        ├── thumbnail_ai_result.json
        ├── subtitles_result.json
        └── workflow_state.json
```

## Event Naming Convention

Events are named using the pattern: `YYYY-MM-DD_HHMM_slug`

Examples:
- `2026-01-26_0900_sunday-service`
- `2026-01-26_1300_youth`
- `2026-01-26_1900_bible-study`

## Event Configuration

Each `event.json` contains:
- Event metadata (title, speaker, scripture, etc.)
- Module toggles (which steps to run)
- Input file references
- Timestamps and status information

See the main README for example event.json structure.
