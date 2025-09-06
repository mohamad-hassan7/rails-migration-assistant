import axios from 'axios';

// Create axios instance with base configuration
const apiClient = axios.create({
  baseURL: 'http://localhost:8000',
  timeout: 30000, // Default 30 seconds timeout for regular requests
  headers: {
    'Content-Type': 'application/json',
  },
  maxContentLength: Infinity,
  maxBodyLength: Infinity,
});

// Request interceptor for logging
apiClient.interceptors.request.use(
  (config) => {
    console.log(`🔵 API Request: ${config.method?.toUpperCase()} ${config.url}`);
    return config;
  },
  (error) => {
    console.error('🔴 API Request Error:', error);
    return Promise.reject(error);
  }
);

// Response interceptor for logging and error handling
apiClient.interceptors.response.use(
  (response) => {
    console.log(`🟢 API Response: ${response.status} ${response.config.url}`);
    console.log(`📊 Response size: ${JSON.stringify(response.data).length} characters`);
    console.log('📋 Response headers:', response.headers);
    console.log('📄 Response data structure:', {
      hasData: !!response.data,
      dataKeys: response.data ? Object.keys(response.data) : [],
      dataType: typeof response.data
    });
    return response;
  },
  (error) => {
    console.error('🔴 API Response Error Details:', {
      name: error.name,
      message: error.message,
      code: error.code,
      stack: error.stack,
      config: error.config,
      request: !!error.request,
      response: !!error.response,
      responseStatus: error.response?.status,
      responseData: error.response?.data,
      responseHeaders: error.response?.headers
    });
    
    // Handle different error types
    if (error.code === 'ECONNREFUSED' || error.message.includes('Network Error')) {
      throw new Error('Cannot connect to API server. Please ensure the backend is running on http://localhost:8000');
    }
    
    if (error.response) {
      // Server responded with error status
      const { status, data } = error.response;
      const message = data?.detail || data?.error || `Server error: ${status}`;
      throw new Error(message);
    }
    
    if (error.request) {
      // Request was made but no response received
      console.error('🔴 No response received. Request details:', {
        url: error.config?.url,
        method: error.config?.method,
        timeout: error.config?.timeout,
        readyState: error.request.readyState,
        status: error.request.status,
        statusText: error.request.statusText
      });
      throw new Error('No response from server. Please check your connection.');
    }
    
    // Something else happened
    throw new Error(error.message || 'An unexpected error occurred');
  }
);

// API endpoints
export const healthCheck = async () => {
  const response = await apiClient.get('/health');
  return response.data;
};

export const getApiStatus = async () => {
  const response = await apiClient.get('/api/analysis/status');
  return response.data;
};

export const analyzeProject = async (projectData) => {
  // Increase timeout to 20 minutes (1200 seconds)
  const response = await apiClient.post('/api/analyze/project', projectData, {
    timeout: 1200000 // 20 minutes
  });
  return response.data;
};

export const analyzeProjectWithProgress = async (projectData, onProgress) => {
  const response = await fetch('http://localhost:8000/api/analyze/project/stream', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(projectData),
  });

  if (!response.ok) {
    throw new Error(`Analysis failed: ${response.statusText}`);
  }

  const reader = response.body.getReader();
  const decoder = new TextDecoder();
  let buffer = '';

  try {
    while (true) {
      const { done, value } = await reader.read();
      
      if (done) break;
      
      buffer += decoder.decode(value, { stream: true });
      
      // Process complete lines
      const lines = buffer.split('\n');
      buffer = lines.pop(); // Keep incomplete line in buffer
      
      for (const line of lines) {
        if (line.startsWith('data: ')) {
          try {
            const data = JSON.parse(line.slice(6));
            if (onProgress) {
              onProgress(data);
            }
            
            // Return final results when completed
            if (data.status === 'completed' && data.results) {
              return {
                status: 'success',
                data: data.results
              };
            }
            
            // Handle errors
            if (data.status === 'error') {
              throw new Error(data.error || 'Analysis failed');
            }
          } catch (parseError) {
            console.warn('Failed to parse SSE data:', line);
          }
        }
      }
    }
  } finally {
    reader.releaseLock();
  }
  
  throw new Error('Analysis completed without final results');
};

