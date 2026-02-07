"""
Live Activity Logger - Shows what AI is researching in real-time
"""

class LiveLogger:
    """Real-time activity logging for web search"""
    
    def __init__(self, callback=None):
        self.callback = callback or print
        self.activities = []
    
    def log(self, message: str, level: str = "info"):
        """
        Log an activity
        level: info, success, warning, error
        """
        icons = {
            'info': '🔍',
            'success': '✅',
            'warning': '⚠️',
            'error': '❌',
            'search': '🌐',
            'verify': '🔬',
            'analyze': '📊'
        }
        
        icon = icons.get(level, '📝')
        formatted = f"{icon} {message}"
        
        self.activities.append({
            'message': message,
            'level': level,
            'formatted': formatted
        })
        
        self.callback(formatted)
    
    def clear(self):
        """Clear activity log"""
        self.activities = []
    
    def get_log(self):
        """Get full activity log"""
        return self.activities


# Global logger instance
_logger = LiveLogger()

def log_activity(message: str, level: str = "info"):
    """Log a web search activity"""
    _logger.log(message, level)

def get_activities():
    """Get all logged activities"""
    return _logger.get_log()

def clear_activities():
    """Clear activity log"""
    _logger.clear()
