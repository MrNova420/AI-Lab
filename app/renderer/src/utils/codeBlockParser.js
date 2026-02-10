/**
 * Code Block Parser
 * Detects and extracts code blocks from messages
 */

export const parseCodeBlocks = (content) => {
  // Match code blocks with ```language or just ```
  const codeBlockRegex = /```(\w+)?\n([\s\S]*?)```/g;
  const parts = [];
  let lastIndex = 0;
  let match;
  
  while ((match = codeBlockRegex.exec(content)) !== null) {
    // Add text before code block
    if (match.index > lastIndex) {
      parts.push({
        type: 'text',
        content: content.slice(lastIndex, match.index)
      });
    }
    
    // Add code block
    parts.push({
      type: 'code',
      language: match[1] || 'plaintext',
      content: match[2].trim()
    });
    
    lastIndex = match.index + match[0].length;
  }
  
  // Add remaining text
  if (lastIndex < content.length) {
    parts.push({
      type: 'text',
      content: content.slice(lastIndex)
    });
  }
  
  return parts.length > 0 ? parts : [{ type: 'text', content }];
};

export const hasCodeBlocks = (content) => {
  return /```(\w+)?\n[\s\S]*?```/.test(content);
};

export default { parseCodeBlocks, hasCodeBlocks };
