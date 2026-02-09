// Tool execution tracking utility
// Tracks tool usage statistics in localStorage for Dashboard visualization

/**
 * Track a tool execution
 * @param {string} toolName - Name of the tool executed
 * @param {string} category - Category of the tool (system, web, etc.)
 * @param {boolean} success - Whether the execution was successful
 * @param {number} duration - Execution duration in milliseconds (optional)
 */
export function trackToolExecution(toolName, category = 'system', success = true, duration = 0) {
  try {
    // Get existing stats
    const stored = localStorage.getItem('toolExecutionStats');
    const stats = stored ? JSON.parse(stored) : { executions: [] };
    
    // Add new execution
    stats.executions = stats.executions || [];
    stats.executions.push({
      tool: toolName,
      category: category,
      success: success,
      duration: duration,
      timestamp: new Date().toISOString()
    });
    
    // Limit to last 1000 executions to prevent storage bloat
    if (stats.executions.length > 1000) {
      stats.executions = stats.executions.slice(-1000);
    }
    
    // Save back to localStorage
    localStorage.setItem('toolExecutionStats', JSON.stringify(stats));
    
    console.log(`📊 Tracked tool execution: ${toolName} (${category}) - ${success ? '✅' : '❌'}`);
  } catch (error) {
    console.error('Failed to track tool execution:', error);
  }
}

/**
 * Extract tool names from AI response containing 🛠️ emoji markers
 * @param {string} response - AI response text
 * @returns {Array<string>} Array of tool names found
 */
export function extractToolsFromResponse(response) {
  const tools = [];
  
  if (!response || !response.includes('🛠️')) {
    return tools;
  }
  
  // Match patterns like "🛠️ tool_name:" or "🛠️ tool_name "
  const toolPattern = /🛠️\s*(\w+)/g;
  let match;
  
  while ((match = toolPattern.exec(response)) !== null) {
    tools.push(match[1]);
  }
  
  return tools;
}

/**
 * Track tools from an AI response
 * @param {string} response - AI response containing tool execution markers
 * @param {string} defaultCategory - Default category if not detected
 */
export function trackToolsFromResponse(response, defaultCategory = 'system') {
  const tools = extractToolsFromResponse(response);
  
  tools.forEach(tool => {
    // Try to determine category from tool name
    let category = defaultCategory;
    if (tool.includes('web') || tool.includes('search')) {
      category = 'web';
    } else if (tool.includes('file') || tool.includes('read') || tool.includes('write')) {
      category = 'files';
    } else if (tool.includes('process')) {
      category = 'processes';
    } else if (tool.includes('system') || tool.includes('mouse') || tool.includes('keyboard') || tool.includes('app')) {
      category = 'system';
    }
    
    trackToolExecution(tool, category, true);
  });
}

/**
 * Clear all tool execution statistics
 */
export function clearToolStats() {
  try {
    localStorage.removeItem('toolExecutionStats');
    console.log('📊 Tool execution statistics cleared');
  } catch (error) {
    console.error('Failed to clear tool stats:', error);
  }
}

/**
 * Get tool execution statistics
 * @returns {Object} Statistics object
 */
export function getToolStats() {
  try {
    const stored = localStorage.getItem('toolExecutionStats');
    if (stored) {
      return JSON.parse(stored);
    }
  } catch (error) {
    console.error('Failed to get tool stats:', error);
  }
  
  return { executions: [] };
}
