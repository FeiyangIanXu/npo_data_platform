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
  Modal
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
  DownloadOutlined
} from '@ant-design/icons';
import axios from 'axios';

const { Title, Text, Paragraph } = Typography;
const { Option } = Select;
const { Panel } = Collapse;
const { Step } = Steps;

const QueryForm = () => {
  // 步骤控制
  const [currentStep, setCurrentStep] = useState(0);
  const [loading, setLoading] = useState(false);
  
  // 步骤1：年份选择
  const [availableYears, setAvailableYears] = useState([]);
  const [selectedYear, setSelectedYear] = useState(null);
  
  // 步骤2：范围筛选
  const [availableStates, setAvailableStates] = useState([]);
  const [availableCities, setAvailableCities] = useState([]);
  const [rangeFilters, setRangeFilters] = useState({
    state: null,
    city: null,
    min_revenue: null,
    max_revenue: null,
    min_assets: null,
    max_assets: null,
    min_ilu: null,
    min_alu: null
  });
  
  // 步骤3：精确定位
  const [filteredOrganizations, setFilteredOrganizations] = useState([]);
  const [searchType, setSearchType] = useState('name');
  const [selectAll, setSelectAll] = useState(false);
  const [selectedOrganizations, setSelectedOrganizations] = useState([]);
  const [searchTerms, setSearchTerms] = useState('');
  
  // 步骤4：变量选择
  const [availableFields, setAvailableFields] = useState([]);
  const [selectedFields, setSelectedFields] = useState([]);
  const [fieldsLoading, setFieldsLoading] = useState(false);
  
  // 步骤5：输出格式
  const [outputFormat, setOutputFormat] = useState('xlsx');
  const [finalData, setFinalData] = useState(null);
  
  // 初始化数据
  useEffect(() => {
    loadAvailableYears();
    loadAvailableFields();
  }, []);
  
  // 加载可用年份
  const loadAvailableYears = async () => {
    try {
      const response = await axios.get('/api/available-years');
      setAvailableYears(response.data.years);
    } catch (error) {
      message.error('加载年份数据失败');
    }
  };
  
  // 加载可用字段
  const loadAvailableFields = async () => {
    setFieldsLoading(true);
    try {
      const response = await axios.get('/api/field-info');
      const fields = response.data.fields;
      
      // 按类别分组
      const groupedFields = fields.reduce((acc, field) => {
        if (!acc[field.category]) {
          acc[field.category] = [];
        }
        acc[field.category].push(field);
        return acc;
      }, {});
      
      setAvailableFields(groupedFields);
    } catch (error) {
      message.error('加载字段信息失败');
    } finally {
      setFieldsLoading(false);
    }
  };
  
  // 年份选择后加载州数据
  const handleYearChange = async (year) => {
    setSelectedYear(year);
    setLoading(true);
    try {
      const response = await axios.get(`/api/available-states?year=${year}`);
      setAvailableStates(response.data.states);
    } catch (error) {
      message.error('加载州数据失败');
    } finally {
      setLoading(false);
    }
  };
  
  // 州选择后加载城市数据
  const handleStateChange = async (state) => {
    setRangeFilters({...rangeFilters, state});
    setLoading(true);
    try {
      const response = await axios.get(`/api/available-cities?year=${selectedYear}&state=${state}`);
      setAvailableCities(response.data.cities);
    } catch (error) {
      message.error('加载城市数据失败');
    } finally {
      setLoading(false);
    }
  };
  
  // 执行第一步筛选
  const executeStep1Filter = async () => {
    setLoading(true);
    try {
      const filterData = {
        year: selectedYear,
        ...rangeFilters
      };
      
      const response = await axios.post('/api/step1-filter', filterData);
      setFilteredOrganizations(response.data.organizations);
      
      message.success(`筛选完成，找到 ${response.data.total_count} 个组织`);
      setCurrentStep(2);
    } catch (error) {
      message.error('筛选失败');
    } finally {
      setLoading(false);
    }
  };
  
  // 执行第二步筛选
  const executeStep2Filter = async () => {
    setLoading(true);
    try {
      let searchTermsArray = [];
      if (!selectAll && searchTerms) {
        searchTermsArray = searchTerms.split('\n').map(term => term.trim()).filter(term => term);
      }
      
      const filterData = {
        select_all: selectAll,
        search_type: searchType,
        search_terms: searchTermsArray,
        step1_filters: { year: selectedYear, ...rangeFilters }
      };
      
      const response = await axios.post('/api/step2-filter', filterData);
      setSelectedOrganizations(response.data.organizations);
      
      message.success(`选择了 ${response.data.total_count} 个组织`);
      setCurrentStep(3);
    } catch (error) {
      message.error('组织选择失败');
    } finally {
      setLoading(false);
    }
  };
  
  // 执行最终查询
  const executeFinalQuery = async () => {
    setLoading(true);
    try {
      const selectedEins = selectedOrganizations.map(org => org.ein);
      const queryData = {
        selected_eins: selectedEins,
        selected_fields: selectedFields
      };
      
      const response = await axios.post('/api/final-query', queryData);
      setFinalData(response.data);
      
      message.success(`查询完成，获得 ${response.data.total_count} 条记录`);
      setCurrentStep(4);
    } catch (error) {
      message.error('最终查询失败');
    } finally {
      setLoading(false);
    }
  };
  
  // 导出数据
  const handleExport = async () => {
    try {
      const selectedEins = selectedOrganizations.map(org => org.ein);
      const response = await axios.post('/api/export', {
        selected_eins: selectedEins,
        selected_fields: selectedFields,
        format: outputFormat
      }, {
        responseType: 'blob'
      });
      
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `nonprofits_data.${outputFormat}`);
      document.body.appendChild(link);
      link.click();
      link.remove();
      
      message.success('导出成功');
    } catch (error) {
      message.error('导出失败');
    }
  };
  
  // 重置所有数据
  const resetForm = () => {
    setCurrentStep(0);
    setSelectedYear(null);
    setRangeFilters({
      state: null,
      city: null,
      min_revenue: null,
      max_revenue: null,
      min_assets: null,
      max_assets: null,
      min_ilu: null,
      min_alu: null
    });
    setFilteredOrganizations([]);
    setSelectedOrganizations([]);
    setSelectedFields([]);
    setFinalData(null);
    setSearchTerms('');
    setSelectAll(false);
  };
  
  // 步骤1：年份选择
  const Step1Component = () => (
    <Card title="Step 1: 选择数据年份" extra={<DatabaseOutlined />}>
      <Alert
        message="数据年份选择"
        description="选择您要查询的数据年份。系统将根据您的选择加载相应年度的数据。"
        type="info"
        showIcon
        style={{ marginBottom: 16 }}
      />
      
      <Row gutter={16}>
        <Col span={12}>
          <Form.Item label="选择年份" required>
            <Select
              placeholder="请选择数据年份"
              value={selectedYear}
              onChange={handleYearChange}
              loading={loading}
              size="large"
            >
              {availableYears.map(year => (
                <Option key={year} value={year}>{year}</Option>
              ))}
            </Select>
          </Form.Item>
        </Col>
        <Col span={12}>
          <div style={{ marginTop: 32 }}>
            <Button
              type="primary"
              onClick={() => setCurrentStep(1)}
              disabled={!selectedYear}
              size="large"
            >
              下一步：范围筛选 <RightOutlined />
            </Button>
          </div>
        </Col>
      </Row>
    </Card>
  );
  
  // 步骤2：范围筛选
  const Step2Component = () => (
    <Card title="Step 2: 范围筛选 (Universe Screening)" extra={<FilterOutlined />}>
      <Alert
        message="圈定研究范围"
        description="通过地理位置、财务规模和运营规模等条件，圈定您感兴趣的机构范围。"
        type="info"
        showIcon
        style={{ marginBottom: 16 }}
      />
      
      <Collapse defaultActiveKey={['1', '2', '3']}>
        <Panel header="地理位置筛选" key="1">
          <Row gutter={16}>
            <Col span={12}>
              <Form.Item label="州 (State)">
                <Select
                  placeholder="选择州"
                  value={rangeFilters.state}
                  onChange={handleStateChange}
                  loading={loading}
                  allowClear
                >
                  {availableStates.map(state => (
                    <Option key={state.state} value={state.state}>
                      {state.state} ({state.count} 个组织)
                    </Option>
                  ))}
                </Select>
              </Form.Item>
            </Col>
            <Col span={12}>
              <Form.Item label="城市 (City)">
                <Select
                  placeholder="选择城市"
                  value={rangeFilters.city}
                  onChange={(city) => setRangeFilters({...rangeFilters, city})}
                  loading={loading}
                  allowClear
                  disabled={!rangeFilters.state}
                >
                  {availableCities.map(city => (
                    <Option key={city.city} value={city.city}>
                      {city.city} ({city.count} 个组织)
                    </Option>
                  ))}
                </Select>
              </Form.Item>
            </Col>
          </Row>
        </Panel>
        
        <Panel header="财务规模筛选" key="2">
          <Row gutter={16}>
            <Col span={12}>
              <Form.Item label="总收入范围 (USD)">
                <Space>
                  <InputNumber
                    placeholder="最小值"
                    value={rangeFilters.min_revenue}
                    onChange={(value) => setRangeFilters({...rangeFilters, min_revenue: value})}
                    formatter={value => `$ ${value}`.replace(/\B(?=(\d{3})+(?!\d))/g, ',')}
                    parser={value => value.replace(/\$\s?|(,*)/g, '')}
                  />
                  <span>至</span>
                  <InputNumber
                    placeholder="最大值"
                    value={rangeFilters.max_revenue}
                    onChange={(value) => setRangeFilters({...rangeFilters, max_revenue: value})}
                    formatter={value => `$ ${value}`.replace(/\B(?=(\d{3})+(?!\d))/g, ',')}
                    parser={value => value.replace(/\$\s?|(,*)/g, '')}
                  />
                </Space>
              </Form.Item>
            </Col>
            <Col span={12}>
              <Form.Item label="总资产范围 (USD)">
                <Space>
                  <InputNumber
                    placeholder="最小值"
                    value={rangeFilters.min_assets}
                    onChange={(value) => setRangeFilters({...rangeFilters, min_assets: value})}
                    formatter={value => `$ ${value}`.replace(/\B(?=(\d{3})+(?!\d))/g, ',')}
                    parser={value => value.replace(/\$\s?|(,*)/g, '')}
                  />
                  <span>至</span>
                  <InputNumber
                    placeholder="最大值"
                    value={rangeFilters.max_assets}
                    onChange={(value) => setRangeFilters({...rangeFilters, max_assets: value})}
                    formatter={value => `$ ${value}`.replace(/\B(?=(\d{3})+(?!\d))/g, ',')}
                    parser={value => value.replace(/\$\s?|(,*)/g, '')}
                  />
                </Space>
              </Form.Item>
            </Col>
          </Row>
        </Panel>
        
        <Panel header="运营规模筛选" key="3">
          <Row gutter={16}>
            <Col span={12}>
              <Form.Item label="独立生活单元数 (ILU)">
                <InputNumber
                  placeholder="最小单元数"
                  value={rangeFilters.min_ilu}
                  onChange={(value) => setRangeFilters({...rangeFilters, min_ilu: value})}
                  min={0}
                  style={{ width: '100%' }}
                />
              </Form.Item>
            </Col>
            <Col span={12}>
              <Form.Item label="辅助生活单元数 (ALU)">
                <InputNumber
                  placeholder="最小单元数"
                  value={rangeFilters.min_alu}
                  onChange={(value) => setRangeFilters({...rangeFilters, min_alu: value})}
                  min={0}
                  style={{ width: '100%' }}
                />
              </Form.Item>
            </Col>
          </Row>
        </Panel>
      </Collapse>
      
      <div style={{ marginTop: 16, textAlign: 'right' }}>
        <Space>
          <Button onClick={() => setCurrentStep(0)}>
            <LeftOutlined /> 上一步
          </Button>
          <Button type="primary" onClick={executeStep1Filter} loading={loading}>
            执行筛选 <RightOutlined />
          </Button>
        </Space>
      </div>
    </Card>
  );
  
  // 步骤3：精确定位
  const Step3Component = () => (
    <Card title="Step 3: 精确定位组织" extra={<SearchOutlined />}>
      <Alert
        message={`筛选结果：找到 ${filteredOrganizations.length} 个组织`}
        description="现在您可以选择所有组织，或通过名称/税号精确查找特定组织。"
        type="success"
        showIcon
        style={{ marginBottom: 16 }}
      />
      
      <Row gutter={16}>
        <Col span={12}>
          <Card size="small" title="选择方式">
            <Radio.Group value={selectAll ? 'all' : 'specific'} onChange={(e) => {
              setSelectAll(e.target.value === 'all');
              if (e.target.value === 'all') {
                setSearchTerms('');
              }
            }}>
              <Space direction="vertical">
                <Radio value="all">选择所有筛选出的组织</Radio>
                <Radio value="specific">精确选择特定组织</Radio>
              </Space>
            </Radio.Group>
          </Card>
        </Col>
        <Col span={12}>
          {!selectAll && (
            <Card size="small" title="搜索方式">
              <Radio.Group value={searchType} onChange={(e) => setSearchType(e.target.value)}>
                <Space direction="vertical">
                  <Radio value="name">按组织名称搜索</Radio>
                  <Radio value="ein">按税号 (EIN) 搜索</Radio>
                </Space>
              </Radio.Group>
            </Card>
          )}
        </Col>
      </Row>
      
      {!selectAll && (
        <div style={{ marginTop: 16 }}>
          <Form.Item label={`输入${searchType === 'name' ? '组织名称' : 'EIN号码'}`}>
            <Input.TextArea
              placeholder={`请输入${searchType === 'name' ? '组织名称' : 'EIN号码'}，多个请用换行分隔`}
              value={searchTerms}
              onChange={(e) => setSearchTerms(e.target.value)}
              rows={4}
            />
          </Form.Item>
        </div>
      )}
      
      {filteredOrganizations.length > 0 && (
        <div style={{ marginTop: 16 }}>
          <Title level={5}>筛选结果预览：</Title>
          <Table
            dataSource={filteredOrganizations.slice(0, 10)}
            columns={[
              { title: 'EIN', dataIndex: 'ein', key: 'ein' },
              { title: '组织名称', dataIndex: 'name', key: 'name' },
              { title: '城市', dataIndex: 'city', key: 'city' },
              { title: '州', dataIndex: 'state', key: 'state' },
              { title: '总收入', dataIndex: 'total_revenue', key: 'total_revenue', render: (value) => value ? `$${Number(value).toLocaleString()}` : 'N/A' },
            ]}
            pagination={false}
            size="small"
          />
          {filteredOrganizations.length > 10 && (
            <Text type="secondary">显示前10条，共{filteredOrganizations.length}条记录</Text>
          )}
        </div>
      )}
      
      <div style={{ marginTop: 16, textAlign: 'right' }}>
        <Space>
          <Button onClick={() => setCurrentStep(1)}>
            <LeftOutlined /> 上一步
          </Button>
          <Button type="primary" onClick={executeStep2Filter} loading={loading}>
            确认选择 <RightOutlined />
          </Button>
        </Space>
      </div>
    </Card>
  );
  
  // 步骤4：变量选择
  const Step4Component = () => (
    <Card title="Step 4: 选择变量" extra={<DatabaseOutlined />}>
      <Alert
        message={`已选择 ${selectedOrganizations.length} 个组织`}
        description="现在请选择您需要查询的具体变量/字段。"
        type="success"
        showIcon
        style={{ marginBottom: 16 }}
      />
      
      <Row gutter={16}>
        <Col span={12}>
          <Card size="small" title="已选择的组织">
            <div style={{ maxHeight: 200, overflowY: 'auto' }}>
              {selectedOrganizations.map(org => (
                <Tag key={org.ein} style={{ margin: 2 }}>
                  {org.name} ({org.state})
                </Tag>
              ))}
            </div>
          </Card>
        </Col>
        <Col span={12}>
          <Card size="small" title="选择统计">
            <p>已选择组织: {selectedOrganizations.length} 个</p>
            <p>已选择变量: {selectedFields.length} 个</p>
          </Card>
        </Col>
      </Row>
      
      <div style={{ marginTop: 16 }}>
        <Title level={5}>选择变量：</Title>
        <Spin spinning={fieldsLoading}>
          <Collapse>
            {Object.entries(availableFields).map(([category, fields]) => (
              <Panel 
                header={`${category} (${fields.length} 个字段)`} 
                key={category}
                extra={
                  <Checkbox
                    indeterminate={
                      fields.some(field => selectedFields.includes(field.field_name)) &&
                      !fields.every(field => selectedFields.includes(field.field_name))
                    }
                    checked={fields.every(field => selectedFields.includes(field.field_name))}
                    onChange={(e) => {
                      if (e.target.checked) {
                        setSelectedFields([...selectedFields, ...fields.map(f => f.field_name)]);
                      } else {
                        setSelectedFields(selectedFields.filter(f => !fields.map(field => field.field_name).includes(f)));
                      }
                    }}
                  >
                    全选
                  </Checkbox>
                }
              >
                <Checkbox.Group
                  value={selectedFields}
                  onChange={(checkedValues) => {
                    setSelectedFields(checkedValues);
                  }}
                >
                  <Row>
                    {fields.map(field => (
                      <Col span={24} key={field.field_name} style={{ marginBottom: 8 }}>
                        <Checkbox value={field.field_name}>
                          <Tooltip title={field.field_name}>
                            {field.display_name}
                          </Tooltip>
                        </Checkbox>
                      </Col>
                    ))}
                  </Row>
                </Checkbox.Group>
              </Panel>
            ))}
          </Collapse>
        </Spin>
      </div>
      
      <div style={{ marginTop: 16, textAlign: 'right' }}>
        <Space>
          <Button onClick={() => setCurrentStep(2)}>
            <LeftOutlined /> 上一步
          </Button>
          <Button 
            type="primary" 
            onClick={executeFinalQuery} 
            loading={loading}
            disabled={selectedFields.length === 0}
          >
            查询数据 <RightOutlined />
          </Button>
        </Space>
      </div>
    </Card>
  );
  
  // 步骤5：输出格式
  const Step5Component = () => (
    <Card title="Step 5: 输出格式与导出" extra={<ExportOutlined />}>
      <Alert
        message="查询完成！"
        description={`成功查询到 ${finalData?.total_count || 0} 条记录，${finalData?.columns?.length || 0} 个字段。`}
        type="success"
        showIcon
        style={{ marginBottom: 16 }}
      />
      
      <Row gutter={16}>
        <Col span={12}>
          <Card size="small" title="选择输出格式">
            <Radio.Group value={outputFormat} onChange={(e) => setOutputFormat(e.target.value)}>
              <Space direction="vertical">
                <Radio value="xlsx">Excel (XLSX)</Radio>
                <Radio value="csv">CSV</Radio>
                <Radio value="json">JSON</Radio>
              </Space>
            </Radio.Group>
          </Card>
        </Col>
        <Col span={12}>
          <Card size="small" title="数据预览">
            <p>记录数: {finalData?.total_count || 0}</p>
            <p>字段数: {finalData?.columns?.length || 0}</p>
            <p>文件格式: {outputFormat.toUpperCase()}</p>
          </Card>
        </Col>
      </Row>
      
      {finalData && (
        <div style={{ marginTop: 16 }}>
          <Title level={5}>数据预览：</Title>
          <Table
            dataSource={finalData.data?.slice(0, 5)}
            columns={finalData.columns?.slice(0, 5).map(col => ({
              title: col,
              dataIndex: col,
              key: col,
              ellipsis: true,
              width: 150
            }))}
            pagination={false}
            size="small"
            scroll={{ x: 'max-content' }}
          />
          {finalData.data?.length > 5 && (
            <Text type="secondary">显示前5条记录...</Text>
          )}
        </div>
      )}
      
      <div style={{ marginTop: 16, textAlign: 'right' }}>
        <Space>
          <Button onClick={() => setCurrentStep(3)}>
            <LeftOutlined /> 上一步
          </Button>
          <Button onClick={resetForm}>
            <ClearOutlined /> 重新开始
          </Button>
          <Button type="primary" onClick={handleExport} icon={<DownloadOutlined />}>
            导出数据
          </Button>
        </Space>
      </div>
    </Card>
  );
  
  const steps = [
    { title: '年份选择', icon: <DatabaseOutlined /> },
    { title: '范围筛选', icon: <FilterOutlined /> },
    { title: '精确定位', icon: <SearchOutlined /> },
    { title: '变量选择', icon: <DatabaseOutlined /> },
    { title: '输出格式', icon: <ExportOutlined /> }
  ];
  
  return (
    <div style={{ padding: '24px' }}>
      <Title level={2}>
        <DatabaseOutlined /> 数据查询系统 (WRDS-Style)
      </Title>
      <Paragraph>
        按照以下步骤进行数据查询，系统将引导您完成整个查询过程。
      </Paragraph>
      
      <Steps current={currentStep} style={{ marginBottom: 24 }}>
        {steps.map((step, index) => (
          <Step key={index} title={step.title} icon={step.icon} />
        ))}
      </Steps>
      
      <div style={{ marginTop: 24 }}>
        {currentStep === 0 && <Step1Component />}
        {currentStep === 1 && <Step2Component />}
        {currentStep === 2 && <Step3Component />}
        {currentStep === 3 && <Step4Component />}
        {currentStep === 4 && <Step5Component />}
      </div>
    </div>
  );
};

export default QueryForm; 