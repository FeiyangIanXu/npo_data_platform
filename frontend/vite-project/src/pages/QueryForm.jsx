import React, { useState, useEffect } from 'react';
import { 
  Form, 
  Input, 
  Button, 
  Card, 
  Row, 
  Col, 
  Select, 
  Steps,
  Typography, 
  Divider,
  message,
  Spin,
  Table,
  Checkbox,
  InputNumber,
  Radio,
  Space,
  Tag,
  Alert,
  Collapse,
  Tooltip,
  Progress,
  Modal,
  Transfer,
  List,
  Badge
} from 'antd';
import { 
  SearchOutlined, 
  FilterOutlined, 
  DatabaseOutlined,
  ExportOutlined,
  InfoCircleOutlined,
  CheckCircleOutlined,
  RightOutlined,
  LeftOutlined,
  ClearOutlined,
  DownloadOutlined,
  EnvironmentOutlined,
  DollarOutlined,
  TeamOutlined,
  FileTextOutlined
} from '@ant-design/icons';
import axios from 'axios';

const { Title, Text, Paragraph } = Typography;
const { Option } = Select;
const { Panel } = Collapse;
const { Step } = Steps;

const QueryForm = () => {
  // 当前步骤
  const [currentStep, setCurrentStep] = useState(0);
  
  // 加载状态
  const [loading, setLoading] = useState(false);
  const [stepLoading, setStepLoading] = useState(false);
  
  // 数据状态
  const [availableYears, setAvailableYears] = useState([]);
  const [availableStates, setAvailableStates] = useState([]);
  const [availableCities, setAvailableCities] = useState([]);
  const [fieldInfo, setFieldInfo] = useState({ categories: {}, fields: [] });
  
  // 查询状态
  const [queryState, setQueryState] = useState({
    selectedYear: null,
    step1Filters: {
      states: [],
      cities: [],
      revenueMin: null,
      revenueMax: null,
      assetsMin: null,
      assetsMax: null,
      iluMin: null,
      aluMin: null
    },
    step2Filters: {
      selectionMode: 'all', // 'all' or 'specific'
      searchTerms: '',
      selectedOrganizations: []
    },
    selectedFields: [],
    finalData: null
  });
  
  // 步骤结果
  const [stepResults, setStepResults] = useState({
    step1Count: 0,
    step2Count: 0,
    step2Organizations: []
  });

  // 初始化数据
  useEffect(() => {
    loadInitialData();
  }, []);

  const loadInitialData = async () => {
    setLoading(true);
    try {
      // 加载可用年份
      const yearsResponse = await axios.get('/api/available-years');
      setAvailableYears(yearsResponse.data.years || []);
      
      // 加载字段信息
      const fieldsResponse = await axios.get('/api/field-info');
      setFieldInfo(fieldsResponse.data);
      
    } catch (error) {
      console.error('加载初始数据失败:', error);
      message.error('加载系统数据失败，请检查后端连接');
    } finally {
      setLoading(false);
    }
  };

  // 步骤1：年份选择
  const handleYearSelect = (year) => {
    setQueryState(prev => ({ ...prev, selectedYear: year }));
    setCurrentStep(1);
  };

  // 步骤2：范围筛选
  const handleStep1Submit = async () => {
    setStepLoading(true);
    try {
      const response = await axios.post('/api/step1-filter', {
        year: queryState.selectedYear,
        filters: queryState.step1Filters
      });
      
      setStepResults(prev => ({ 
        ...prev, 
        step1Count: response.data.count,
        step1Data: response.data.data 
      }));
      
      setCurrentStep(2);
      message.success(`筛选完成，找到 ${response.data.count} 个组织`);
      
    } catch (error) {
      console.error('范围筛选失败:', error);
      message.error('范围筛选失败，请检查筛选条件');
    } finally {
      setStepLoading(false);
    }
  };

  // 步骤3：精确定位
  const handleStep2Submit = async () => {
    setStepLoading(true);
    try {
      const response = await axios.post('/api/step2-filter', {
        year: queryState.selectedYear,
        step1Filters: queryState.step1Filters,
        step2Filters: queryState.step2Filters
      });
      
      setStepResults(prev => ({ 
        ...prev, 
        step2Count: response.data.count,
        step2Organizations: response.data.organizations || []
      }));
      
      setCurrentStep(3);
      message.success(`精确定位完成，最终选择 ${response.data.count} 个组织`);
      
    } catch (error) {
      console.error('精确定位失败:', error);
      message.error('精确定位失败，请检查选择条件');
    } finally {
      setStepLoading(false);
    }
  };

  // 步骤4：变量选择
  const handleStep3Submit = () => {
    if (queryState.selectedFields.length === 0) {
      message.warning('请至少选择一个数据字段');
      return;
    }
    setCurrentStep(4);
  };

  // 步骤5：数据导出
  const handleFinalQuery = async (format = 'xlsx') => {
    setStepLoading(true);
    try {
      const response = await axios.post('/api/final-query', {
        year: queryState.selectedYear,
        step1Filters: queryState.step1Filters,
        step2Filters: queryState.step2Filters,
        selectedFields: queryState.selectedFields,
        format: format
      });
      
      setQueryState(prev => ({ ...prev, finalData: response.data }));
      
      // 如果是文件下载
      if (response.data.download_url) {
        const link = document.createElement('a');
        link.href = response.data.download_url;
        link.download = `nonprofit_data_${queryState.selectedYear}.${format}`;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
      }
      
      message.success(`数据导出成功！共 ${response.data.record_count} 条记录`);
      
    } catch (error) {
      console.error('数据导出失败:', error);
      message.error('数据导出失败，请重试');
    } finally {
      setStepLoading(false);
    }
  };

  // 渲染步骤内容
  const renderStepContent = () => {
    switch (currentStep) {
      case 0:
        return <Step0YearSelect />;
      case 1:
        return <Step1RangeFilter />;
      case 2:
        return <Step2PreciseSelection />;
      case 3:
        return <Step3VariableSelection />;
      case 4:
        return <Step4DataExport />;
      default:
        return <Step0YearSelect />;
    }
  };

  // 步骤0：年份选择
  const Step0YearSelect = () => (
    <Card title="步骤 1: 选择数据年份" style={{ marginBottom: 16 }}>
      <Space direction="vertical" size="large" style={{ width: '100%' }}>
        <div>
          <Title level={4}>
            <DatabaseOutlined /> 选择要查询的数据年度
          </Title>
          <Paragraph>
            请选择您要查询的数据年份。系统将根据选择的年份加载相应的筛选选项。
          </Paragraph>
        </div>

        <div>
          <Title level={5}>可用年份</Title>
          <Row gutter={[16, 16]}>
            {availableYears.map(year => (
              <Col key={year} xs={24} sm={12} md={8} lg={6}>
                <Card
                  hoverable
                  style={{ textAlign: 'center', cursor: 'pointer' }}
                  onClick={() => handleYearSelect(year)}
                >
                  <Title level={3} style={{ margin: 0, color: '#1890ff' }}>
                    {year}
                  </Title>
                  <Text type="secondary">年度数据</Text>
                </Card>
              </Col>
            ))}
          </Row>
        </div>

        <Alert
          message="数据说明"
          description="当前系统包含2022-2024年度的非营利组织数据，共201个组织的164个字段信息。"
          type="info"
          showIcon
        />
      </Space>
    </Card>
  );

  // 步骤1：范围筛选
  const Step1RangeFilter = () => (
    <Card title="步骤 2: 范围筛选 (Universe Screening)" style={{ marginBottom: 16 }}>
      <Form layout="vertical">
        <Row gutter={[24, 24]}>
          {/* 地理位置筛选 */}
          <Col xs={24} lg={12}>
            <Card title={<><EnvironmentOutlined /> 地理位置筛选</>} size="small">
              <Form.Item label="州 (State)">
                <Select
                  mode="multiple"
                  placeholder="选择州"
                  value={queryState.step1Filters.states}
                  onChange={(values) => setQueryState(prev => ({
                    ...prev,
                    step1Filters: { ...prev.step1Filters, states: values }
                  }))}
                  style={{ width: '100%' }}
                >
                  {availableStates.map(state => (
                    <Option key={state.code} value={state.code}>
                      {state.name} ({state.count})
                    </Option>
                  ))}
                </Select>
              </Form.Item>

              <Form.Item label="城市 (City)">
                <Select
                  mode="multiple"
                  placeholder="选择城市"
                  value={queryState.step1Filters.cities}
                  onChange={(values) => setQueryState(prev => ({
                    ...prev,
                    step1Filters: { ...prev.step1Filters, cities: values }
                  }))}
                  style={{ width: '100%' }}
                >
                  {availableCities.map(city => (
                    <Option key={city.name} value={city.name}>
                      {city.name} ({city.count})
                    </Option>
                  ))}
                </Select>
              </Form.Item>
            </Card>
          </Col>

          {/* 财务规模筛选 */}
          <Col xs={24} lg={12}>
            <Card title={<><DollarOutlined /> 财务规模筛选</>} size="small">
              <Row gutter={[16, 16]}>
                <Col span={12}>
                  <Form.Item label="总收入最小值">
                    <InputNumber
                      placeholder="最小值"
                      value={queryState.step1Filters.revenueMin}
                      onChange={(value) => setQueryState(prev => ({
                        ...prev,
                        step1Filters: { ...prev.step1Filters, revenueMin: value }
                      }))}
                      style={{ width: '100%' }}
                      formatter={value => `$ ${value}`.replace(/\B(?=(\d{3})+(?!\d))/g, ',')}
                      parser={value => value.replace(/\$\s?|(,*)/g, '')}
                    />
                  </Form.Item>
                </Col>
                <Col span={12}>
                  <Form.Item label="总收入最大值">
                    <InputNumber
                      placeholder="最大值"
                      value={queryState.step1Filters.revenueMax}
                      onChange={(value) => setQueryState(prev => ({
                        ...prev,
                        step1Filters: { ...prev.step1Filters, revenueMax: value }
                      }))}
                      style={{ width: '100%' }}
                      formatter={value => `$ ${value}`.replace(/\B(?=(\d{3})+(?!\d))/g, ',')}
                      parser={value => value.replace(/\$\s?|(,*)/g, '')}
                    />
                  </Form.Item>
                </Col>
              </Row>

              <Row gutter={[16, 16]}>
                <Col span={12}>
                  <Form.Item label="总资产最小值">
                    <InputNumber
                      placeholder="最小值"
                      value={queryState.step1Filters.assetsMin}
                      onChange={(value) => setQueryState(prev => ({
                        ...prev,
                        step1Filters: { ...prev.step1Filters, assetsMin: value }
                      }))}
                      style={{ width: '100%' }}
                      formatter={value => `$ ${value}`.replace(/\B(?=(\d{3})+(?!\d))/g, ',')}
                      parser={value => value.replace(/\$\s?|(,*)/g, '')}
                    />
                  </Form.Item>
                </Col>
                <Col span={12}>
                  <Form.Item label="总资产最大值">
                    <InputNumber
                      placeholder="最大值"
                      value={queryState.step1Filters.assetsMax}
                      onChange={(value) => setQueryState(prev => ({
                        ...prev,
                        step1Filters: { ...prev.step1Filters, assetsMax: value }
                      }))}
                      style={{ width: '100%' }}
                      formatter={value => `$ ${value}`.replace(/\B(?=(\d{3})+(?!\d))/g, ',')}
                      parser={value => value.replace(/\$\s?|(,*)/g, '')}
                    />
                  </Form.Item>
                </Col>
              </Row>
            </Card>
          </Col>

          {/* 运营规模筛选 */}
          <Col xs={24}>
            <Card title={<><TeamOutlined /> 运营规模筛选</>} size="small">
              <Row gutter={[16, 16]}>
                <Col span={12}>
                  <Form.Item label="独立生活单元数 (ILU) 最小值">
                    <InputNumber
                      placeholder="最小单元数"
                      value={queryState.step1Filters.iluMin}
                      onChange={(value) => setQueryState(prev => ({
                        ...prev,
                        step1Filters: { ...prev.step1Filters, iluMin: value }
                      }))}
                      style={{ width: '100%' }}
                      min={0}
                    />
                  </Form.Item>
                </Col>
                <Col span={12}>
                  <Form.Item label="辅助生活单元数 (ALU) 最小值">
                    <InputNumber
                      placeholder="最小单元数"
                      value={queryState.step1Filters.aluMin}
                      onChange={(value) => setQueryState(prev => ({
                        ...prev,
                        step1Filters: { ...prev.step1Filters, aluMin: value }
                      }))}
                      style={{ width: '100%' }}
                      min={0}
                    />
                  </Form.Item>
                </Col>
              </Row>
            </Card>
          </Col>
        </Row>

        <Divider />

        <Space>
          <Button 
            icon={<LeftOutlined />} 
            onClick={() => setCurrentStep(0)}
          >
            上一步
          </Button>
          <Button 
            type="primary" 
            icon={<RightOutlined />}
            onClick={handleStep1Submit}
            loading={stepLoading}
          >
            执行筛选
          </Button>
        </Space>
      </Form>
    </Card>
  );

  // 步骤2：精确定位
  const Step2PreciseSelection = () => (
    <Card title="步骤 3: 精确定位组织" style={{ marginBottom: 16 }}>
      <Space direction="vertical" size="large" style={{ width: '100%' }}>
        <Alert
          message={`范围筛选结果: ${stepResults.step1Count} 个组织`}
          description="请选择您要查询的具体组织"
          type="info"
          showIcon
        />

        <Card title="选择方式" size="small">
          <Radio.Group
            value={queryState.step2Filters.selectionMode}
            onChange={(e) => setQueryState(prev => ({
              ...prev,
              step2Filters: { ...prev.step2Filters, selectionMode: e.target.value }
            }))}
          >
            <Space direction="vertical">
              <Radio value="all">
                <Text strong>全选模式</Text>
                <br />
                <Text type="secondary">选择所有筛选出的组织 ({stepResults.step1Count} 个)</Text>
              </Radio>
              <Radio value="specific">
                <Text strong>精确选择</Text>
                <br />
                <Text type="secondary">通过名称或EIN精确查找特定组织</Text>
              </Radio>
            </Space>
          </Radio.Group>
        </Card>

        {queryState.step2Filters.selectionMode === 'specific' && (
          <Card title="精确搜索" size="small">
            <Form.Item label="搜索条件">
              <Input.TextArea
                placeholder="请输入组织名称或EIN号码，多个条件请换行输入"
                value={queryState.step2Filters.searchTerms}
                onChange={(e) => setQueryState(prev => ({
                  ...prev,
                  step2Filters: { ...prev.step2Filters, searchTerms: e.target.value }
                }))}
                rows={4}
              />
            </Form.Item>
            <Text type="secondary">
              支持模糊匹配，可以输入部分名称或EIN号码
            </Text>
          </Card>
        )}

        <Divider />

        <Space>
          <Button 
            icon={<LeftOutlined />} 
            onClick={() => setCurrentStep(1)}
          >
            上一步
          </Button>
          <Button 
            type="primary" 
            icon={<RightOutlined />}
            onClick={handleStep2Submit}
            loading={stepLoading}
          >
            确认选择
          </Button>
        </Space>
      </Space>
    </Card>
  );

  // 步骤3：变量选择
  const Step3VariableSelection = () => (
    <Card title="步骤 4: 变量选择" style={{ marginBottom: 16 }}>
      <Space direction="vertical" size="large" style={{ width: '100%' }}>
        <Alert
          message={`已选择: ${stepResults.step2Count} 个组织`}
          description="请选择您需要的数据字段"
          type="info"
          showIcon
        />

        <Card title="字段分类选择" size="small">
          <Collapse>
            {Object.entries(fieldInfo.categories || {}).map(([category, fields]) => (
              <Panel 
                header={
                  <Space>
                    <Text strong>{category}</Text>
                    <Badge count={fields.length} style={{ backgroundColor: '#52c41a' }} />
                  </Space>
                } 
                key={category}
              >
                <Checkbox.Group
                  value={queryState.selectedFields}
                  onChange={(values) => setQueryState(prev => ({
                    ...prev,
                    selectedFields: values
                  }))}
                >
                  <Row gutter={[16, 8]}>
                    {fields.map(field => (
                      <Col key={field.name} xs={24} sm={12} md={8} lg={6}>
                        <Tooltip title={field.name}>
                          <Checkbox value={field.name}>
                            {field.display_name || field.name}
                          </Checkbox>
                        </Tooltip>
                      </Col>
                    ))}
                  </Row>
                </Checkbox.Group>
              </Panel>
            ))}
          </Collapse>
        </Card>

        <Alert
          message={`已选择 ${queryState.selectedFields.length} 个字段`}
          description={`共 ${fieldInfo.fields?.length || 0} 个可用字段`}
          type="success"
          showIcon
        />

        <Divider />

        <Space>
          <Button 
            icon={<LeftOutlined />} 
            onClick={() => setCurrentStep(2)}
          >
            上一步
          </Button>
          <Button 
            type="primary" 
            icon={<RightOutlined />}
            onClick={handleStep3Submit}
            disabled={queryState.selectedFields.length === 0}
          >
            确认字段
          </Button>
        </Space>
      </Space>
    </Card>
  );

  // 步骤4：数据导出
  const Step4DataExport = () => (
    <Card title="步骤 5: 数据导出" style={{ marginBottom: 16 }}>
      <Space direction="vertical" size="large" style={{ width: '100%' }}>
        <Alert
          message="查询配置确认"
          description={
            <div>
              <p><strong>年份:</strong> {queryState.selectedYear}</p>
              <p><strong>组织数量:</strong> {stepResults.step2Count} 个</p>
              <p><strong>字段数量:</strong> {queryState.selectedFields.length} 个</p>
            </div>
          }
          type="success"
          showIcon
        />

        <Card title="导出格式选择" size="small">
          <Space direction="vertical" style={{ width: '100%' }}>
            <Button 
              type="primary" 
              icon={<DownloadOutlined />}
              size="large"
              onClick={() => handleFinalQuery('xlsx')}
              loading={stepLoading}
              style={{ width: '100%' }}
            >
              导出为 Excel (XLSX)
            </Button>
            
            <Button 
              icon={<DownloadOutlined />}
              size="large"
              onClick={() => handleFinalQuery('csv')}
              loading={stepLoading}
              style={{ width: '100%' }}
            >
              导出为 CSV
            </Button>
            
            <Button 
              icon={<DownloadOutlined />}
              size="large"
              onClick={() => handleFinalQuery('json')}
              loading={stepLoading}
              style={{ width: '100%' }}
            >
              导出为 JSON
            </Button>
          </Space>
        </Card>

        {queryState.finalData && (
          <Card title="导出结果" size="small">
            <Alert
              message="导出成功！"
              description={
                <div>
                  <p><strong>记录数:</strong> {queryState.finalData.record_count}</p>
                  <p><strong>字段数:</strong> {queryState.finalData.field_count}</p>
                  <p><strong>文件大小:</strong> {queryState.finalData.file_size}</p>
                </div>
              }
              type="success"
              showIcon
            />
          </Card>
        )}

        <Divider />

        <Space>
          <Button 
            icon={<LeftOutlined />} 
            onClick={() => setCurrentStep(3)}
          >
            上一步
          </Button>
          <Button 
            type="primary" 
            icon={<ClearOutlined />}
            onClick={() => {
              setCurrentStep(0);
              setQueryState({
                selectedYear: null,
                step1Filters: {
                  states: [],
                  cities: [],
                  revenueMin: null,
                  revenueMax: null,
                  assetsMin: null,
                  assetsMax: null,
                  iluMin: null,
                  aluMin: null
                },
                step2Filters: {
                  selectionMode: 'all',
                  searchTerms: '',
                  selectedOrganizations: []
                },
                selectedFields: [],
                finalData: null
              });
              setStepResults({
                step1Count: 0,
                step2Count: 0,
                step2Organizations: []
              });
            }}
          >
            重新开始
          </Button>
        </Space>
      </Space>
    </Card>
  );

  return (
    <div style={{ padding: '24px' }}>
      <Title level={2}>
        <DatabaseOutlined /> WRDS风格数据查询系统
      </Title>
      
      <Card style={{ marginBottom: 16 }}>
        <Steps current={currentStep} size="small">
          <Step title="年份选择" description="选择数据年度" />
          <Step title="范围筛选" description="地理位置、财务规模" />
          <Step title="精确定位" description="选择目标组织" />
          <Step title="变量选择" description="选择数据字段" />
          <Step title="数据导出" description="导出查询结果" />
        </Steps>
      </Card>

      {loading ? (
        <Card>
          <div style={{ textAlign: 'center', padding: '50px' }}>
            <Spin size="large" />
            <div style={{ marginTop: 16 }}>正在加载系统数据...</div>
          </div>
        </Card>
      ) : (
        renderStepContent()
      )}
    </div>
  );
};

export default QueryForm; 