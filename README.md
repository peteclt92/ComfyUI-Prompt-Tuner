# 🎨 ComfyUI Prompt Tuner

An LLM-powered prompt expansion node for ComfyUI. Transform simple prompts into detailed, high-quality image generation prompts.

![ComfyUI](https://img.shields.io/badge/ComfyUI-Custom%20Node-blue)
![License](https://img.shields.io/badge/license-MIT-green)

## ✨ Features

- 🚀 **Groq API** support (free, super fast)
- 🏠 **Ollama** support (local, offline)
- 🎬 **5 Styles**: cinematic, anime, photorealistic, artistic, niji
- 📊 **4 Detail Levels**: minimal, medium, detailed, extreme
- ✅ Automatic **positive & negative prompt** generation
- 🔧 Custom instructions support

## 📦 Installation

Manual Installation via GIT

```bash
cd ComfyUI/custom_nodes
git clone https://github.com/peteclt92/ComfyUI-Prompt-Tuner.git
```

Restart ComfyUI after installation.

## 🔑 API Setup

### Groq (Recommended - Free & Fast)

1. Go to [console.groq.com](https://console.groq.com)
2. Create a free account
3. Navigate to API Keys → Create API Key
4. Copy and paste the key into the node, or set as environment variable:

**Windows (Command Prompt):**
```cmd
setx GROQ_API_KEY "gsk_xxxxxxxxxxxxx"
```

**Windows (PowerShell):**
```powershell
[Environment]::SetEnvironmentVariable("GROQ_API_KEY", "gsk_xxxxxxxxxxxxx", "User")
```

**Linux/Mac:**
```bash
export GROQ_API_KEY="gsk_xxxxxxxxxxxxx"
```

### Ollama (Local/Offline)

```bash
# Install Ollama
curl -fsSL https://ollama.com/install.sh | sh

# Download a model
ollama pull llama3.2

# Start Ollama server
ollama serve
```

## 🎯 Usage

### Node: `🎨 Prompt Tuner (LLM)`

Located in: **bozkut/AI**

| Input | Description |
|-------|-------------|
| `simple_prompt` | Your basic prompt (e.g., "boy, blonde, driving a car") |
| `llm_provider` | Choose between `groq` or `ollama` |
| `model` | Select LLM model |
| `style` | cinematic, anime, photorealistic, artistic, niji |
| `detail_level` | minimal, medium, detailed, extreme |
| `groq_api_key` | Your Groq API key (optional if using env variable) |
| `custom_instructions` | Additional instructions for the LLM (optional) |
| `negative_prompt_request` | Generate negative prompt (true/false) |

| Output | Description |
|--------|-------------|
| `positive_prompt` | Expanded detailed prompt |
| `negative_prompt` | Generated negative prompt |

## 📸 Example

**Input:**
```
boy, blonde, driving a car in San Francisco
```

**Output (cinematic, detailed):**
```
A young blonde-haired man behind the wheel of a classic convertible, 
golden hour sunlight streaming through the windshield, the iconic 
Golden Gate Bridge visible in the distant background, warm amber and 
teal color grading, shallow depth of field with bokeh lights, 
cinematic composition, lens flare, 8k resolution, photorealistic 
skin texture, wind-swept hair, California coastal atmosphere, 
dramatic lighting, movie still quality
```

## 🔗 Workflow

### Connection Diagram

```
┌─────────────────────┐
│  🎨 Prompt Tuner │
│  "simple prompt"    │
└──┬──────────────┬───┘
   │              │
   ▼              ▼
┌────────┐    ┌────────┐
│positive│    │negative│
│ prompt │    │ prompt │
└───┬────┘    └───┬────┘
    │             │
    ▼             ▼
┌────────┐    ┌────────┐
│ShowText│    │ShowText│  (optional - to preview)
└───┬────┘    └────────┘
    │
    ▼
┌─────────────────────┐
│  Image Generator    │
│  (Z Image, SDXL..)  │
└─────────────────────┘
```

### Included Workflows

- `workflow_z_image_turbo.json` - Ready-to-use workflow with Z Image Turbo

## 🛠️ Requirements

- ComfyUI
- Python 3.10+
- `requests` library (usually pre-installed)

### Optional
- [ComfyUI-Custom-Scripts](https://github.com/pythongosssss/ComfyUI-Custom-Scripts) - For ShowText node

## 🤝 Contributing

Pull requests are welcome! Feel free to:
- Report bugs
- Suggest new features
- Add new styles or LLM providers

## 📄 License

MIT License - see [LICENSE](LICENSE) for details.

## 🙏 Credits

Created by [Bora Ozkut](https://github.com/bozkut)

---

⭐ If you find this useful, please consider giving it a star!
