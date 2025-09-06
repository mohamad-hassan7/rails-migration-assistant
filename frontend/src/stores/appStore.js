import { create } from 'zustand';

const useAppStore = create((set, get) => ({
  // Navigation state
  currentPage: 'welcome',
  setCurrentPage: (page) => set({ currentPage: page }),

  // Project analysis state
  projectPath: '',
  targetVersion: '7.0',
  backupEnabled: true,
  backupLocation: '',
  isAnalyzing: false,
  analysisResults: null,
  currentSuggestionIndex: 0,

  setProjectPath: (path) => set({ projectPath: path }),
  setTargetVersion: (version) => set({ targetVersion: version }),
  setBackupEnabled: (enabled) => set({ backupEnabled: enabled }),
  setBackupLocation: (location) => set({ backupLocation: location }),
  setIsAnalyzing: (analyzing) => set({ isAnalyzing: analyzing }),
  setAnalysisResults: (results) => set({ 
    analysisResults: results,
    currentSuggestionIndex: 0 
  }),
  setCurrentSuggestionIndex: (index) => set({ currentSuggestionIndex: index }),

  // Navigation helpers
  navigateToProject: () => set({ currentPage: 'project' }),
  navigateToQuery: () => set({ currentPage: 'query' }),
  navigateToWelcome: () => set({ currentPage: 'welcome' }),

  // Analysis helpers
  nextSuggestion: () => {
    const { analysisResults, currentSuggestionIndex } = get();
    if (analysisResults?.suggestions && currentSuggestionIndex < analysisResults.suggestions.length - 1) {
      set({ currentSuggestionIndex: currentSuggestionIndex + 1 });
    }
  },

  previousSuggestion: () => {
    const { currentSuggestionIndex } = get();
    if (currentSuggestionIndex > 0) {
      set({ currentSuggestionIndex: currentSuggestionIndex - 1 });
    }
  },

  getCurrentSuggestion: () => {
    const { analysisResults, currentSuggestionIndex } = get();
    return analysisResults?.suggestions?.[currentSuggestionIndex] || null;
  },

  // Query mode state
  chatMessages: [],
  isProcessingQuery: false,

  addChatMessage: (message) => set(state => ({
    chatMessages: [...state.chatMessages, {
      ...message,
      id: Date.now(),
      timestamp: new Date().toISOString()
    }]
  })),

  clearChatMessages: () => set({ chatMessages: [] }),
  setIsProcessingQuery: (processing) => set({ isProcessingQuery: processing }),

  // UI state
  sidebarCollapsed: false,
  theme: 'light',
  
  toggleSidebar: () => set(state => ({ sidebarCollapsed: !state.sidebarCollapsed })),
  setTheme: (theme) => set({ theme }),

  // API state
  apiStatus: 'unknown', // 'connected', 'disconnected', 'unknown'
  setApiStatus: (status) => set({ apiStatus: status }),

  // Error handling
  error: null,
  setError: (error) => set({ error }),
  clearError: () => set({ error: null }),

  // Loading states
  loadingStates: {},
  setLoading: (key, loading) => set(state => ({
    loadingStates: { ...state.loadingStates, [key]: loading }
  })),
  
  isLoading: (key) => get().loadingStates[key] || false,

  // Reset functions
  resetProjectState: () => set({
    projectPath: '',
    targetVersion: '7.0',
    backupEnabled: true,
    backupLocation: '',
    isAnalyzing: false,
    analysisResults: null,
    currentSuggestionIndex: 0,
  }),

  resetQueryState: () => set({
    chatMessages: [],
    isProcessingQuery: false,
  }),

  resetAll: () => set({
    currentPage: 'welcome',
    projectPath: '',
    targetVersion: '7.0',
    backupEnabled: true,
    backupLocation: '',
    isAnalyzing: false,
    analysisResults: null,
    currentSuggestionIndex: 0,
    chatMessages: [],
    isProcessingQuery: false,
    error: null,
    loadingStates: {},
  }),
}));

export default useAppStore;
