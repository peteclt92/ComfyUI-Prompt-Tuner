# 🎛️ ComfyUI Prompt Tuner

An LLM-powered prompt tuning node for ComfyUI. Turn short, rough prompts into detailed, model-ready **positive** prompts (and optionally **negative** prompts), using either Groq (cloud) or Ollama (local).

![ComfyUI](https://img.shields.io/badge/ComfyUI-Custom%20Node-blue)
![License](https://img.shields.io/badge/license-MIT-green)

## ✨ Features

- 🚀 **Groq API** support (fast, generous free tier)
- 🏠 **Ollama** support (local, offline)
- 🎬 **5 Styles**: cinematic, anime, photorealistic, artistic, niji
- 📊 **4 Detail Levels**: minimal, medium, detailed, extreme
- ✅ **Positive + Negative** prompt output (toggleable)
- 🧩 **Custom instructions** with a clean override/merge model
- 🪲 **Debug output**: shows the exact **system prompt** sent to the LLM (advanced node)

## 📦 Installation

Manual installation via Git:

```bash
cd ComfyUI/custom_nodes
git clone https://github.com/peteclt92/ComfyUI-Prompt-Tuner.git
```

Restart ComfyUI after installation.

## 🔑 API Setup

### Groq (Recommended)

1. Go to https://console.groq.com
2. Create an account
3. Create an API key
4. Paste the key into the node or set an environment variable:

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

# Download a model (example)
ollama pull llama3.2

# Start Ollama server
ollama serve
```

## 🎯 Nodes and Usage

Nodes are located under: **BoraOzkut/AI** (category name preserved for compatibility)

### Node: `🎛️ Prompt Tuner (LLM)` (Advanced)

This node supports Groq + Ollama, styles, detail levels, negatives, and debugging.

**Inputs**
- `simple_prompt`: the short prompt you want to tune/expand
- `llm_provider`: `groq` or `ollama`
- `model`: the LLM model identifier
- `style`: cinematic / anime / photorealistic / artistic / niji
- `detail_level`: minimal / medium / detailed / extreme
- `groq_api_key`: optional if `GROQ_API_KEY` is set
- `negative_prompt_request`: enable/disable negative prompt generation
- `custom_instructions`: your own instruction block for the LLM
- `merge_default_instructions`:
  - `false` (default): if `custom_instructions` is set, it **fully overrides** the built-in style/detail rules
  - `true`: if `custom_instructions` is set, it will be **appended** after the built-in style/detail rules

**Outputs**
- `positive_prompt`: tuned/expanded prompt
- `negative_prompt`: negative prompt (generated or fallback default)
- `system_prompt`: the exact system instruction text that was sent to the LLM (debugging)

### Node: `🎛️ Prompt Tuner (Simple)`

Ollama-only node with minimal controls.

**Inputs**
- `simple_prompt`
- `custom_instructions` (optional): if set, it **fully overrides** the built-in system instruction text

**Output**
- `tuned_prompt`

## 🧠 Custom Instructions: Override vs Merge

Default behavior is simple and predictable:

If `custom_instructions` is empty, the node uses its built-in prompt engineering instructions (style + detail + formatting rules).

If `custom_instructions` is set:
- With `merge_default_instructions = false`, your custom text becomes the **only** system prompt sent to the model.
- With `merge_default_instructions = true`, the node sends **defaults first**, then your custom text after it.

Tip: if you want a negative prompt in override mode, your `custom_instructions` must explicitly require the output format:
`POSITIVE: ...` and `NEGATIVE: ...` (otherwise the node will fall back to a default negative prompt).

## 📸 Example

**Input**
```text
boy, blonde, driving a car in San Francisco
```

**Possible output (cinematic, detailed)**
```text
A young blonde-haired man driving a vintage convertible through San Francisco, golden hour sunlight casting warm highlights across the dashboard, soft lens flare, shallow depth of field, cinematic framing with the Golden Gate Bridge in the distance, teal-and-amber color grading, crisp textures and realistic materials, subtle motion blur on the background, atmospheric haze, film still quality, ultra-detailed, high resolution
```

## 🔗 Workflow

Example connection:

```text
┌─────────────────────────┐
│   🎛️ Prompt Tuner (LLM)  │
│   "simple prompt"        │
└──┬──────────────┬────────┘
   │              │
   ▼              ▼
┌───────────┐  ┌───────────┐
│ positive  │  │ negative  │
│ prompt    │  │ prompt    │
└─────┬─────┘  └─────┬─────┘
      │              │
      ▼              ▼
  (to your)      (to your)
  sampler         sampler
  /pipeline       /pipeline
```

### Included workflows

- `workflow_z_image_turbo.json` (if present in the repo): ready-to-use workflow example

## 🛠️ Requirements

- ComfyUI
- Python 3.10+
- `requests` (commonly already present in ComfyUI environments)

Optional:
- ComfyUI-Custom-Scripts (ShowText helpers) if you like preview nodes in-graph

## 🤝 Contributing

PRs and issues are welcome:
- bugs and edge cases
- model/provider compatibility improvements
- additional styles or output formats (JSON parsing, structured prompts, etc.)

## 📄 License

MIT — see `LICENSE`.

## 🙏 Credits

Original concept and base implementation by **Bora Ozkut**.  
This fork continues development under the updated repository namespace.
