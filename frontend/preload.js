const { contextBridge, ipcRenderer } = require('electron');

// Expose protected methods that allow the renderer process to use
// the ipcRenderer without exposing the entire object
contextBridge.exposeInMainWorld('electronAPI', {
  // File operations
  openProject: (callback) => ipcRenderer.on('open-project', callback),
  exportReport: (callback) => ipcRenderer.on('export-report', callback),
  
  // File dialogs
  showOpenDialog: (options) => ipcRenderer.invoke('show-open-dialog', options),
  showSaveDialog: (options) => ipcRenderer.invoke('show-save-dialog', options),
  
  // Analysis operations  
  startAnalysis: (callback) => ipcRenderer.on('start-analysis', callback),
  clearResults: (callback) => ipcRenderer.on('clear-results', callback),
  
  // System info
  platform: process.platform,
  versions: process.versions,
  
  // Utility functions
  removeAllListeners: (channel) => ipcRenderer.removeAllListeners(channel),
  
  // Window controls
  minimize: () => ipcRenderer.invoke('minimize-window'),
  maximize: () => ipcRenderer.invoke('maximize-window'),
  close: () => ipcRenderer.invoke('close-window'),
});
