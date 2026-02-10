"""
Enhanced AI Protocol - Supports 1B to 70B+ models
Integrates Grok-inspired search capabilities
"""

from core.hyper_minimal_protocol import get_hyper_minimal_prompt
from core.minimal_protocol import get_minimal_prompt
from core.ultra_simple_protocol import get_ultra_simple_prompt


def get_system_prompt(commander_mode: bool = False, model_size: str = 'medium', search_mode: str = 'basic') -> str:
    """
    Get appropriate system prompt based on mode and model size
    
    Args:
        commander_mode: Enable full system control capabilities
        model_size: 'tiny' (1B), 'small' (3B), 'medium' (7B+), 'large' (70B+)
        search_mode: 'basic' or 'grok' for enhanced search
        
    Returns:
        System prompt string
    """
    # Select base protocol by model size
    if model_size == 'tiny':
        # Hyper-minimal protocol - works with 1B models!
        prompt = get_hyper_minimal_prompt(commander_mode)
    elif model_size == 'small':
        # Minimal protocol - works with 3B models
        prompt = get_minimal_prompt(commander_mode)
    else:
        # Ultra simple protocol - works great with 7B+ models (default)
        prompt = get_ultra_simple_prompt(commander_mode)
    
    # Add Grok search capabilities if requested
    if search_mode == 'grok' and commander_mode:
        prompt += get_grok_search_addon()
    
    return prompt


def get_grok_search_addon() -> str:
    """
    Add Grok-inspired search capabilities to prompt
    """
    return """

ENHANCED SEARCH (Grok-Inspired):
Use grok_search for deep research:
<TOOLS>grok_search(query="topic", deep_mode=True)</TOOLS>

This gives you:
- Multi-source results
- Verification
- Citations
- Confidence scores
- Deep analysis

Example:
User: "Research AI safety"
You: <TOOLS>grok_search(query="AI safety research 2024", deep_mode=True)</TOOLS>
You: [Synthesize results with citations]
"""


# Convenience functions
def get_prompt_for_1b_model(commander_mode: bool = False) -> str:
    """Get prompt optimized for 1B models (TinyLlama, Phi-1, Qwen 1.8B)"""
    return get_hyper_minimal_prompt(commander_mode)


def get_prompt_for_3b_model(commander_mode: bool = False) -> str:
    """Get prompt optimized for 3B models (Phi-2, StableLM 3B)"""
    return get_minimal_protocol(commander_mode)


def get_prompt_for_7b_model(commander_mode: bool = False, grok_search: bool = False) -> str:
    """Get prompt optimized for 7B+ models (Mistral, Llama 2, etc.)"""
    return get_system_prompt(commander_mode, 'medium', 'grok' if grok_search else 'basic')


def get_prompt_for_70b_model(commander_mode: bool = False, grok_search: bool = True) -> str:
    """Get prompt optimized for 70B+ models with full capabilities"""
    return get_system_prompt(commander_mode, 'large', 'grok' if grok_search else 'basic')


# Model size detection helper
def detect_model_size(model_name: str) -> str:
    """
    Detect model size from name
    
    Returns: 'tiny', 'small', 'medium', or 'large'
    
    Examples:
        'tinyllama-1.1b' -> 'tiny'
        'phi-2-3b' -> 'small'
        'mistral-7b' -> 'medium'
        'llama-2-70b' -> 'large'
    """
    model_lower = model_name.lower()
    
    # Tiny models (1B-2B)
    if any(x in model_lower for x in ['1b', '1.1b', '1.3b', '1.8b', 'tinyllama', 'phi-1']):
        return 'tiny'
    
    # Small models (3B-7B)
    if any(x in model_lower for x in ['3b', '4b', '6b', 'phi-2']):
        return 'small'
    
    # Large models (70B+)
    if any(x in model_lower for x in ['70b', '65b', 'mixtral', '72b']):
        return 'large'
    
    # Default: Medium (7B-34B) - most common
    return 'medium'


# Get recommended prompt for model
def get_recommended_prompt(model_name: str, commander_mode: bool = False, grok_search: bool = False) -> str:
    """
    Get recommended prompt for specific model
    
    Args:
        model_name: Name of the model (e.g., 'mistral-7b-instruct')
        commander_mode: Enable Commander Mode
        grok_search: Enable Grok-inspired search
        
    Returns:
        Optimized system prompt
    """
    size = detect_model_size(model_name)
    search_mode = 'grok' if grok_search else 'basic'
    return get_system_prompt(commander_mode, size, search_mode)
