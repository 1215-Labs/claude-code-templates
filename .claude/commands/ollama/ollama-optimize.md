---
name: ollama-optimize
description: |
  Recommend optimal Ollama model quantization and context window for your Apple Silicon Mac

  Usage: /ollama-optimize [model-name]

  Examples:
  /ollama-optimize
  /ollama-optimize "llama3.1"
  /ollama-optimize "qwen2.5:14b"
  /ollama-optimize "deepseek-r1"

  Best for: Picking the right model variant and maximizing usable context
argument-hint: "[model name like 'llama3.1' or 'qwen2.5:14b']"
user-invocable: true
thinking: auto
allowed-tools:
  - Bash(*)
  - Read
  - WebFetch
  - Write
  - Task
---

# Ollama Model Optimizer

**User request**: $ARGUMENTS

## Step 1: Preflight Checks

Run these commands in parallel to gather system state:

```bash
# Verify Ollama is running
curl -sf http://localhost:11434/api/version

# Detect hardware
sysctl -n hw.memsize
sysctl -n machdep.cpu.brand_string

# Check external storage
ls -d /Volumes/Storage/manifests 2>/dev/null && echo "STORAGE_MOUNTED=true" || echo "STORAGE_MOUNTED=false"

# Check installed models
ollama list
```

Read the Ollama launchd plist to detect KV cache type:

```bash
cat /Users/mike/Library/LaunchAgents/homebrew.mxcl.ollama.plist
```

Look for `OLLAMA_KV_CACHE_TYPE` in the plist. This affects memory math:
- `fp16` (or not set) → `kv_bytes = 2.0`
- `q8_0` → `kv_bytes = 1.0`
- `q4_0` → `kv_bytes = 0.5`

Also check for `OLLAMA_FLASH_ATTENTION` — if `1`, KV cache quantization is active.

**Compute memory budget:**
```
total_ram_gb = hw.memsize / 1073741824
usable_ram_gb = total_ram_gb × 0.75    # Reserve 25% for macOS + GPU driver on unified memory
```

Report: chip name, total RAM, usable RAM budget, KV cache type, flash attention status, storage mount status.

## Step 2: Parse Mode

- If `$ARGUMENTS` is present and non-empty → **Recommend mode** (go to Step 3B)
- If `$ARGUMENTS` is empty → **Audit mode** (go to Step 3A)

## Step 3A: Audit Installed Models

For each model in `ollama list`:

