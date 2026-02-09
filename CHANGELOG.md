# 📝 Changelog

All notable changes to NovaForge AI Lab are documented here.

## [0.6.0] - 2026-02-09

### 🎉 Added - Session & User Management

#### Complete Session Management System
- **Unlimited Conversation History**: No more 100-message limits, full history preserved
- **Session Browser UI**: Dedicated Sessions page for browsing all past conversations
- **Smart Session Resumption**: Auto-resumes last session if < 30 minutes, fresh session otherwise
- **Activity Tracking**: Tracks user activity to determine session freshness
- **Session Export**: Export individual or bulk sessions with full metadata and tool tracking
- **Session Search/Filter**: Find sessions by content, type, or date
- **Auto-Save**: Every 5 seconds to backend storage
- **Session API**: 6 REST endpoints (start, load, list, save, delete, export)

#### Multi-User System
- **User Management**: Create, update, and switch between users
- **User Preferences**: Save mode preferences (commander, web search) per user
- **User Statistics**: Track sessions created, messages sent, conversations
- **Auto-Create Default**: Automatically creates "default" user on first run
- **User API**: 5 REST endpoints (current, list, create, update, set)
- **Session-User Linking**: Sessions tagged with user_id for isolation

#### Enhanced Tools (28 total, +7 new)
- **File Operations** (4 tools): read_file, write_file, list_files, file_info
  - Path-restricted to PROJECT_ROOT for security
  - Requires commander mode
- **Process Management** (3 tools): list_processes, process_info, find_process
  - Requires commander mode
  - Safe null handling

#### Frontend Enhancements
- **Chat Component**: New session button (✨ New), session browser modal
- **Voice Component**: Tool badges, backend session integration
- **Dashboard**: Tool statistics panel with analytics
- **Sessions Page**: Full-featured browser with export, search, filter
- **Tool Tracking**: Utility module tracks tool usage across sessions
- **State Persistence**: Utility module for preferences and history

### 🔧 Changed

#### API Server
- Enhanced `/api/sessions/list` with pagination and rich metadata
- Added session deletion endpoint `/api/sessions/delete`
- Updated `/api/sessions/start` to link with current user
- Improved error handling across all endpoints

#### Session Manager
- Added activity tracking methods (updateActivity, isSessionFresh)
- Enhanced session metadata (user_id, message counts, timestamps)
- Improved auto-save with debouncing
- Added export functionality with tool extraction

#### Chat/Voice Components
- Integrated with sessionManager instead of localStorage
- Added session UI controls (new, load, delete)
- Implemented smart session loading on mount
- Enhanced message metadata tracking

### 🔒 Security Fixes (PR Review - 28 comments resolved)

#### Critical Fixes
- **File Operations**: Added path validation to prevent directory traversal
- **Process Tools**: Gated behind commander mode to prevent info disclosure
- **Tool Markup**: Stripped `<TOOLS>` tags before streaming to prevent exposure
- **Exception Handling**: Replaced BaseException with specific exceptions
- **Null Safety**: Added checks for None values in process handling

#### API Improvements
- **Streaming Protocol**: Restored `full_response` in done payload
- **Commander API**: Fixed method mismatches (focus_window, keyboard_shortcut, clicks=2)
- **Error Responses**: Proper "not implemented" errors for unavailable features

#### Code Quality
- Removed unused imports from 4 files
- Fixed 7 broad exception handlers
- Enhanced error messages throughout

### 📚 Documentation

#### New Documentation
- `PROJECT_COMPLETE.md` - Comprehensive project status and features
- `FUTURE_ENHANCEMENTS.md` - AI-powered features roadmap (5 phases, 500+ lines)
- `PR_REVIEW_IMPLEMENTATION.md` - Security fixes and improvements
- `SESSION_MANAGEMENT_COMPLETE.md` - Session system documentation
- `USER_SYSTEM_COMPLETE.md` - User system documentation
- `FULL_SESSION_SYSTEM_COMPLETE.md` - Complete implementation guide

#### Updated Documentation
- `README.md` - Updated with current features, tool count, session management
- `ARCHITECTURE.md` - Added session and user management architecture
- Archived 23 old/redundant documentation files

### ✅ Quality Metrics
- **Security Vulnerabilities**: 0 (CodeQL validated)
- **Code Review Issues**: 0
- **Test Coverage**: Core features covered
- **Production Code**: ~15,000 lines
- **Documentation**: ~5,000 lines

## [0.5.0] - 2026-02-07

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
