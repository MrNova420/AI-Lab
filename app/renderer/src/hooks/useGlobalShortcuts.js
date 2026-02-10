/**
 * Global Keyboard Shortcuts Hook
 * Provides keyboard shortcuts across the entire application
 */

import { useEffect, useState } from 'react';
import { useHotkeys } from 'react-hotkeys-hook';

export const useGlobalShortcuts = (handlers) => {
  // Command Palette (Cmd/Ctrl + K)
  useHotkeys('mod+k', (e) => {
    e.preventDefault();
    handlers.openCommandPalette?.();
  }, [handlers.openCommandPalette]);
  
  // Show Shortcuts (Cmd/Ctrl + /)
  useHotkeys('mod+/', (e) => {
    e.preventDefault();
    handlers.showShortcuts?.();
  }, [handlers.showShortcuts]);
  
  // New Chat (Cmd/Ctrl + N)
  useHotkeys('mod+n', (e) => {
    e.preventDefault();
    handlers.newChat?.();
  }, [handlers.newChat]);
  
  // Save Session (Cmd/Ctrl + S)
  useHotkeys('mod+s', (e) => {
    e.preventDefault();
    handlers.saveSession?.();
  }, [handlers.saveSession]);
  
  // Toggle Sidebar (Cmd/Ctrl + B)
  useHotkeys('mod+b', (e) => {
    e.preventDefault();
    handlers.toggleSidebar?.();
  }, [handlers.toggleSidebar]);
  
  // Settings (Cmd/Ctrl + ,)
  useHotkeys('mod+,', (e) => {
    e.preventDefault();
    handlers.openSettings?.();
  }, [handlers.openSettings]);
  
  // Toggle Commander Mode (Cmd/Ctrl + Shift + C)
  useHotkeys('mod+shift+c', (e) => {
    e.preventDefault();
    handlers.toggleCommander?.();
  }, [handlers.toggleCommander]);
  
  // Toggle Web Search (Cmd/Ctrl + Shift + W)
  useHotkeys('mod+shift+w', (e) => {
    e.preventDefault();
    handlers.toggleWebSearch?.();
  }, [handlers.toggleWebSearch]);
  
  // Create Branch (Cmd/Ctrl + Shift + B)
  useHotkeys('mod+shift+b', (e) => {
    e.preventDefault();
    handlers.createBranch?.();
  }, [handlers.createBranch]);
  
  // Create Artifact (Cmd/Ctrl + Shift + A)
  useHotkeys('mod+shift+a', (e) => {
    e.preventDefault();
    handlers.createArtifact?.();
  }, [handlers.createArtifact]);
};

export default useGlobalShortcuts;
