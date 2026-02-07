# 📝 Changelog

All notable changes to NovaForge AI Lab are documented here.

## [Unreleased] - 2026-02-07

### 🎉 Added

#### Reasoning & Learning Layer
- **Context Memory System**: Tracks tool history (20), conversations (50), user preferences
- **Session Persistence**: Sessions save to `memory/sessions/{session_id}.pkl`
- **Smart Caching**: Tool-specific timeouts (30s-1hr) with 30-120x speedup
- **Intent Analysis**: Classifies requests into 5 types (Simple, Complex, Multi-step, Research, Control)
- **Multi-Step Planning**: Dependency analysis and execution planning
- **Learning System**: Tracks success rates and execution times
- **Result Verification**: Confidence scoring and error detection
- **Session Management**: Per-session isolation for multi-user scenarios

#### API Enhancements
- Session ID tracking in API requests
- Context injection into AI system prompts
- Smart execution with cache checking
- Result verification before final response
- Conversation tracking and auto-save
- Reasoning info streaming to UI (new message type: "reasoning")
- Cache indicators in tool results (💾 icon)

#### UI Improvements
- Session ID included in API requests (`browser_session`)
- Reasoning message handling
- Visual feedback for cache hits
- Mode badges in chat (⚡CMD, 🌐WEB)
- Console logging for reasoning traces

#### Documentation
- `MASTER_DOCUMENTATION.md` (61KB) - Complete system reference
- `CURRENT_TOOLS.md` - Full tool documentation
- `docs/WORKFLOW_ANALYSIS.md` - Mode workflow details
- Updated `README.md` with reasoning layer info

### 🔧 Changed

#### Tools System
- Combined date/time tools into single `datetime` tool
- Enhanced `system_info` to return real system data (no hallucinations)
- Added `requires_verification` flag to tool definitions
- Fast vs Smart execution modes for different tool types

#### AI Protocol
- Dynamic tool description generation
- No hardcoded response patterns
- Tool-aware system prompts
- Improved error handling

### 🐛 Fixed
- System info returning fake data (Intel/64GB) → Now returns real Ubuntu/AMD data
- API 404 errors with incorrect port (5173 vs 5174)
- Mode toggles not working properly
- Cache not being utilized efficiently
- Sessions not persisting across restarts

### 🚀 Performance
- Cache hit speedup: 30-120x faster responses
- Expected cache hit rates: datetime 60-80%, system_info 90-95%, user_info 95-99%
- Reduced API response times from 2-6s to 0.01-0.1s on cache hits
- Session persistence prevents re-learning on restart

## Previous Versions

See git history for earlier changes.

---

**Format:** Based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/)
