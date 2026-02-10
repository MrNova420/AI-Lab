# AI-Lab User Guide

Welcome to AI-Lab v1 Beta! This guide will help you get the most out of all the powerful features available.

---

## 🚀 Getting Started

### Installation
1. Clone the repository
2. Install Python dependencies: `pip3 install -r core/requirements.txt`
3. Install frontend dependencies: `cd app && npm install`
4. Start the backend: `python3 api/server.py`
5. Start the frontend: `cd app && npm run dev`

### First Launch
- The app opens with a clean chat interface
- Choose your preferred theme in Settings
- Configure your AI model (local or API)
- Start chatting!

---

## 🎨 Theme System

### Available Themes (7)
1. **Dark** - Default professional dark mode
2. **Light** - Clean bright theme
3. **High Contrast** - Maximum accessibility
4. **Dracula** - Popular purple developer theme
5. **Nord** - Cool Arctic minimal
6. **GitHub Dark** - Official GitHub colors
7. **Monokai** - Classic code editor theme

### How to Switch Themes
1. Click **Settings** in the sidebar
2. Scroll to **Theme Selection**
3. Click any theme preview card
4. Theme applies instantly
5. Your choice is saved automatically

---

## ⌨️ Keyboard Shortcuts

### Global Shortcuts
- `Cmd/Ctrl + K` - Open command palette
- `Cmd/Ctrl + /` - Show all shortcuts
- `Cmd/Ctrl + N` - New chat session
- `Cmd/Ctrl + S` - Save session
- `Cmd/Ctrl + B` - Toggle sidebar
- `Cmd/Ctrl + ,` - Open settings

### Feature Shortcuts
- `Cmd/Ctrl + Shift + C` - Toggle Commander Mode
- `Cmd/Ctrl + Shift + W` - Toggle Web Search
- `Cmd/Ctrl + Shift + B` - Create conversation branch
- `Cmd/Ctrl + Shift + A` - Create artifact

### Command Palette (Cmd+K)
Type to search for any command:
- New Session
- Save Session
- Open Settings
- Toggle modes
- Create artifacts
- Manage branches
- And more...

---

## 📦 Artifacts System

### What Are Artifacts?
Artifacts are reusable pieces of content created during conversations. Think of them like Claude's artifacts - code snippets, documents, data tables, charts, or HTML previews that you can save, edit, and reuse.

### 5 Artifact Types

#### 1. Code Artifacts
- Syntax highlighting for 50+ languages
- Copy code with one click
- Version control tracking
- Edit and update easily

#### 2. Document Artifacts
- Rich markdown support
- Live preview
- Edit mode available
- Export to markdown

#### 3. Data Artifacts
- Table display
- Sort by any column
- Filter/search data
- Export to CSV/JSON

#### 4. Chart Artifacts
- Line charts
- Bar charts
- Pie charts
- Area charts
- Interactive tooltips

#### 5. HTML Artifacts
- Safe iframe rendering
- Interactive content
- Live preview
- Full HTML/CSS/JS support

### How to Use Artifacts

#### Creating Artifacts
1. Click **📦 Artifacts** button in chat header
2. Click **+ New Artifact**
3. Choose artifact type
4. Fill in details (title, content, language)
5. Add tags for organization
6. Click **Save**

#### Managing Artifacts
- **View** - Click any artifact in library
- **Edit** - Click edit icon, make changes, save
- **Delete** - Click delete icon, confirm
- **Export** - Use export button (JSON, Markdown, Plain Text)
- **Search** - Use search bar to filter by title/tags

#### Version Control
- Every edit creates a new version
- View version history
- Restore previous versions
- Compare versions

---

## 🌿 Conversation Branching

### What Is Branching?
Like Git for conversations! Create alternate conversation paths from any point, explore different approaches, and merge the best ideas.

### How to Use Branches

#### Create a Branch
1. Click **🌿 Branch** button
2. Select a message to branch from
3. Enter branch name
4. Click **Create Branch**
5. Start chatting on the new branch

#### Switch Branches
1. Click **🌿 Branch** button
2. See tree visualization
3. Click any branch name
4. Messages update instantly

#### Merge Branches
1. Open branch navigator
2. Select branch to merge
3. Click **Merge** button
4. Confirm merge
5. Branches combine

#### Delete Branches
1. Open branch navigator
2. Select branch
3. Click **Delete**
4. Confirm deletion
5. Main branch remains safe

### Branch Tree Visualization
- See all branches in tree format
- Visual connections between branches
- Message count per branch
- Created date/time
- Current branch highlighted

---

## 🔍 Code Review System

### What Is Code Review?
Review code snippets with inline comments, threaded discussions, and approval workflow - just like GitHub!

### How to Review Code

#### Start a Review
1. Find any code block in messages
2. Click **🔍 Review** button
3. Review modal opens
4. Code displayed with line numbers

