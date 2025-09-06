import React, { useState, useEffect } from 'react';
import { 
  Card, 
  Button, 
  Input, 
  Select, 
  Checkbox, 
  Tabs, 
  Typography, 
  Space, 
  message,
  Progress,
  Row,
  Col,
  Divider,
  Modal
} from 'antd';
import { 
  FolderOpenOutlined, 
  PlayCircleOutlined,
  LeftOutlined,
  RightOutlined,
  CheckOutlined,
  CloseOutlined,
  FastForwardOutlined,
  FileTextOutlined,
  DownloadOutlined
} from '@ant-design/icons';
import Editor from 'react-simple-code-editor';
import Prism from 'prismjs';
import 'prismjs/components/prism-ruby';
import useAppStore from '../stores/appStore';
import { analyzeProject, generateReport, analyzeProjectWithProgress } from '../services/apiClient';

const { Title, Text, Paragraph } = Typography;
const { Option } = Select;
const { TabPane } = Tabs;

const ProjectMode = () => {
  const {
    projectPath,
    targetVersion,
    backupEnabled,
    backupLocation,
    isAnalyzing,
    analysisResults,
    currentSuggestionIndex,
    setProjectPath,
    setTargetVersion,
    setBackupEnabled,
    setBackupLocation,
    setIsAnalyzing,
    setAnalysisResults,
    nextSuggestion,
    previousSuggestion,
    getCurrentSuggestion,
    setError
  } = useAppStore();

  const [reportContent, setReportContent] = useState('');
  const [reportType, setReportType] = useState('summary');
  const [pathModalVisible, setPathModalVisible] = useState(false);
  const [tempPath, setTempPath] = useState('');
  const [pathModalType, setPathModalType] = useState('project'); // 'project' or 'backup'
  const [progressData, setProgressData] = useState(null);

  // Listen for Electron file dialog events
  useEffect(() => {
    console.log('🔧 ProjectMode component mounted');
    console.log('🔧 Available window properties:', Object.keys(window));
    console.log('🔧 window.electronAPI:', window.electronAPI);
    
    if (window.electronAPI) {
      const handleOpenProject = (_, path) => {
        setProjectPath(path);
      };

      window.electronAPI.openProject(handleOpenProject);

      return () => {
        window.electronAPI.removeAllListeners('open-project');
      };
    }
  }, [setProjectPath]);

  const handleBrowseProject = async () => {
    console.log('🔧 Browse project clicked');
    console.log('🔧 window.electronAPI:', window.electronAPI);
    console.log('🔧 window.electronAPI?.showOpenDialog:', window.electronAPI?.showOpenDialog);
    
    if (window.electronAPI && window.electronAPI.showOpenDialog) {
      try {
        console.log('🔧 Using Electron file dialog');
        const result = await window.electronAPI.showOpenDialog({
          properties: ['openDirectory'],
          title: 'Select Rails Project Directory',
          buttonLabel: 'Select Project'
        });
        
        console.log('🔧 Dialog result:', result);
        
        if (!result.canceled && result.filePaths.length > 0) {
          setProjectPath(result.filePaths[0]);
          message.success('Project directory selected successfully!');
        }
      } catch (error) {
        console.error('🔧 File dialog error:', error);
        message.error('Failed to open file dialog. Please enter the path manually.');
        // Use modal dialog instead of prompt
        setTempPath('');
        setPathModalType('project');
        setPathModalVisible(true);
      }
    } else {
      console.log('🔧 Electron API not available, using input method');
      // Use modal dialog instead of prompt
      setTempPath('');
      setPathModalType('project');
      setPathModalVisible(true);
    }
  };

  const handleBrowseBackup = async () => {
    console.log('🔧 Browse backup clicked');
    
    if (window.electronAPI && window.electronAPI.showOpenDialog) {
      try {
        console.log('🔧 Using Electron file dialog for backup');
        const result = await window.electronAPI.showOpenDialog({
          properties: ['openDirectory', 'createDirectory'],
          title: 'Select Backup Location',
          buttonLabel: 'Select Backup Location'
        });
        
        console.log('🔧 Backup dialog result:', result);
        
        if (!result.canceled && result.filePaths.length > 0) {
          setBackupLocation(result.filePaths[0]);
          message.success('Backup location selected successfully!');
        }
      } catch (error) {
        console.error('🔧 Backup dialog error:', error);
        message.error('Failed to open file dialog. Please enter the path manually.');
        setTempPath('');
        setPathModalType('backup');
        setPathModalVisible(true);
      }
    } else {
      console.log('🔧 Electron API not available, using input method for backup');
      setTempPath('');
      setPathModalType('backup');
      setPathModalVisible(true);
    }
  };

  const handlePathModalOk = () => {
    if (tempPath.trim()) {
      if (pathModalType === 'project') {
        setProjectPath(tempPath.trim());
        message.success('Project path set successfully!');
      } else {
        setBackupLocation(tempPath.trim());
        message.success('Backup location set successfully!');
      }
      setPathModalVisible(false);
      setTempPath('');
    } else {
      message.warning('Please enter a valid path.');
    }
  };

  const handlePathModalCancel = () => {
    setPathModalVisible(false);
    setTempPath('');
  };

  const handleAnalyze = async () => {
    if (!projectPath.trim()) {
      message.error('Please select a Rails project directory first.');
      return;
    }

    setIsAnalyzing(true);
    setError(null);
    setProgressData(null);

    try {
      message.info('Starting project analysis...');
      
      const results = await analyzeProjectWithProgress({
        path: projectPath,
        target_version: targetVersion,
        backup_enabled: backupEnabled,
        backup_location: backupLocation
      }, (progress) => {
        // Handle real-time progress updates
        setProgressData(progress);
        
        if (progress.status === 'starting') {
          message.info(progress.message);
        } else if (progress.status === 'analyzing') {
          // Update progress bar in real-time
          console.log(`Progress: ${progress.progress}% - ${progress.current_file}`);
        } else if (progress.status === 'completed') {
          message.success(progress.message);
        }
      });

      setAnalysisResults(results.data);
      
      if (results.data.total_suggestions > 0) {
        message.success(`Analysis complete! Found ${results.data.total_suggestions} suggestions.`);
      } else {
        message.success('Analysis complete! No issues found.');
      }
    } catch (error) {
      console.error('Analysis failed:', error);
      setError(error.message);
      message.error('Analysis failed. Please check the console for details.');
    } finally {
      setIsAnalyzing(false);
      setProgressData(null);
    }
  };

  const handleDemoAnalysis = async () => {
    setIsAnalyzing(true);
    setError(null);

    try {
      message.info('Loading demo analysis results...');
      
      // Call the demo endpoint
      const response = await fetch('http://localhost:8000/api/analyze/project/demo', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' }
      });
      
      if (!response.ok) {
        throw new Error(`Demo failed: ${response.statusText}`);
      }
      
      const results = await response.json();
      setAnalysisResults(results.data);
      
      message.success(`Demo analysis loaded! Found ${results.data.total_suggestions} example suggestions.`);
    } catch (error) {
      console.error('Demo analysis failed:', error);
      setError(error.message);
      message.error('Demo analysis failed. Please check if the backend is running.');
    } finally {
      setIsAnalyzing(false);
    }
  };

  const handleGenerateReport = async () => {
    if (!analysisResults) {
      message.warning('Please run an analysis first.');
      return;
    }

    try {
      const report = await generateReport({
        type: reportType,
        analysis_data: analysisResults
      });
      
      setReportContent(report.report);
      message.success('Report generated successfully!');
    } catch (error) {
      console.error('Report generation failed:', error);
      message.error('Failed to generate report.');
    }
  };

  const handleExportReport = async () => {
    if (!reportContent) {
      message.warning('Please generate a report first.');
      return;
    }

    if (window.electronAPI && window.electronAPI.showSaveDialog) {
      try {
        const result = await window.electronAPI.showSaveDialog({
          title: 'Export Analysis Report',
          defaultPath: `rails_analysis_report_${new Date().toISOString().split('T')[0]}.txt`,
          filters: [
            { name: 'Text Files', extensions: ['txt'] },
            { name: 'Markdown Files', extensions: ['md'] },
            { name: 'All Files', extensions: ['*'] }
          ]
        });
        
        if (!result.canceled && result.filePath) {
          // In a full Electron app, you would write the file here using Node.js fs
          // For now, we'll use the blob download method as a fallback
          const blob = new Blob([reportContent], { type: 'text/plain' });
          const url = URL.createObjectURL(blob);
          const a = document.createElement('a');
          a.href = url;
          a.download = result.filePath.split('/').pop() || 'report.txt';
          document.body.appendChild(a);
          a.click();
          document.body.removeChild(a);
          URL.revokeObjectURL(url);
          
          message.success('Report exported successfully!');
        }
      } catch (error) {
        console.error('Save dialog error:', error);
        message.error('Failed to open save dialog. Using default download.');
        // Fallback to original method
        const blob = new Blob([reportContent], { type: 'text/plain' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `rails_analysis_report_${new Date().toISOString().split('T')[0]}.txt`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
        message.success('Report exported successfully!');
      }
    } else {
      // Fallback for non-Electron environments
      const blob = new Blob([reportContent], { type: 'text/plain' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `rails_analysis_report_${new Date().toISOString().split('T')[0]}.txt`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
      
      message.success('Report exported successfully!');
    }
  };

  // Defensive: Ensure currentSuggestion is always an object, not undefined/null
  const currentSuggestion = getCurrentSuggestion() || {};
  const hasSuggestions = analysisResults?.suggestions && analysisResults.suggestions.length > 0;

  // Helper to get code fields regardless of backend naming
  const getCodeField = (obj, key1, key2, fallback) => {
    if (typeof obj[key1] === 'string' && obj[key1].trim() !== '') return obj[key1];
    if (typeof obj[key2] === 'string' && obj[key2].trim() !== '') return obj[key2];
    return fallback;
  };

  // Handler to accept suggestion
  const handleAcceptSuggestion = () => {
    if (!hasSuggestions) return;
    // Defensive: clone results to avoid direct mutation
    const updatedResults = { ...analysisResults };
    const idx = currentSuggestionIndex;
    if (updatedResults.suggestions && updatedResults.suggestions[idx]) {
      updatedResults.suggestions[idx] = {
        ...updatedResults.suggestions[idx],
        status: 'accepted',
      };
      // Preserve currentSuggestionIndex when updating results
      setAnalysisResults({ ...updatedResults });
      // Manually preserve index after update
      useAppStore.getState().setCurrentSuggestionIndex(idx);
      nextSuggestion();
      message.success('Suggestion accepted!');
    }
  };

  // Handler to reject suggestion
  const handleRejectSuggestion = () => {
    if (!hasSuggestions) return;
    const updatedResults = { ...analysisResults };
    const idx = currentSuggestionIndex;
    if (updatedResults.suggestions && updatedResults.suggestions[idx]) {
      updatedResults.suggestions[idx] = {
        ...updatedResults.suggestions[idx],
        status: 'rejected',
      };
      setAnalysisResults({ ...updatedResults });
      useAppStore.getState().setCurrentSuggestionIndex(idx);
      nextSuggestion();
      message.info('Suggestion rejected.');
    }
  };

  return (
    <div className="fade-in" style={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
      {/* Project Configuration */}
      <Card title="🔧 Project Configuration" style={{ marginBottom: '16px' }}>
        <Row gutter={[16, 16]}>
          <Col xs={24} lg={12}>
            <Space direction="vertical" size="middle" style={{ width: '100%' }}>
              <div>
                <Text strong>Rails Project Directory</Text>
                <Space.Compact style={{ width: '100%', marginTop: '4px' }}>
                  <Input
                    placeholder="Select Rails project directory..."
                    value={projectPath}
                    onChange={(e) => setProjectPath(e.target.value)}
                    style={{ flex: 1 }}
                  />
                  <Button 
                    icon={<FolderOpenOutlined />} 
                    onClick={handleBrowseProject}
                  >
                    Browse
                  </Button>
                </Space.Compact>
              </div>

              <div>
                <Text strong>Target Rails Version</Text>
                <Select
                  value={targetVersion}
                  onChange={setTargetVersion}
                  style={{ width: '100%', marginTop: '4px' }}
                >
                  <Option value="6.0">Rails 6.0</Option>
                  <Option value="6.1">Rails 6.1</Option>
                  <Option value="7.0">Rails 7.0</Option>
                  <Option value="7.1">Rails 7.1</Option>
                </Select>
              </div>
            </Space>
          </Col>

          <Col xs={24} lg={12}>
            <Space direction="vertical" size="middle" style={{ width: '100%' }}>
              <div>
                <Checkbox
                  checked={backupEnabled}
                  onChange={(e) => setBackupEnabled(e.target.checked)}
                >
                  <Text strong>Create backup before changes</Text>
                </Checkbox>
              </div>

              {backupEnabled && (
                <div>
                  <Text strong>Backup Location</Text>
                  <Space.Compact style={{ width: '100%', marginTop: '4px' }}>
                    <Input
                      placeholder="Choose backup location..."
                      value={backupLocation}
                      onChange={(e) => setBackupLocation(e.target.value)}
                      style={{ flex: 1 }}
                    />
                    <Button 
                      icon={<FolderOpenOutlined />} 
                      onClick={handleBrowseBackup}
                    >
                      Browse
                    </Button>
                  </Space.Compact>
                </div>
              )}

              <Button
                type="primary"
                size="large"
                icon={<PlayCircleOutlined />}
                onClick={handleAnalyze}
                loading={isAnalyzing}
                disabled={!projectPath.trim()}
                style={{ width: '100%', marginBottom: '8px' }}
              >
                {isAnalyzing ? 'Analyzing Project...' : 'Analyze Project'}
              </Button>
              
      {/* Spinner/Progress for long-running analysis */}
      {isAnalyzing && (
        <div style={{ textAlign: 'center', margin: '32px 0' }}>
          <Progress 
            type="line" 
            percent={progressData?.progress || 0}
            status="active"
            style={{ width: 400, maxWidth: '90%' }}
          />
          <Text type="secondary" style={{ display: 'block', marginTop: 16 }}>
            {progressData?.message || 'Analyzing project... This may take several minutes.'}
          </Text>
          {progressData?.current_file && (
            <Text type="secondary" style={{ display: 'block', marginTop: 8, fontSize: '12px' }}>
              Current file: {progressData.current_file}
            </Text>
          )}
          {progressData?.analyzed_files && progressData?.total_files && (
            <Text type="secondary" style={{ display: 'block', marginTop: 8, fontSize: '12px' }}>
              Files analyzed: {progressData.analyzed_files} / {progressData.total_files}
            </Text>
          )}
        </div>
      )}
              
              <Button
                type="default"
                size="small"
                onClick={() => window.location.reload()}
                style={{ width: '100%' }}
              >
                🔄 Force Refresh (if buttons broken)
              </Button>
            </Space>
          </Col>
        </Row>
      </Card>

      {/* Analysis Results */}
      <Card 
        title="📊 Analysis Results" 
        style={{ flex: 1, display: 'flex', flexDirection: 'column' }}
        bodyStyle={{ flex: 1, display: 'flex', flexDirection: 'column' }}
      >
        <Tabs 
          defaultActiveKey="review" 
          style={{ flex: 1, display: 'flex', flexDirection: 'column' }}
          tabBarStyle={{ marginBottom: '16px' }}
        >
          <TabPane 
            tab="📝 Code Review" 
            key="review"
            style={{ flex: 1, display: 'flex', flexDirection: 'column' }}
          >
            {hasSuggestions ? (
              <div style={{ flex: 1, display: 'flex', flexDirection: 'column' }}>
                {/* Navigation */}
                <div style={{ 
                  display: 'flex', 
                  justifyContent: 'space-between', 
                  alignItems: 'center',
                  marginBottom: '16px',
                  padding: '12px',
                  background: '#f5f5f5',
                  borderRadius: '6px'
                }}>
                  <Button 
                    icon={<LeftOutlined />}
                    onClick={previousSuggestion}
                    disabled={currentSuggestionIndex === 0}
                  >
                    Previous
                  </Button>
                  
                  <Text strong>
                    Suggestion {currentSuggestionIndex + 1} of {analysisResults.suggestions.length}
                  </Text>
                  
                  <Button 
                    icon={<RightOutlined />}
                    onClick={nextSuggestion}
                    disabled={currentSuggestionIndex === analysisResults.suggestions.length - 1}
                  >
                    Next
                  </Button>
                </div>

                {currentSuggestion && (
                  <>
                    {/* File Info */}
                    <Card size="small" style={{ marginBottom: '16px' }}>
                      <Text strong>📁 File: </Text>
                      <Text code>{currentSuggestion.file || currentSuggestion.file_path || 'Unknown file'}</Text>
                      <Divider type="vertical" />
                      <Text strong>Issue: </Text>
                      <Text>{currentSuggestion.issue_type || 'Unknown issue'}</Text>
                      <Divider type="vertical" />
                      <Text strong>Confidence: </Text>
                      <Text>{((currentSuggestion.confidence || 0) * 100).toFixed(1)}%</Text>
                      <Divider type="vertical" />
                      <Text strong>Status: </Text>
                      <Text>{currentSuggestion.status || 'pending'}</Text>
                    </Card>

                    {/* Code Comparison */}
                    <Row gutter={16} style={{ flex: 1, marginBottom: '16px' }}>
                      <Col span={12} style={{ display: 'flex', flexDirection: 'column' }}>
                        <Text strong style={{ marginBottom: '8px' }}>📄 Current Code</Text>
                        <div style={{ flex: 1, border: '1px solid #d9d9d9', borderRadius: '6px', minHeight: 300, background: '#f5f5f5' }}>
                          <Editor
                            value={getCodeField(currentSuggestion, 'original_code', 'old_code', 'No code available')}
                            onValueChange={() => {}}
                            highlight={code => Prism.highlight(code, Prism.languages.ruby, 'ruby')}
                            padding={10}
                            style={{
                              fontFamily: 'monospace',
                              fontSize: 13,
                              background: '#f5f5f5',
                              borderRadius: 6,
                              minHeight: 300,
                            }}
                            readOnly
                          />
                        </div>
                      </Col>
                      
                      <Col span={12} style={{ display: 'flex', flexDirection: 'column' }}>
                        <Text strong style={{ marginBottom: '8px' }}>✨ Suggested Code</Text>
                        <div style={{ flex: 1, border: '1px solid #d9d9d9', borderRadius: '6px', minHeight: 300, background: '#f5f5f5' }}>
                          <Editor
                            value={getCodeField(currentSuggestion, 'refactored_code', 'new_code', 'No suggestion available')}
                            onValueChange={() => {}}
                            highlight={code => Prism.highlight(code, Prism.languages.ruby, 'ruby')}
                            padding={10}
                            style={{
                              fontFamily: 'monospace',
                              fontSize: 13,
                              background: '#f5f5f5',
                              borderRadius: 6,
                              minHeight: 300,
                            }}
                            readOnly
                          />
                        </div>
                      </Col>
                    </Row>

                    {/* Explanation */}
                    <Card 
                      title="📋 Explanation" 
                      size="small" 
                      style={{ marginBottom: '16px' }}
                    >
                      <Paragraph>
                        {currentSuggestion.explanation || 'No explanation available'}
                      </Paragraph>
                    </Card>

                    {/* Action Buttons */}
                    <Space>
                      <Button type="primary" icon={<CheckOutlined />} onClick={handleAcceptSuggestion}>
                        Accept
                      </Button>
                      <Button danger icon={<CloseOutlined />} onClick={handleRejectSuggestion}>
                        Reject
                      </Button>
                      <Button icon={<FastForwardOutlined />} onClick={nextSuggestion}>
                        Skip
                      </Button>
                    </Space>
                  </>
                )}
              </div>
            ) : (
              <div style={{ 
                display: 'flex', 
                flexDirection: 'column', 
                alignItems: 'center', 
                justifyContent: 'center',
                height: '300px',
                color: '#999'
              }}>
                <FileTextOutlined style={{ fontSize: '48px', marginBottom: '16px' }} />
                <Text style={{ fontSize: '16px', color: '#999' }}>
                  {analysisResults ? 'No suggestions found. Your project is up to date!' : 'Run an analysis to see code suggestions'}
                </Text>
              </div>
            )}
          </TabPane>

          <TabPane tab="📊 Analysis Summary" key="analysis">
            {analysisResults && typeof analysisResults === 'object' ? (
              <div>
                <Row gutter={[16, 16]} style={{ marginBottom: '24px' }}>
                  <Col xs={24} sm={8}>
                    <Card>
                      <div style={{ textAlign: 'center' }}>
                        <Title level={2} style={{ color: '#1890ff', margin: 0 }}>
                          {analysisResults.total_suggestions ?? 0}
                        </Title>
                        <Text>Total Suggestions</Text>
                      </div>
                    </Card>
                  </Col>
                  <Col xs={24} sm={8}>
                    <Card>
                      <div style={{ textAlign: 'center' }}>
                        <Title level={2} style={{ color: '#52c41a', margin: 0 }}>
                          {analysisResults.target_version ?? targetVersion}
                        </Title>
                        <Text>Target Version</Text>
                      </div>
                    </Card>
                  </Col>
                  <Col xs={24} sm={8}>
                    <Card>
                      <div style={{ textAlign: 'center' }}>
                        <Title level={2} style={{ color: '#faad14', margin: 0 }}>
                          {analysisResults.analysis_timestamp ? new Date(analysisResults.analysis_timestamp).toLocaleDateString() : ''}
                        </Title>
                        <Text>Analysis Date</Text>
                      </div>
                    </Card>
                  </Col>
                </Row>
                <Card title="Project Information">
                  <Paragraph>
                    <Text strong>Project Path: </Text>
                    <Text code>{analysisResults.project_path ?? ''}</Text>
                  </Paragraph>
                  <Paragraph>
                    <Text strong>Target Rails Version: </Text>
                    <Text>{analysisResults.target_version ?? targetVersion}</Text>
                  </Paragraph>
                  <Paragraph>
                    <Text strong>Analysis Status: </Text>
                    <Text style={{ color: '#52c41a' }}>{analysisResults.status ?? ''}</Text>
                  </Paragraph>
                </Card>
              </div>
            ) : (
              <div style={{ 
                display: 'flex', 
                flexDirection: 'column', 
                alignItems: 'center', 
                justifyContent: 'center',
                height: '300px',
                color: '#999'
              }}>
                <PlayCircleOutlined style={{ fontSize: '48px', marginBottom: '16px' }} />
                <Text style={{ fontSize: '16px', color: '#999' }}>
                  Run an analysis to see detailed results
                </Text>
              </div>
            )}
          </TabPane>

          <TabPane tab="📋 Reports" key="reports">
            <Space direction="vertical" size="large" style={{ width: '100%' }}>
              <Card title="Report Generation" size="small">
                <Row gutter={16} align="middle">
                  <Col span={8}>
                    <Text strong>Report Type:</Text>
                    <Select
                      value={reportType}
                      onChange={setReportType}
                      style={{ width: '100%', marginTop: '4px' }}
                    >
                      <Option value="summary">Summary Report</Option>
                      <Option value="detailed">Detailed Report</Option>
                    </Select>
                  </Col>
                  <Col span={8}>
                    <Button 
                      type="primary"
                      icon={<FileTextOutlined />}
                      onClick={handleGenerateReport}
                      disabled={!analysisResults}
                      style={{ width: '100%' }}
                    >
                      Generate Report
                    </Button>
                  </Col>
                  <Col span={8}>
                    <Button 
                      icon={<DownloadOutlined />}
                      onClick={handleExportReport}
                      disabled={!reportContent}
                      style={{ width: '100%' }}
                    >
                      Export Report
                    </Button>
                  </Col>
                </Row>
              </Card>

              {typeof reportContent === 'string' && reportContent.trim() !== '' ? (
                <Card title="Generated Report" size="small">
                  <div style={{ 
                    background: '#f5f5f5', 
                    padding: '16px', 
                    borderRadius: '6px',
                    fontFamily: 'monospace',
                    whiteSpace: 'pre-wrap',
                    maxHeight: '400px',
                    overflow: 'auto'
                  }}>
                    {reportContent}
                  </div>
                </Card>
              ) : null}
            </Space>
          </TabPane>
        </Tabs>
      </Card>

      {/* Path Input Modal */}
      <Modal
        title={pathModalType === 'project' ? 'Enter Rails Project Path' : 'Enter Backup Location'}
        open={pathModalVisible}
        onOk={handlePathModalOk}
        onCancel={handlePathModalCancel}
        okText="Select"
        cancelText="Cancel"
      >
        <Space direction="vertical" style={{ width: '100%' }}>
          <Typography.Text>
            {pathModalType === 'project' 
              ? 'Please enter the full path to your Rails project directory:'
              : 'Please enter the full path where you want to store backups:'
            }
          </Typography.Text>
          <Input
            placeholder={pathModalType === 'project' 
              ? "e.g., C:\\path\\to\\rails\\project" 
              : "e.g., C:\\path\\to\\backup\\folder"
            }
            value={tempPath}
            onChange={(e) => setTempPath(e.target.value)}
            onPressEnter={handlePathModalOk}
          />
          <Typography.Text type="secondary" style={{ fontSize: '12px' }}>
            {pathModalType === 'project' 
              ? 'The directory should contain a Gemfile and typical Rails structure.'
              : 'This directory will be used to store backup files before making changes.'
            }
          </Typography.Text>
        </Space>
      </Modal>
    </div>
  );
};

export default ProjectMode;