1. Run `ollama show <model> --verbose` and extract these architecture values:
   - `parameters` (e.g., 1.2B)
   - `quantization` (e.g., Q8_0)
   - `context length` (the model's native maximum)
   - `*.block_count` (n_layers)
   - `*.attention.head_count_kv` (n_kv_heads)
   - `*.attention.key_length` (head_dim for K)
   - `*.attention.value_length` (head_dim for V)

2. Calculate optimal context for this model using **Step 4 memory math**.

3. Determine the model's current effective num_ctx. Run:
   ```bash
   ollama show <model> --modelfile 2>/dev/null
   ```
   Look for `PARAMETER num_ctx` in the Modelfile output. If absent, the model uses Ollama's default (2048).

4. Flag models where current num_ctx is significantly below the calculated optimal.

**Present audit results as a table:**

```
| Model | Quant | Current ctx | Optimal ctx | Model's Max | Status |
|-------|-------|-------------|-------------|-------------|--------|
```

Status values:
- "Under-utilizing memory" — current ctx is <50% of optimal
- "Good" — current ctx is within 50-100% of optimal
- "Optimized" — running at or near optimal/max context
- "Over-allocated" — num_ctx exceeds what memory can support

For under-utilized models, offer to create optimized variants (go to Step 6).

## Step 3B: Recommend for Model

Parse the model argument:
- `"llama3.1"` → base model name, show all size variants
- `"qwen2.5:14b"` → specific size, show quant variants for that size
- `"deepseek-r1:32b-q4_K_M"` → exact variant, just analyze it

### Check if already installed

```bash
ollama show "$MODEL" --verbose 2>&1
```

If installed, extract architecture params from verbose output and calculate optimal settings. Then go to Step 5.

### If not installed: fetch available tags

Use WebFetch to get available tags from the Ollama library:

```
https://ollama.com/library/<base-model-name>/tags
```

Extract the tag list. For each relevant variant (matching size if specified), estimate memory requirements using the **embedded reference tables** below.

When the model name includes a size (e.g., `qwen2.5:14b`), focus on quant variants for that size. When it's just the base name (e.g., `llama3.1`), show the most promising variant for each parameter size.

For each variant, calculate memory and max context using Step 4 formulas. Go to Step 5.

## Step 4: Memory Math

These formulas compute how much context a model can handle given available memory.

### Model memory

```
model_memory_gb = parameters_B × bits_per_weight / 8
```

Where `bits_per_weight` comes from the quantization type (see reference table below).

### KV cache per token

```
kv_per_token_bytes = 2 × n_layers × (n_kv_heads_k × head_dim_k + n_kv_heads_v × head_dim_v) × kv_bytes
```

For most architectures, head_dim_k == head_dim_v and n_kv_heads_k == n_kv_heads_v, simplifying to:

```
kv_per_token_bytes = 2 × n_layers × n_kv_heads × head_dim × 2 × kv_bytes
```

Note: the first `2` accounts for both K and V caches. The `kv_bytes` depends on `OLLAMA_KV_CACHE_TYPE`:

| KV Cache Type | kv_bytes |
|---------------|----------|
| fp16 (default) | 2.0 |
| q8_0 | 1.0 |
| q4_0 | 0.5 |

### Available memory for KV cache

```
available_kv_gb = usable_ram_gb - model_memory_gb - 2.0    # 2 GB overhead for runtime buffers
```

If `available_kv_gb ≤ 0`, the model does not fit.

### Maximum context

```
max_context = floor(available_kv_gb × 1073741824 / kv_per_token_bytes)
```

Cap at the model's native maximum context length. Round down to nearest 1024.

### For uninstalled models (no verbose data)

When architecture params aren't available from `ollama show`, use the **model architecture reference table** below to estimate. Always prefer actual values from `ollama show --verbose` when the model is installed.

## Step 5: Recommendation Table

Present results as:

```
| Variant | Size (GB) | Max Context | Quality | Verdict |
|---------|-----------|-------------|---------|---------|
```

**Quality ratings by quantization:**

| Quant | Bits/Weight | Quality Rating |
|-------|-------------|----------------|
| Q4_0 | 4.0 | Fair — fastest, lowest quality |
| Q4_K_M | 4.8 | Good — best balance for constrained memory |
| Q5_K_M | 5.5 | Very Good — sweet spot when memory allows |
| Q6_K | 6.6 | Excellent — diminishing returns above this |
| Q8_0 | 8.0 | Near-FP16 — use when model is small enough |
| FP16 | 16.0 | Reference — only for very small models |

**Verdict logic** (pick the first that applies):
1. If `available_kv_gb ≤ 0` → "Too large"
2. If max_context < 4096 → "Too tight" (usable but severely limited)
3. If max_context < 16384 → "Context-limited"
4. Mark as **"Recommended"** the highest quality variant with max_context ≥ 16384 (or the model's native max if lower)
5. Mark variants above "Recommended" quality with useful context as "Also viable"
6. Mark lower quality variants that enable more context as "If context-hungry"

If multiple variants hit the model's native context cap, recommend the highest quality among them.

Present the table sorted by quality (highest first), then add a **summary recommendation** explaining the pick in plain language.

## Step 6: Execute (Confirmation Gate)

**IMPORTANT: Always ask the user before pulling models or creating Modelfiles.**

Present the action plan:
1. What will be pulled (tag name, estimated download size)
2. Where the Modelfile will be written (`/Volumes/Storage/Modelfiles/<name>` if storage is mounted, otherwise `~/.ollama/Modelfiles/<name>`)
3. The Modelfile contents:
   ```
   FROM <recommended-tag>
   PARAMETER num_ctx <calculated-optimal>
   PARAMETER num_gpu 99
   ```
4. The `ollama create` command that will run

Wait for explicit user confirmation before executing any of these commands.

### On confirmation

```bash
# Pull the model (may take a while)
ollama pull <recommended-tag>

# Write the Modelfile
mkdir -p /Volumes/Storage/Modelfiles
cat > /Volumes/Storage/Modelfiles/<name>.Modelfile << 'EOF'
FROM <recommended-tag>
PARAMETER num_ctx <calculated>
PARAMETER num_gpu 99
EOF

# Create the optimized variant
ollama create <name>-optimized -f /Volumes/Storage/Modelfiles/<name>.Modelfile
```

## Step 7: Verify

After creating the optimized variant:

```bash
# Confirm settings are applied
ollama show <name>-optimized --modelfile

# Quick smoke test
ollama run <name>-optimized "Say hello in exactly 5 words." --verbose 2>&1 | head -20

# Report disk usage
df -h /Volumes/Storage 2>/dev/null || df -h ~
```

Report:
- Confirmed num_ctx setting
- Smoke test response
- Remaining disk space
- Any warnings or issues

---

## Embedded Reference Tables

### Model Architecture Reference

Use these values ONLY when the model is not installed (no `ollama show --verbose` data). Always prefer actual values.

| Model Family | Params | Layers | KV Heads | Head Dim | Native Max Ctx |
|-------------|--------|--------|----------|----------|----------------|
| Llama 3.2 | 1B | 16 | 8 | 64 | 131072 |
| Llama 3.2 | 3B | 28 | 8 | 128 | 131072 |
| Llama 3.1 / 3.3 | 8B | 32 | 8 | 128 | 131072 |
| Llama 3.1 | 70B | 80 | 8 | 128 | 131072 |
| Qwen 2.5 | 0.5B | 24 | 2 | 64 | 32768 |
| Qwen 2.5 | 1.5B | 28 | 2 | 128 | 32768 |
| Qwen 2.5 | 3B | 36 | 4 | 128 | 32768 |
| Qwen 2.5 | 7B | 28 | 4 | 128 | 131072 |
| Qwen 2.5 | 14B | 48 | 4 | 128 | 131072 |
| Qwen 2.5 | 32B | 64 | 8 | 128 | 131072 |
| Qwen 2.5 | 72B | 80 | 8 | 128 | 131072 |
| Qwen3 | 0.6B | 28 | 2 | 64 | 40960 |
| Qwen3 | 1.7B | 28 | 4 | 128 | 40960 |
| Qwen3 | 4B | 36 | 8 | 128 | 40960 |
| Qwen3 | 8B | 36 | 8 | 128 | 131072 |
| Qwen3 | 14B | 40 | 8 | 128 | 131072 |
| Qwen3 | 30B | 48 | 8 | 128 | 131072 |
| Qwen3 | 32B | 64 | 8 | 128 | 131072 |
| DeepSeek-R1 (distill) | 1.5B | 28 | 2 | 128 | 131072 |
| DeepSeek-R1 (distill) | 7B | 28 | 4 | 128 | 131072 |
| DeepSeek-R1 (distill) | 8B | 32 | 8 | 128 | 131072 |
| DeepSeek-R1 (distill) | 14B | 48 | 4 | 128 | 131072 |
| DeepSeek-R1 (distill) | 32B | 64 | 8 | 128 | 131072 |
| DeepSeek-R1 (distill) | 70B | 80 | 8 | 128 | 131072 |
| Gemma 2 | 2B | 18 | 4 | 256 | 8192 |
| Gemma 2 | 9B | 42 | 4 | 256 | 8192 |
| Gemma 2 | 27B | 46 | 16 | 128 | 8192 |
| Gemma 3 | 1B | 18 | 4 | 256 | 32768 |
| Gemma 3 | 4B | 34 | 4 | 256 | 131072 |
| Gemma 3 | 12B | 48 | 4 | 256 | 131072 |
| Gemma 3 | 27B | 62 | 16 | 128 | 131072 |
| Phi-3 Mini | 3.8B | 32 | 8 | 96 | 131072 |
| Phi-3 Medium | 14B | 40 | 8 | 128 | 131072 |
| Phi-4 | 14B | 40 | 10 | 96 | 16384 |
| Mistral | 7B | 32 | 8 | 128 | 32768 |
| Mistral Nemo | 12B | 40 | 8 | 128 | 131072 |
| Mistral Small | 24B | 40 | 8 | 128 | 32768 |
| Codestral | 22B | 56 | 8 | 128 | 32768 |
| Command-R | 35B | 40 | 8 | 128 | 131072 |

### Quantization Bits Reference

| Quant Tag Suffix | Bits/Weight |
|-----------------|-------------|
| q4_0 | 4.0 |
| q4_1 | 4.5 |
| q4_K_S | 4.5 |
| q4_K_M | 4.8 |
| q5_0 | 5.0 |
| q5_1 | 5.5 |
| q5_K_S | 5.3 |
| q5_K_M | 5.5 |
| q6_K | 6.6 |
| q8_0 | 8.0 |
| fp16 | 16.0 |

---

## Error Handling

- **Ollama not running** → `curl` to version endpoint fails → Report: "Ollama is not running. Start it with: `brew services start ollama`"
- **External drive not mounted** → `/Volumes/Storage/manifests` doesn't exist → Warn user, fall back to default `~/.ollama` paths for Modelfiles. Note that OLLAMA_MODELS may point to unmounted drive.
- **Model not found on ollama.com** → WebFetch returns no tags → Suggest checking `https://ollama.com/library` for the correct name.
- **No variant fits in memory** → All variants have `available_kv_gb ≤ 0` → Recommend the smallest quantization of the smallest parameter count, or suggest a smaller model entirely.
- **Model already optimized** → Current num_ctx is within 10% of calculated optimal → Report "Already well-optimized" and show current settings.
- **WebFetch fails** → Fall back to the embedded architecture reference table. Note that estimates may be less accurate than live data.
