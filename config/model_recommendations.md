# Recommended Models for GTX 1050 4GB

## Chat/Instruction (Best Performance)
- **Llama 3.2 3B** (Q4_K_M, ~2GB VRAM) - Fast, capable
- **Phi-3 Mini 3.8B** (Q4_K_M, ~2.5GB VRAM) - Excellent quality
- **Qwen2.5 1.5B** (Q6_K, ~1.2GB VRAM) - Lightning fast

## Coding
- **Qwen2.5-Coder 1.5B** (Q6_K) - Surprisingly good
- **DeepSeek-Coder 1.3B** (Q4_K_M)

## Avoid (Too Big)
- Llama 3.1 8B (needs 6GB+)
- Mistral 7B (needs 5GB+)
- Any unquantized model

## Command to run optimally:
ollama run llama3.2:3b
# or
python -m llama_cpp.server --model models/gguf/llama-3.2-3b-q4_k_m.gguf --n_gpu_layers 25