export const askQuestion = async (queryData) => {
  try {
    console.log('🔵 Sending question to API:', queryData);
    console.log('🔵 Request config: timeout=120000ms, baseURL=http://localhost:8000');
    
    const startTime = Date.now();
    
    // Use longer timeout specifically for AI queries (10 minutes)
    const response = await apiClient.post('/api/query/ask', queryData, {
      timeout: 600000, // 10 minutes for AI generation
      maxContentLength: Infinity, // Allow large responses
      maxBodyLength: Infinity,
      validateStatus: function (status) {
        return status >= 200 && status < 300; // default
      },
    });
    
    const duration = Date.now() - startTime;
    console.log('🟢 Received response from API:', {
      status: response.status,
      statusText: response.statusText,
      headers: response.headers,
      dataKeys: Object.keys(response.data || {}),
      answerLength: response.data?.answer?.length || 0,
      duration: `${duration}ms`,
      responseSize: JSON.stringify(response.data).length
    });
    
    // Validate response structure
    if (!response.data) {
      throw new Error('Empty response data from server');
    }
    
    if (!response.data.answer) {
      console.warn('⚠️ Response missing answer field:', response.data);
      throw new Error('Invalid response format: missing answer field');
    }
    
    return response.data;
  } catch (error) {
    console.error('🔴 API Error in askQuestion:', error);
    console.error('🔴 Error code:', error.code);
    console.error('🔴 Error message:', error.message);
    
    // Check if it's a network error
    if (error.code === 'ECONNREFUSED' || error.message.includes('ECONNREFUSED')) {
      throw new Error('Cannot connect to API server. Please ensure the backend is running on http://localhost:8000');
    }
    
    // Check if it's a timeout
    if (error.code === 'ECONNABORTED' || error.message.includes('timeout')) {
      console.error('🔴 Request timed out after 120 seconds');
      throw new Error('AI response timeout. The model is taking longer than expected. Please try a simpler question or try again later.');
    }
    
    // Check for server errors
    if (error.response?.status >= 500) {
      throw new Error(`Server error: ${error.response.statusText}`);
    }
    
    // Check if no response was received
    if (error.request && !error.response) {
      console.error('🔴 No response received from server');
      throw new Error('No response from server. The connection may have been lost during AI processing.');
    }
    
    // Generic error
    throw new Error(error.response?.data?.detail || error.message || 'Unknown API error');
  }
};

export const generateReport = async (reportData) => {
  const response = await apiClient.post('/api/reports/generate', reportData);
  return response.data;
};

// Utility function to check if API is available
export const checkApiConnection = async () => {
  try {
    console.log('🔵 Testing API connection...');
    await healthCheck();
    console.log('🟢 API connection successful');
    return { connected: true, error: null };
  } catch (error) {
    console.error('🔴 API connection failed:', error);
    let errorMessage = 'Connection failed';
    
    if (error.code === 'ECONNREFUSED' || error.message.includes('ECONNREFUSED')) {
      errorMessage = 'Cannot connect to API server. Please ensure the backend is running on http://localhost:8000';
    } else if (error.code === 'ECONNABORTED') {
      errorMessage = 'Connection timeout. Server might be starting up.';
    }
    
    return { connected: false, error: errorMessage };
  }
};

// Helper function to handle file uploads (if needed in the future)
export const uploadFile = async (file, endpoint) => {
  const formData = new FormData();
  formData.append('file', file);
  
  const response = await apiClient.post(endpoint, formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  });
  
  return response.data;
};

export default apiClient;
