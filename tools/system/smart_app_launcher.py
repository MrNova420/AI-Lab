#!/usr/bin/env python3
"""
Simple AI Helper Functions - NO HARDCODED LOGIC
AI uses its intelligence to figure things out!
"""

# NOTE: This file is kept minimal on purpose
# We removed hardcoded URL mappings because:
# - AI models already know common websites (Steam = store.steampowered.com, etc.)
# - AI can use search_web tool to find URLs if unsure
# - AI reasoning is better than hardcoded rules
# - More flexible - works for ANY app, not just predefined ones

# The AI workflow is:
# 1. User: "Open Steam"
# 2. AI: check_app("steam") 
# 3. AI sees it's not installed
# 4. AI KNOWS Steam website or searches for it
# 5. AI: open_url("https://store.steampowered.com")
#
# This is TRUE AI-driven behavior!