#### Add Comments
1. Click on any line number
2. Choose comment type:
   - **Suggestion** - Propose improvements
   - **Question** - Ask for clarification
   - **Praise** - Highlight good code
   - **Issue** - Point out problems
3. Write your comment
4. Click **Add Comment**

#### Reply to Comments
1. Find existing comment
2. Click **Reply**
3. Write response
4. Thread appears indented

#### Resolve Conversations
1. Click **Resolve** on comment thread
2. Thread collapses
3. Toggle to see resolved comments

#### Approve or Request Changes
1. Review all code
2. Add any comments
3. Click **Approve** or **Request Changes**
4. Status updates

### Review Statistics
- Total comments count
- Resolved vs open
- Approval status
- Last updated time

---

## 🧠 Context Management

### What Is Context?
The AI has a limited "memory window" (context). Context management helps you track and optimize what the AI remembers.

### Context Viewer

#### Open Context Viewer
- Click **🧠 Context** button in chat header
- Viewer appears above messages
- Shows real-time statistics

#### What You See
1. **Token Usage Bar**
   - Visual progress bar
   - Color coded: Green (safe), Orange (caution), Red (warning)
   - Used tokens / Total tokens

2. **Statistics**
   - Message count
   - Total characters
   - Estimated tokens
   - Percentage used

3. **Warnings**
   - Alert when > 80% full
   - Suggestion to start new session
   - Prevents context overflow

#### Pin Important Messages
1. Find important message
2. Click pin icon (when available)
3. Pinned messages stay in context
4. Count shows in context viewer

### Best Practices
- Monitor context regularly
- Start new session when near limit
- Pin important information
- Use branches for separate topics

---

## 💬 Chat Features

### Session Management

#### New Session
- Click **New Session** button
- Or press `Cmd/Ctrl + N`
- Fresh start with clean context

#### Save Session
- Click **Save Session**
- Or press `Cmd/Ctrl + S`
- Session saved automatically

#### Load Session
- Click **Sessions** button
- Browse saved sessions
- Click to load
- Messages restore

#### Delete Session
- Open sessions list
- Click trash icon
- Confirm deletion
- Session removed

### Commander Mode
- Toggle with button or `Cmd/Ctrl + Shift + C`
- Enables system operations
- File access, command execution
- Use responsibly!

### Web Search Mode
- Toggle with button or `Cmd/Ctrl + Shift + W`
- AI can search the web
- Get real-time information
- Sources included in responses

---

## 🎯 Tips & Best Practices

### For Better AI Responses
1. **Be Specific** - Clear questions get better answers
2. **Use Context** - Reference previous messages
3. **Break Down Complex Tasks** - Step by step works best
4. **Use Artifacts** - Save reusable content
5. **Branch Conversations** - Explore alternatives

### For Organization
1. **Name Your Branches** - Use descriptive names
2. **Tag Your Artifacts** - Makes finding easier
3. **Regular Sessions** - Start fresh for new topics
4. **Pin Key Info** - Keep important context

### For Productivity
1. **Learn Shortcuts** - Press `Cmd+/` to see all
2. **Use Command Palette** - `Cmd+K` for quick actions
3. **Customize Theme** - Find what works for you
4. **Review Your Code** - Catch issues early
5. **Export Artifacts** - Share with others

---

## 🔧 Troubleshooting

### App Won't Start
- Check Python 3.8+ installed
- Check Node.js installed
- Install all dependencies
- Check ports 5174 (frontend) and 5000 (backend) available

### AI Not Responding
- Check backend server running
- Verify model configured correctly
- Check internet connection (if using API)
- Look at console for errors

### Features Not Working
- Clear browser cache
- Restart frontend and backend
- Check for error messages
- Verify all dependencies installed

### Theme Not Applying
- Refresh the page
- Check browser console
- Try different theme
- Clear localStorage if needed

### Sessions Not Saving
- Check backend server running
- Verify write permissions
- Check disk space
- Look for error messages

---

## 📚 Additional Resources

### Documentation
- **README.md** - Project overview
- **INSTALLATION.md** - Detailed setup
- **LOCAL_MODEL_GUIDE.md** - Using local models
- **COMMANDER_MODE_GUIDE.md** - Advanced features
- **V1_BETA_IMPLEMENTATION.md** - Technical details

### Getting Help
- Check documentation first
- Look for similar issues
- Report bugs with details
- Include error messages

### Contributing
- Follow code style
- Add tests for features
- Update documentation
- Submit pull requests

---

## 🎉 Enjoy AI-Lab!

You now know how to use all the powerful features in AI-Lab v1 Beta. Explore, experiment, and enjoy!

**Happy Coding!** 🚀💙

---

**Version:** v1 Beta  
**Last Updated:** 2026-02-10  
**Questions?** Check the documentation or open an issue!
