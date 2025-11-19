# Quick Start Guide

Get up and running with GDOT Educational Video Generator in 5 minutes!

## Prerequisites

- **Python 3.10+** installed
- **Git** (optional, for cloning)

## Installation Steps

### 1. Install Dependencies

```bash
# Install Python packages
pip install -r requirements.txt

# Or run the automated setup
python setup.py
```

### 2. Install System Dependencies

#### Windows
Download and install **FFmpeg**: https://ffmpeg.org/download.html

#### Linux
```bash
sudo apt update
sudo apt install ffmpeg
```

#### macOS
```bash
brew install ffmpeg
```

### 3. Configure API Keys

1. Copy the environment template:
   ```bash
   cp env.example .env
   ```

2. Edit `.env` and add your API keys:
   ```env
   GROQ_API_KEY=your_groq_key_here
   SERPAPI_KEY=your_serpapi_key_here
   ```

   **Get API Keys:**
   - **Groq** (required): https://console.groq.com/keys
   - **SerpAPI** (optional): https://serpapi.com/manage-api-key

### 4. Run the Application

#### Streamlit UI (Recommended)
```bash
streamlit run app.py
```

Open browser to: http://localhost:8501

#### FastAPI Backend (Optional)
```bash
uvicorn api:app --reload
```

API docs at: http://localhost:8000/docs

## First Video Generation

1. **Load Sample**: Click "📄 Load Sample GDOT Markdown" button
2. **Generate**: Click "🚀 Generate Video" button
3. **Wait**: Watch the live flowchart as each step completes (~3-5 minutes)
4. **Download**: Download your generated video!

## Verify Installation

Run this quick check:

```bash
python -c "
import streamlit
import groq
import manim
print('✅ All imports successful!')
"
```

## Troubleshooting

### "ModuleNotFoundError: No module named 'X'"
```bash
pip install -r requirements.txt
```

### "Groq API Key missing"
Edit `.env` file and add your `GROQ_API_KEY`

### "Manim not found"
```bash
pip install manim
```

### "FFmpeg not found"
Install FFmpeg for your operating system (see step 2)

### Video generation fails
Check `data/errors.json` for detailed error logs

## Project Structure

```
coursemaker/
├── app.py              # Streamlit UI (start here!)
├── api.py              # FastAPI endpoints
├── workflow.py         # 11-step workflow engine
├── prompts.py          # GDOT-DOT prompts
├── db.py               # Database models
├── logger.py           # Error logging
├── requirements.txt    # Python dependencies
├── setup.py           # Automated setup
├── .env               # Your configuration
└── data/              # Generated files
    ├── md_videos.db   # SQLite database
    ├── outputs/       # Final videos
    ├── work/          # Temporary files
    └── checkpoints/   # Step checkpoints
```

## Usage Examples

### Example 1: Basic Usage
1. Paste Markdown content
2. Click "Generate Video"
3. Wait for completion
4. Download MP4

### Example 2: API Usage
```python
import requests

response = requests.post('http://localhost:8000/generate', json={
    'markdown_content': '# My Tutorial\n\nContent here...',
    'async_mode': True
})

job_id = response.json()['job_id']
print(f"Job started: {job_id}")

# Check status
status = requests.get(f'http://localhost:8000/jobs/{job_id}')
print(status.json())

# Download when done
video = requests.get(f'http://localhost:8000/download/{job_id}')
with open('video.mp4', 'wb') as f:
    f.write(video.content)
```

## Next Steps

- Customize prompts in `prompts.py` for your use case
- Adjust retry/error settings in `env.example`
- Explore the API documentation at `/docs`
- Check the full README.md for advanced features

## Support

- **Documentation**: See README.md
- **Errors**: Check `data/errors.json`
- **Logs**: Check `app.log`

## Tips for Best Results

✅ **DO:**
- Use clear, structured Markdown
- Include headers and sections
- Keep content under 2000 words
- Use technical language appropriate for audience

❌ **DON'T:**
- Submit extremely long documents (>10k chars)
- Include special characters in headers
- Expect instant results (3-5 min typical)
- Run multiple jobs simultaneously

Happy video making! 🎥

