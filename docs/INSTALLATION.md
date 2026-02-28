# Installation Guide for uDownloader

## Quick Install (Recommended)

### macOS / Linux
```bash
pip install udownloader
```

### Windows
```cmd
pip install udownloader
```

Then run:
- **CLI**: `udownloader --help`
- **Desktop GUI**: `udownloader-desktop`

---

## Detailed Installation

### Prerequisites
- **Python 3.8 or higher** - [Download](https://www.python.org/downloads/)
- **pip** - Usually comes with Python3

### Platform-Specific Instructions

#### macOS
```bash
# Install dependencies
brew install ffmpeg  # Required for audio extraction

# Install uDownloader
pip install udownloader

# Run desktop app
udownloader-desktop

# Or use CLI
udownloader --url "https://youtube.com/watch?v=VIDEO_ID"
```

#### Linux (Ubuntu/Debian)
```bash
# Install dependencies
sudo apt-get update
sudo apt-get install python3 python3-pip ffmpeg

# Install uDownloader
pip install udownloader

# Run desktop app (may require display)
udownloader-desktop

# Or use CLI
udownloader --init-config
udownloader --url "https://youtube.com/watch?v=VIDEO_ID"
```

#### Windows (PowerShell or CMD)
```cmd
# Install ffmpeg using chocolatey (recommended)
choco install ffmpeg

# Or download from https://ffmpeg.org/download.html

# Install uDownloader
pip install udownloader

# Run desktop app
udownloader-desktop

# Or use CLI
udownloader --url "https://youtube.com/watch?v=VIDEO_ID"
```

---

## Development Installation

For development or custom modifications:

```bash
# Clone repository
git clone https://github.com/yourusername/uDownloader.git
cd uDownloader

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install in development mode
pip install -e .

# Or install with development tools
pip install -e ".[dev]"

# Run tests
pytest

# Run linter
flake8 youdownload

# Format code
black youdownload
```

---

## Docker Installation (Optional)

If you prefer Docker:

```bash
# Build image
docker build -t udownloader .

# Run CLI
docker run --rm -v $(pwd)/uDownload:/app/uDownload udownloader \
  udownloader --url "https://youtube.com/watch?v=VIDEO_ID"

# Run desktop (requires X11 display)
docker run --rm -e DISPLAY=$DISPLAY -v /tmp/.X11-unix:/tmp/.X11-unix \
  -v $(pwd)/uDownload:/app/uDownload udownloader udownloader-desktop
```

---

## Troubleshooting

### PyQt6 Installation Issues
If you get errors installing PyQt6 on macOS:
```bash
pip install --upgrade pip
pip install --user PyQt6
```

### FFmpeg Not Found
The desktop GUI and CLI require FFmpeg for audio extraction:
- **macOS**: `brew install ffmpeg`
- **Linux**: `sudo apt-get install ffmpeg`
- **Windows**: Download from [ffmpeg.org](https://ffmpeg.org/download.html)

### Permission Denied (Linux/macOS)
```bash
sudo pip install udownloader
# Or use user installation
pip install --user udownloader
```

### Virtual Environment Issues
```bash
# Create fresh venv
python3 -m venv venv --upgrade-deps
source venv/bin/activate
pip install udownloader
```

---

## Verify Installation

```bash
# Check CLI installation
udownloader --help

# Check desktop installation
udownloader-desktop --help  # (May not show help without display)

# Check package version
python -c "import youdownload; print(youdownload.__version__)"
```

---

## Uninstall

```bash
pip uninstall udownloader
```

This will remove the package and entry points but keep configuration in `~/.uDownloader/`

---

## Next Steps

After installation:
1. **CLI Users**: Run `udownloader --init-config` to create default config
2. **Desktop Users**: Launch `udownloader-desktop` and configure settings in the app
3. **First Download**: Start a download and check `./uDownload` folder for results

For more information, see [README.md](../README.md)
