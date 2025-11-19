# OpenAI API Setup Guide

This application now supports **both Groq and OpenAI** as LLM providers. You can choose which one to use!

## Quick Setup for OpenAI

### 1. Get Your OpenAI API Key

1. Go to https://platform.openai.com/api-keys
2. Sign in or create an account
3. Click "Create new secret key"
4. Copy your API key (starts with `sk-...`)

### 2. Configure Your `.env` File

Edit your `.env` file and add:

```env
# Choose OpenAI as your LLM provider
LLM_PROVIDER=openai

# Add your OpenAI API key
OPENAI_API_KEY=sk-your-key-here

# Optional: SerpAPI for images
SERPAPI_KEY=your_serpapi_key_here

# Other settings
MANIM_PATH=manim
EDGE_TTS_VOICE=en-US-GuyNeural
DB_PATH=./data/md_videos.db
CHECKPOINT_DIR=./data/checkpoints
LOGS_PATH=./data/errors.json
MAX_RETRIES_PER_STEP=3
MAX_TOTAL_RETRIES=10
ERROR_THRESHOLD_DEGRADED=5
```

### 3. Install OpenAI Package

```bash
pip install openai>=1.0.0
```

Or just:

```bash
pip install -r requirements.txt
```

### 4. Run the Application

```bash
streamlit run app.py
```

The UI will show "🤖 LLM Provider: **OPENAI**" in the sidebar.

## Switching Between Providers

### Use OpenAI (GPT-4o-mini)

```env
LLM_PROVIDER=openai
OPENAI_API_KEY=sk-your-key-here
```

**Pros:**
- High-quality output
- Well-tested models (GPT-4o-mini, GPT-4)
- Reliable performance
- Better code generation

**Cons:**
- Costs money (pay-per-token)
- Rate limits on free tier
- Requires billing setup

**Cost Estimate:**
- ~$0.02-0.05 per video (GPT-4o-mini)
- ~$0.10-0.30 per video (GPT-4)

### Use Groq (Mixtral-8x7b)

```env
LLM_PROVIDER=groq
GROQ_API_KEY=gsk-your-key-here
```

**Pros:**
- Free tier available
- Very fast inference
- Good open-source models
- No billing required

**Cons:**
- Smaller context window
- Rate limits can be strict
- Occasional quality variations

## Model Selection

### OpenAI Models (Configurable in `workflow.py`)

**Default: GPT-4o-mini**
- Fast and affordable
- Great for most use cases
- Recommended for development

**Alternative: GPT-4**
- Highest quality
- Best code generation
- More expensive

To change model, edit `workflow.py` line 319:

```python
response = client.chat.completions.create(
    model="gpt-4",  # Change from "gpt-4o-mini"
    messages=[{"role": "user", "content": prompt}],
    max_tokens=max_tokens,
    temperature=0.7
)
```

**Other OpenAI Models:**
- `gpt-4o`: Latest GPT-4 optimized
- `gpt-4-turbo`: Fast GPT-4 variant
- `gpt-3.5-turbo`: Cheaper, faster, lower quality

### Groq Models (Default: Mixtral-8x7b)

```python
model="mixtral-8x7b-32768"  # 32k context window
```

Other Groq models available:
- `llama-3.1-70b-versatile`: Llama 3.1 70B
- `llama-3.1-8b-instant`: Fastest, lower quality
- `gemma-7b-it`: Google's Gemma model

## Pricing Comparison

### OpenAI (Pay-per-token)

**GPT-4o-mini** (Recommended):
- Input: $0.15 / 1M tokens
- Output: $0.60 / 1M tokens
- **Video cost: ~$0.02-0.05**

**GPT-4**:
- Input: $5.00 / 1M tokens
- Output: $15.00 / 1M tokens
- **Video cost: ~$0.10-0.30**

**GPT-3.5-turbo**:
- Input: $0.50 / 1M tokens
- Output: $1.50 / 1M tokens
- **Video cost: ~$0.01-0.03**

### Groq (Free Tier)

- **Free:** 30 requests/min, 14,400 tokens/min
- **Pro ($0.59/mo):** Unlimited requests, 100k tokens/min
- **Video cost: FREE (with limits)**

## Recommended Configuration

### For Development/Testing
```env
LLM_PROVIDER=groq
GROQ_API_KEY=your-groq-key
```
✅ Free, fast, good enough for testing

