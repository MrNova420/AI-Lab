/**
 * Browser-based Commander - System control via JavaScript
 * Note: Limited by browser security - can only:
 * - Open URLs
 * - Copy/paste to clipboard
 * - Open new tabs/windows
 * - Navigate pages
 * 
 * For full system control (mouse, keyboard, apps), use Electron or native app
 */

export class BrowserCommander {
  constructor() {
    this.activityLog = [];
  }

  logActivity(action, details, success = true) {
    const entry = {
      timestamp: new Date().toISOString(),
      action,
      details,
      success
    };
    this.activityLog.push(entry);
    console.log('📝 Commander log:', entry);
  }

  parseCommand(userInput) {
    const userLower = userInput.toLowerCase();
    const commands = [];

    // Open URL
    if (userLower.includes('open') && (userLower.includes('http') || userLower.includes('.com') || userLower.includes('.org'))) {
      const urlMatch = userInput.match(/(https?:\/\/[^\s]+|www\.[^\s]+|[^\s]+\.(com|org|net|edu))/i);
      if (urlMatch) {
        let url = urlMatch[0];
        if (!url.startsWith('http')) {
          url = 'https://' + url;
        }
        commands.push({ action: 'open_url', url });
      }
    }

    // Search web
    if (userLower.includes('search') || userLower.includes('google')) {
      const searchMatch = userInput.match(/(?:search|google)\s+(?:for\s+)?["']?([^"']+)["']?/i);
      if (searchMatch) {
        const query = searchMatch[1].trim();
        commands.push({ action: 'search_web', query });
      }
    }

    // Copy text
    if (userLower.includes('copy')) {
      const copyMatch = userInput.match(/copy\s+["']([^"']+)["']/i);
      if (copyMatch) {
        commands.push({ action: 'clipboard_copy', text: copyMatch[1] });
      }
    }

    // Open app (limited - only web apps)
    if (userLower.includes('open')) {
      const webApps = {
        'gmail': 'https://mail.google.com',
        'youtube': 'https://youtube.com',
        'github': 'https://github.com',
        'discord': 'https://discord.com/app',
        'twitter': 'https://twitter.com',
        'reddit': 'https://reddit.com',
        'spotify': 'https://open.spotify.com',
        'netflix': 'https://netflix.com',
        'amazon': 'https://amazon.com',
        'steam': 'https://store.steampowered.com'
      };

      for (const [app, url] of Object.entries(webApps)) {
        if (userLower.includes(app)) {
          commands.push({ action: 'open_url', url, appName: app });
          break;
        }
      }
    }

    // Screenshot (download page as PDF or capture visible area)
    if (userLower.includes('screenshot') || userLower.includes('capture')) {
      commands.push({ action: 'screenshot' });
    }

    // Fullscreen
    if (userLower.includes('fullscreen') || userLower.includes('full screen')) {
      commands.push({ action: 'fullscreen' });
    }

    // Scroll
    if (userLower.includes('scroll')) {
      const amount = userLower.includes('up') ? -300 : 300;
      commands.push({ action: 'scroll', amount });
    }

    return commands;
  }

  async executeCommand(command) {
    const { action } = command;

    try {
      switch (action) {
        case 'open_url':
          return await this.openUrl(command.url, command.appName);

        case 'search_web':
          return await this.searchWeb(command.query);

        case 'clipboard_copy':
          return await this.copyToClipboard(command.text);

        case 'screenshot':
          return await this.takeScreenshot();

        case 'fullscreen':
          return await this.toggleFullscreen();

        case 'scroll':
          return await this.scroll(command.amount);

        default:
          return { success: false, error: `Unknown action: ${action}` };
      }
    } catch (error) {
      this.logActivity(action, { error: error.message }, false);
      return { success: false, error: error.message };
    }
  }

  async openUrl(url, appName = null) {
    try {
      window.open(url, '_blank');
      const message = appName ? `Opened ${appName}` : `Opened ${url}`;
      this.logActivity('open_url', { url, appName });
      return { success: true, message };
    } catch (error) {
      this.logActivity('open_url', { error: error.message }, false);
      return { success: false, error: error.message };
    }
  }

  async searchWeb(query) {
    try {
      const url = `https://www.google.com/search?q=${encodeURIComponent(query)}`;
      window.open(url, '_blank');
      this.logActivity('search_web', { query });
      return { success: true, message: `Searching for: ${query}` };
    } catch (error) {
      this.logActivity('search_web', { error: error.message }, false);
      return { success: false, error: error.message };
    }
  }

  async copyToClipboard(text) {
    try {
      await navigator.clipboard.writeText(text);
      this.logActivity('clipboard_copy', { length: text.length });
      return { success: true, message: 'Copied to clipboard' };
    } catch (error) {
      this.logActivity('clipboard_copy', { error: error.message }, false);
      return { success: false, error: error.message };
    }
  }

  async takeScreenshot() {
    try {
      // Browser can't take system screenshots, but we can trigger print dialog
      window.print();
      this.logActivity('screenshot', {});
      return { success: true, message: 'Print dialog opened (use "Save as PDF" to capture page)' };
    } catch (error) {
      this.logActivity('screenshot', { error: error.message }, false);
      return { success: false, error: error.message };
    }
  }

  async toggleFullscreen() {
    try {
      if (!document.fullscreenElement) {
        await document.documentElement.requestFullscreen();
        this.logActivity('fullscreen', { state: 'entered' });
        return { success: true, message: 'Entered fullscreen' };
      } else {
        await document.exitFullscreen();
        this.logActivity('fullscreen', { state: 'exited' });
        return { success: true, message: 'Exited fullscreen' };
      }
    } catch (error) {
      this.logActivity('fullscreen', { error: error.message }, false);
      return { success: false, error: error.message };
    }
  }

  async scroll(amount) {
    try {
      window.scrollBy({
        top: amount,
        behavior: 'smooth'
      });
      this.logActivity('scroll', { amount });
      return { success: true, message: `Scrolled ${amount > 0 ? 'down' : 'up'}` };
    } catch (error) {
      this.logActivity('scroll', { error: error.message }, false);
      return { success: false, error: error.message };
    }
  }

  async executeUserCommand(userInput) {
    try {
      const commands = this.parseCommand(userInput);

      if (commands.length === 0) {
        return {
          success: false,
          error: 'Could not parse command',
          suggestion: 'Try: "open gmail", "search for AI tutorials", "copy hello world", "scroll down"'
        };
      }

      const results = [];
      for (const cmd of commands) {
        const result = await this.executeCommand(cmd);
        results.push({ command: cmd, result });
      }

      const allSuccess = results.every(r => r.result.success);
      const messages = results.map(r => r.result.message || r.result.error).filter(Boolean);

      return {
        success: allSuccess,
        user_input: userInput,
        commands,
        results,
        message: messages.join(', ')
      };
    } catch (error) {
      return { success: false, error: error.message };
    }
  }

  getActivityLog() {
    return this.activityLog;
  }
}

export default BrowserCommander;
