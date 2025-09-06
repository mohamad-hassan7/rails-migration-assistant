const { app, BrowserWindow, dialog, shell, Menu, ipcMain } = require('electron');
const path = require('path');
const isDev = process.env.NODE_ENV === 'development';

let mainWindow;

function createWindow() {
  // Create the browser window
  mainWindow = new BrowserWindow({
    width: 1200,
    height: 800,
    minWidth: 1000,
    minHeight: 700,
    webPreferences: {
      nodeIntegration: false,
      contextIsolation: true,
      enableRemoteModule: false,
      preload: path.join(__dirname, 'preload.js')
    },
    icon: path.join(__dirname, 'assets/icon.png'), // Add app icon
    titleBarStyle: process.platform === 'darwin' ? 'hiddenInset' : 'default',
    show: false // Don't show until ready-to-show
  });

  // Load the app
  if (isDev) {
    mainWindow.loadURL('http://localhost:5173');
    // DevTools can still be opened via View menu or F12 if needed
  } else {
    // Load the fixed main app
    const appPath = path.join(__dirname, 'dist', 'index_fixed.html');
    console.log('Loading app from:', appPath);
    mainWindow.loadFile(appPath);
    
    // Don't open DevTools by default in production
    // Users can still open them via View menu or F12
  }

  // Show window when ready to prevent visual flash
  mainWindow.once('ready-to-show', () => {
    mainWindow.show();
    
    // Focus on window (for Windows/Linux)
    if (process.platform !== 'darwin') {
      mainWindow.focus();
    }
  });

  // Handle window closed
  mainWindow.on('closed', () => {
    mainWindow = null;
  });

  // Handle external links
  mainWindow.webContents.setWindowOpenHandler(({ url }) => {
    shell.openExternal(url);
    return { action: 'deny' };
  });

  // Set up menu
  createMenu();

  // Monaco preload removed: no longer needed
}

function createMenu() {
  const template = [
    {
      label: 'File',
      submenu: [
        {
          label: 'Open Project...',
          accelerator: 'CmdOrCtrl+O',
          click: async () => {
            const result = await dialog.showOpenDialog(mainWindow, {
              properties: ['openDirectory'],
              title: 'Select Rails Project Directory'
            });
            
            if (!result.canceled && result.filePaths.length > 0) {
              mainWindow.webContents.send('open-project', result.filePaths[0]);
            }
          }
        },
        { type: 'separator' },
        {
          label: 'Export Report...',
          accelerator: 'CmdOrCtrl+E',
          click: () => {
            mainWindow.webContents.send('export-report');
          }
        },
        { type: 'separator' },
        {
          label: 'Exit',
          accelerator: process.platform === 'darwin' ? 'Cmd+Q' : 'Ctrl+Q',
          click: () => {
            app.quit();
          }
        }
      ]
    },
    {
      label: 'Edit',
      submenu: [
        { role: 'undo' },
        { role: 'redo' },
        { type: 'separator' },
        { role: 'cut' },
        { role: 'copy' },
        { role: 'paste' },
        { role: 'selectall' }
      ]
    },
    {
      label: 'View',
      submenu: [
        { role: 'reload' },
        { role: 'forceReload' },
        { role: 'toggleDevTools' },
        { type: 'separator' },
        { role: 'resetZoom' },
        { role: 'zoomIn' },
        { role: 'zoomOut' },
        { type: 'separator' },
        { role: 'togglefullscreen' }
      ]
    },
    {
      label: 'Analysis',
      submenu: [
        {
          label: 'Start Analysis',
          accelerator: 'CmdOrCtrl+R',
          click: () => {
            mainWindow.webContents.send('start-analysis');
          }
        },
        {
          label: 'Clear Results',
          click: () => {
            mainWindow.webContents.send('clear-results');
          }
        }
      ]
    },
    {
      label: 'Help',
      submenu: [
        {
          label: 'About Rails Migration Assistant',
          click: () => {
            dialog.showMessageBox(mainWindow, {
              type: 'info',
              title: 'About',
              message: 'Rails Migration Assistant',
              detail: 'Version 2.0.0\n\nA modern tool for upgrading Ruby on Rails applications.\n\nBuilt with Electron and React.'
            });
          }
        },
        {
          label: 'Documentation',
          click: () => {
            shell.openExternal('https://github.com/mohamed7456/rails-migration-assistant');
          }
        }
      ]
    }
  ];

  // macOS specific menu adjustments
  if (process.platform === 'darwin') {
    template.unshift({
      label: app.getName(),
      submenu: [
        { role: 'about' },
        { type: 'separator' },
        { role: 'services' },
        { type: 'separator' },
        { role: 'hide' },
        { role: 'hideOthers' },
        { role: 'unhide' },
        { type: 'separator' },
        { role: 'quit' }
      ]
    });

    // Window menu
    template[4].submenu = [
      { role: 'close' },
      { role: 'minimize' },
      { role: 'zoom' },
      { type: 'separator' },
      { role: 'front' }
    ];
  }

  const menu = Menu.buildFromTemplate(template);
  Menu.setApplicationMenu(menu);
}

// IPC handlers for file dialogs
ipcMain.handle('show-open-dialog', async (event, options) => {
  const result = await dialog.showOpenDialog(mainWindow, options);
  return result;
});

ipcMain.handle('show-save-dialog', async (event, options) => {
  const result = await dialog.showSaveDialog(mainWindow, options);
  return result;
});

// App event handlers
app.whenReady().then(() => {
  createWindow();

  app.on('activate', () => {
    // On macOS, re-create window when dock icon is clicked
    if (BrowserWindow.getAllWindows().length === 0) {
      createWindow();
    }
  });
});

app.on('window-all-closed', () => {
  // On macOS, keep app running even when all windows are closed
  if (process.platform !== 'darwin') {
    app.quit();
  }
});

// Security: Prevent new window creation
app.on('web-contents-created', (event, contents) => {
  contents.on('new-window', (event, navigationUrl) => {
    event.preventDefault();
    shell.openExternal(navigationUrl);
  });
});

// Handle protocol for production
if (!isDev) {
  // Set protocol handler for production
  app.setAsDefaultProtocolClient('rails-migration-assistant');
}