### For Production/Quality
```env
LLM_PROVIDER=openai
OPENAI_API_KEY=your-openai-key
```
✅ Best quality, reliable, professional output

### For High Volume
```env
LLM_PROVIDER=openai
OPENAI_API_KEY=your-openai-key
# Set batch size limits, add queuing
```
✅ Scale with demand, predictable costs

## Verification

After configuration, run:

```bash
python test_installation.py
```

It will verify:
- ✅ LLM provider setting
- ✅ API key configuration
- ✅ Package availability
- ✅ Connection to API

Or check manually:

```python
import os
from dotenv import load_dotenv

load_dotenv()

provider = os.getenv('LLM_PROVIDER', 'groq')
print(f"Provider: {provider}")

if provider == 'openai':
    key = os.getenv('OPENAI_API_KEY')
    print(f"OpenAI Key: {'✓ Set' if key else '✗ Missing'}")
    
    # Test API
    from openai import OpenAI
    client = OpenAI(api_key=key)
    
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": "Say hello!"}],
        max_tokens=10
    )
    
    print(f"Response: {response.choices[0].message.content}")
    print("✅ OpenAI API working!")
```

## Troubleshooting

### Error: "OpenAI API Key missing"

**Solution:**
1. Check `.env` file exists
2. Verify `OPENAI_API_KEY=sk-...` (no quotes)
3. Verify `LLM_PROVIDER=openai`
4. Restart application

### Error: "Incorrect API key provided"

**Solution:**
1. Generate new key at https://platform.openai.com/api-keys
2. Copy entire key (starts with `sk-`)
3. Update `.env` file
4. Save and restart

### Error: "Rate limit exceeded"

**Solution for OpenAI:**
1. Add billing info at https://platform.openai.com/account/billing
2. Check usage limits
3. Wait for rate limit reset
4. Consider upgrading tier

**Solution for Groq:**
1. Wait 1 minute for reset
2. Reduce concurrent requests
3. Consider Groq Pro ($0.59/mo)

### Error: "You exceeded your current quota"

**Solution:**
1. Add credits to OpenAI account
2. Check billing dashboard
3. Set usage limits
4. Or switch to Groq (free)

### Provider Not Switching

**Solution:**
1. Clear any cached imports
2. Restart Python kernel
3. Verify `.env` file saved
4. Check `LLM_PROVIDER` value (lowercase)

## Performance Comparison

| Metric | OpenAI (GPT-4o-mini) | Groq (Mixtral-8x7b) |
|--------|---------------------|---------------------|
| **Speed** | ~3-5s per call | ~1-2s per call ⚡ |
| **Quality** | Excellent 🌟 | Good ✓ |
| **Cost** | $0.02-0.05/video 💰 | FREE 🆓 |
| **Reliability** | Very High 🔒 | High ✓ |
| **Code Gen** | Excellent 🌟 | Good ✓ |
| **Context** | 128k tokens | 32k tokens |
| **Rate Limits** | Generous | Moderate |

## Best Practices

### 1. Use OpenAI for Production
- More reliable output
- Better script generation
- Professional quality
- Worth the cost (~$0.05/video)

### 2. Use Groq for Development
- Test workflows quickly
- Iterate on prompts
- Save money during development
- Switch to OpenAI for final runs

### 3. Monitor Costs
```python
# Track tokens in UI
tokens_used = job.tokens['total']
estimated_cost = tokens_used / 1_000_000 * 0.75  # GPT-4o-mini average
print(f"Cost: ${estimated_cost:.4f}")
```

### 4. Set Budgets
In OpenAI dashboard:
1. Go to Settings → Limits
2. Set monthly budget
3. Enable email alerts
4. Monitor usage daily

## Support

### OpenAI Documentation
- API Docs: https://platform.openai.com/docs
- Pricing: https://openai.com/api/pricing
- Community: https://community.openai.com

### Groq Documentation
- API Docs: https://console.groq.com/docs
- Models: https://console.groq.com/docs/models
- Console: https://console.groq.com

### This Application
- See README.md for general setup
- See ARCHITECTURE.md for technical details
- See QUICKSTART.md for 5-min setup

---

**Recommendation:** Start with **Groq (free)** to test, then switch to **OpenAI (GPT-4o-mini)** for production quality at minimal cost (~$0.02-0.05 per video).

✅ Both providers fully supported with automatic switching!

