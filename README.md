# ⛪ Church Media Automation System

A modular, “LEGO-style” media workflow for churches: recording/streaming → thumbnail → subtitles → publishing.

This project is pipeline-first and replaceable-by-design: swap modules (subtitle engine, AI models, publishers) without rewriting the system.

## Quick Start

1. Install dependencies (guided):

```bash
python utils/dependency_manager.py setup
```

2. Start the API server:

```bash
python api_server.py
```

3. Start the frontend (separate terminal):

```bash
cd frontend
npm install
npm run dev
```

Open the web UI at http://localhost:3000

---

**Core concepts**

- Events: each run is an event (metadata + module toggles + inputs/outputs)
- Modules: small, single-purpose plugins (subtitles, thumbnails, uploads)
- Files + JSON: modules exchange data via standard JSON inputs and file-based outputs

---

## System Requirements

Required:
- Python 3.8+
- FFmpeg
- Node.js 18+

Optional (enhanced features):
- whisper.cpp (local ASR models)
- Ollama (local LLM for subtitle correction / summaries / image prompts)
- OBS Studio (if using OBS monitor ingestion)

The project auto-detects missing dependencies and helps guide installation.

---

## Project layout (high level)

See the repository root for details; main folders:

- `frontend/` — React app and UI
- `controller/` — workflow orchestrator and event manager
- `modules/` — plugin implementations (subtitles, thumbnail, publish, ingest)
- `utils/` — dependency manager and helpers
- `events/` — generated event folders (input/output/logs)
- `config/` — YAML configuration

Key files: `api_server.py`, `controller/workflow_controller.py`, `modules/subtitles/engine_whispercpp.py`, `modules/content/ai_processor.py`.

---

## Typical user flow

1. Create an event (title, speaker, time)
2. Enable required modules (subtitles, thumbnail, publish)
3. Add or auto-detect video input (OBS monitor or manual)
4. Run workflow
5. Review outputs and publish

---

## Subtitles: fixes & best practices

This project uses `whisper.cpp` by default (fast local ASR). Recent fixes and recommendations:

1) Model path handling
- Model paths are resolved to absolute paths to avoid relative-path failures when the API server runs from a different cwd.

2) File name sanitization
- Filenames with spaces are normalized (spaces → underscores) before calling CLI tools to avoid shell parsing issues.

3) Fallback behavior
- The subtitle engine will try direct video input, then fall back to audio extraction if needed.

How to verify:

```bash
# check whisper-cli and model
/path/to/whisper-cli -m /absolute/path/to/ggml-base.bin --help

# look for generated subtitles
ls -lh events/NEW_EVENT_ID/output/*.srt
```

---

## Subtitle segmentation (controls)

New subtitle settings are exposed in the Event Create UI:

- `Max Characters per Line` (recommended defaults: 60–84 for English, 40–60 for Chinese)
- `Split on Word Boundaries` (avoid splitting words mid-token)

Practical recommendations:

- YouTube / desktop: 60–84 chars
- Mobile: 40–60 chars
- Technical content: 60–70 chars

CLI / whisper options supported:

- `--max-len N` — max characters per subtitle segment
- `-sow` / `--split-on-word` — split on word boundaries

Adjust settings per-event and re-run the workflow to test results.

---

## Language & model selection

Event creation UI lets you choose:

- Language (Auto / en / zh / es / fr / de / ja / ko / pt / ru / ar / hi ...)
- Whisper model (tiny / base / small / medium / large-v3)

Trade-offs:

- Tiny: fastest, lowest quality
- Base: recommended for everyday use
- Small/Medium: higher quality, slower
- Large-v3: highest quality, slowest and largest download

If a model is not available locally, the system can prompt you to download it (or use `../whisper.cpp/download-ggml-model.sh`).

---

## whisper.cpp connection checks

Quick checks and troubleshooting:

- Ensure `whisper-cli` binary is executable and configured in `config/config.yaml` under `modules.subtitles.whispercpp.whisper_bin`.
- Copy required `.bin` model files into `models/` or set `modules.subtitles.whispercpp.model_path` to an absolute path.
- Verify ffmpeg is installed and in `$PATH`.

Run the included test:

```bash
python test_whisper_connection.py
```

Expected outputs: `CST-xxx_Final.srt` or similar in `events/NEW_EVENT_ID/output/` and log lines showing model path and whisper-cli invocation.

---

## AI content (Ollama) — subtitle correction & summaries

If Ollama is available at `http://localhost:11434`, the system can:

- Post-process generated `.srt` to correct punctuation, timing edge-cases, and formatting
- Produce a short summary of the sermon / talk as a `.txt` alongside the corrected `.srt`

These features are optional and controlled per-event via `ai_content` module settings.

---

## Developer notes

- Modules follow a simple contract: JSON input → produce files + result JSON
- Use `controller/workflow_controller.py` to trace runs and inspect logs
- Frontend calls the API endpoints to list available Whisper and Ollama models; the UI populates selects dynamically

---

## Troubleshooting checklist

- Server logs: the API server prints processing steps and applied subtitle settings
- Filenames: ensure input video filenames are accessible and do not contain problematic characters (spaces are normalized by the system)
- Models: verify `models/` contains required `.bin` files
- FFmpeg: run `ffmpeg -version` to confirm installation

---

## Where to get help

File issues in the repo, or inspect `events/` logs for detailed errors. If you want, I can run tests or merge additional documentation sections.

---

## A note about documentation consolidation

This README now contains consolidated guidance (installation, quick start, subtitle tips, model selection, and connection checks). Redundant top-level docs have been removed from the repository to reduce duplication.

---

## License

Apache-2.0 - see LICENSE file for details
