# 🤖 Local Model Compatibility Guide

**Works great with ANY local model!**

The AI-Lab has been optimized to work well with local models of all sizes - from small 7B models to large 70B+ models.

---

## ✅ Tested Models

### Excellent Performance:
- **Llama 2 7B/13B** - Works great with simple mode
- **Mistral 7B** - Very good instruction following
- **CodeLlama 7B/13B** - Excellent for coding tasks
- **Qwen 7B/14B** - Strong multilingual support
- **Gemma 7B** - Good balance of performance

### Best Performance:
- **Llama 2 70B** - Excellent with complex tasks
- **CodeLlama 34B/70B** - Best for development work
- **Mixtral 8x7B** - Great instruction following
- **Yi 34B** - Very capable

---

## 🎯 Simple Mode (Default)

The system uses **Simple Mode** by default - optimized for local models:

### What Makes It Better:

**Clear Instructions:**
```
Instead of: "You're a development partner combining GitHub Copilot..."
Simple:     "You help users build software projects."
```

**Simple Tool Syntax:**
```
Clear example: <TOOLS>read_file(path="test.py")</TOOLS>
Not complex nested instructions
```

**Straightforward Steps:**
```
1. Ask where user wants project
2. Use create_project_from_template
3. Tell them it's done
```

**No Fancy Formatting:**
- No excessive emojis
- No complex unicode boxes
- Clear bullet points
- Simple examples

---

## 📋 Model-Specific Tips

### For 7B Models (Llama 2, Mistral):

**Best Practices:**
- Use commander mode for tasks
- Give clear, specific instructions
- One task at a time
- Use templates for projects

**Good Commands:**
```
✅ "Create a Python API called my-app"
✅ "Read the file test.py"
✅ "Make a new folder on Desktop called project"
✅ "List files in current directory"
```

**Avoid:**
```
❌ "Create a complex multi-service architecture with microservices..."
❌ Too many steps at once
```

### For 13B-34B Models:

**Can Handle:**
- Multi-step workflows
- Code refactoring
- Project analysis
- Complex file operations

**Good Commands:**
```
✅ "Create a Flask API with user authentication"
✅ "Refactor this code to be more efficient"
✅ "Analyze the project and suggest improvements"
```

### For 70B+ Models:

**Full Capability:**
- Everything smaller models can do
- Complex reasoning
- Large code refactoring
- Multi-file changes

---

## ⚙️ Configuration

### Enable Simple Mode (Default):
Simple mode is ON by default - no configuration needed!

### Use Advanced Mode (Optional):
For larger models (70B+), you can use advanced mode:

```python
# In api_server.py
system_prompt = get_system_prompt(
    commander_mode=True,
    use_simple_mode=False  # Use advanced prompts
)
```

---

## 💡 Tips for Best Results

### 1. **Be Specific**
```
Good: "Create a Flask API in ~/projects/my-api"
Bad:  "Make something"
```

### 2. **One Step at a Time**
For smaller models, break tasks down:
```
1. "Create project my-api"
2. "Add user authentication"
3. "Create database models"
```

### 3. **Use Templates**
Templates work great with all model sizes:
```
"Create a python-api project called user-service"
→ Complete project instantly!
```

### 4. **Specify Locations**
Always say where you want things:
```
"Create on Desktop" ✅
"Create in ~/Documents/work" ✅
"Just create my-api" → uses default workspace ✅
```

---

## 🧪 Testing Your Model

Quick test to see how well your model works:

### Test 1: Basic Tool Use
```
You: "What's the current directory?"
Expected: <TOOLS>get_current_directory</TOOLS>
```

### Test 2: File Creation
```
You: "Create a file test.py with print('hello')"
Expected: <TOOLS>create_file_with_content(path="test.py", content="print('hello')")</TOOLS>
```

### Test 3: Project Creation
```
You: "Create a Python CLI app called my-tool"
Expected: Asks where you want it
Then: Uses create_project_from_template
```

If your model passes these tests, it's working great!

---

## ⚡ Performance Optimization

### For Faster Response:

**1. Use Smaller Context**
- Commander mode works with any context size
- Tools list is shown clearly

**2. Quantization**
- Q4_K_M works great (good balance)
- Q5_K_M for better quality
- Q8_0 for best quality (slower)

**3. GPU Layers**
- Set based on your VRAM
- More layers = faster
- Even CPU-only works fine!

**Example Ollama Config:**
```bash
# Good balance
ollama run llama2:7b-q4_K_M

# Better quality
ollama run mistral:7b-q5_K_M

# Best for coding
ollama run codellama:13b
```

---

## 🎯 Model Recommendations

### For General Use:
1. **Mistral 7B** - Best all-around
2. **Llama 2 13B** - Very capable
3. **Qwen 14B** - Great alternative

### For Coding:
1. **CodeLlama 13B** - Excellent for development
2. **Deepseek Coder 7B** - Good code generation
3. **CodeLlama 7B** - Smaller but capable

### For Best Experience:
1. **Mixtral 8x7B** - Excellent reasoning
2. **CodeLlama 34B** - Best coding
3. **Llama 2 70B** - Most capable (requires good hardware)

---

## 🔧 Troubleshooting

### Model Not Following Instructions?

**Try:**
1. Check Commander Mode is enabled (⚡ button)
2. Be more specific in commands
3. Use simpler instructions
4. Break complex tasks into steps

### Tool Syntax Errors?

The model should use:
```
<TOOLS>tool_name(param="value")</TOOLS>
```

If it doesn't:
1. Model may need more examples
2. Try a different model
3. Mistral/CodeLlama usually work best

### Model Too Slow?

1. Use smaller model (7B)
2. Increase GPU layers
3. Use lower quantization (Q4)
4. Simple mode helps (default)

---

## ✅ Summary

**The system works great with local models because:**

✅ Simple, clear instructions
✅ Straightforward tool syntax
✅ No complex formatting
✅ Works with models from 7B to 70B+
✅ Optimized by default
✅ Templates for instant projects
✅ Clear examples provided

**Just enable Commander Mode and start building!** 🚀

---

**Recommended Setup:**
- Model: Mistral 7B or CodeLlama 13B
- Quantization: Q4_K_M or Q5_K_M
- Mode: Commander Mode with Simple Protocol (default)
- Works: Perfectly with this configuration! ✅
