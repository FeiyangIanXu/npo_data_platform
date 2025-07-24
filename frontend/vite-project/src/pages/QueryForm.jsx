import React, { useState, useEffect } from 'react';
import {
  Steps,
  Select,
  Button,
  Card,
  Spin,
  message,
  Typography,
  Row,
  Col,
  Divider,
  Radio,
  InputNumber,
  Input,
  Table,
  Alert,
  Checkbox
} from 'antd';
import { useNavigate } from 'react-router-dom';

const { Step } = Steps;
const { Title, Paragraph } = Typography;

const QueryForm = () => {
  const [currentStep, setCurrentStep] = useState(0);
  const [loadingYears, setLoadingYears] = useState(true);
  const [loadingMonths, setLoadingMonths] = useState(false);
  const [availableYears, setAvailableYears] = useState([]);
  const [availableMonths, setAvailableMonths] = useState([]);
  const [selectedYear, setSelectedYear] = useState(null);
  const [selectedMonth, setSelectedMonth] = useState(null);

  // New state management for enhanced filtering
  const [filterMode, setFilterMode] = useState('criteria'); // 'criteria' or 'search'
  const [geoFilters, setGeoFilters] = useState({ st: null, city: null });
  const [financialFilters, setFinancialFilters] = useState({ min_revenue: null, max_revenue: null });
  const [operationalFilters, setOperationalFilters] = useState({ min_ilu: null, max_ilu: null });
  const [searchText, setSearchText] = useState('');

  // New state for optional filtering modules
  const [activeFilters, setActiveFilters] = useState({
    geographic: true, // Default enabled geographic filtering
    financial: false,
    operational: false,
  });

  // New state for specific search type
  const [specificSearchType, setSpecificSearchType] = useState('name'); // 'name' or 'ein'

  const [availableStates, setAvailableStates] = useState([]);
  const [availableCities, setAvailableCities] = useState([]);
  const [loadingOptions, setLoadingOptions] = useState({ states: false, cities: false });

  const [step2Results, setStep2Results] = useState([]); // Store Step 2 filtered company list
  const [step3SelectedKeys, setStep3SelectedKeys] = useState([]); // Store Step 3 final confirmed company EIN list

  const navigate = useNavigate();

  useEffect(() => {
    // Load available years
    const fetchYears = async () => {
      try {
        setLoadingYears(true);
        const response = await fetch('/api/available-years');
        if (!response.ok) {
          throw new Error('Failed to fetch years');
        }
        const data = await response.json();
        setAvailableYears(data.years || []);
      } catch (error) {
        message.error('Unable to load available years. Please check if the backend service is running.');
        console.error(error);
      } finally {
        setLoadingYears(false);
      }
    };

    fetchYears();
  }, []);

  // Dynamic month loading based on selected year
  useEffect(() => {
    if (selectedYear) {
      const fetchMonths = async () => {
        setLoadingMonths(true);
        setAvailableMonths([]);
        setSelectedMonth(null);
        try {
          const response = await fetch(`/api/available-months?year=${selectedYear}`);
          if (!response.ok) {
            throw new Error('Failed to fetch months');
          }
          const data = await response.json();
          setAvailableMonths(data.months || []);
        } catch (error) {
          message.error(`Unable to load available months for ${selectedYear}.`);
          console.error(error);
        } finally {
          setLoadingMonths(false);
        }
      };
      fetchMonths();
    } else {
      setAvailableMonths([]);
      setSelectedMonth(null);
    }
  }, [selectedYear]);

  // Load geographic options when year changes with enhanced debugging
  useEffect(() => {
    if (selectedYear) {
      // Load available states
      const fetchStates = async () => {
        setLoadingOptions(prev => ({ ...prev, states: true }));
        try {
          console.log(`Fetching states for fiscal year: ${selectedYear}`);
          const response = await fetch(`/api/available-states?fiscal_year=${selectedYear}`);
          console.log('States API response status:', response.status);
          
          if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
          }
          
          const data = await response.json();
          console.log('States data received:', data);
          
          if (data.states && Array.isArray(data.states)) {
            setAvailableStates(data.states);
            console.log(`Successfully loaded ${data.states.length} states:`, data.states);
          } else {
            console.warn('States data is not in expected format:', data);
            setAvailableStates([]);
          }
        } catch (error) {
          console.error('Failed to fetch states:', error);
          message.error(`Failed to load states: ${error.message}`);
          setAvailableStates([]);
        } finally {
          setLoadingOptions(prev => ({ ...prev, states: false }));
        }
      };
      fetchStates();
    } else {
      setAvailableStates([]);
    }
  }, [selectedYear]);

  // Load cities when state changes
  useEffect(() => {
    if (selectedYear && geoFilters.st) {
      const fetchCities = async () => {
        setLoadingOptions(prev => ({ ...prev, cities: true }));
        try {
          const response = await fetch(`/api/available-cities?fiscal_year=${selectedYear}&state=${geoFilters.st}`);
          if (response.ok) {
            const data = await response.json();
            setAvailableCities(data.cities || []);
          }
        } catch (error) {
          console.error('Failed to fetch cities:', error);
        } finally {
          setLoadingOptions(prev => ({ ...prev, cities: false }));
        }
      };
      fetchCities();
    } else {
      setAvailableCities([]);
      setGeoFilters(prev => ({ ...prev, city: null }));
    }
  }, [selectedYear, geoFilters.st]);

  const handleNextStep = () => {
    if (!selectedYear) {
      message.warning('Please select a fiscal year!');
      return;
    }
    setCurrentStep(1);
  };

  const handlePreviousStep = () => {
    setCurrentStep(Math.max(0, currentStep - 1));
  };

  const handleYearChange = (value) => {
    setSelectedYear(value);
  };

  const handleMonthChange = (value) => {
    setSelectedMonth(value);
  };

  // Handle filter toggle for optional modules
  const handleFilterToggle = (filterType, checked) => {
    setActiveFilters(prev => ({
      ...prev,
      [filterType]: checked
    }));
    
    // Clear filter values when module is disabled
    if (!checked) {
      switch (filterType) {
        case 'geographic':
          setGeoFilters({ st: null, city: null });
          break;
        case 'financial':
          setFinancialFilters({ min_revenue: null, max_revenue: null });
          break;
        case 'operational':
          setOperationalFilters({ min_ilu: null, max_ilu: null });
          break;
      }
    }
  };

  // Handle Step 2 - Universe Screening with optional filters
  const handleStep2Next = async () => {
    try {
      let results = [];

      if (filterMode === 'criteria') {
        // Construct filter request for criteria mode - only include active filters
        const filterRequest = {
          fiscal_year: selectedYear,
          fiscal_month: selectedMonth,
        };

        // Only add filter sections that are active
        if (activeFilters.geographic) {
          filterRequest.geo_filters = geoFilters;
        }
        
        if (activeFilters.financial) {
          filterRequest.financial_filters = financialFilters;
        }
        
        if (activeFilters.operational) {
          filterRequest.operational_filters = operationalFilters;
        }

        console.log('Sending filter request:', filterRequest);

        const response = await fetch('/api/filter/enhanced', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify(filterRequest),
        });

        if (!response.ok) {
          throw new Error('Failed to filter organizations');
        }

        const data = await response.json();
        results = data.results || [];
      } else {
        // Search mode - split search text into company list with search type
        const searchTerms = searchText.split('\n').filter(term => term.trim());
        if (searchTerms.length === 0) {
          message.warning('Please enter organization names or EINs to search');
          return;
        }

        const searchRequest = {
          fiscal_year: selectedYear,
          fiscal_month: selectedMonth,
          search_terms: searchTerms,
          search_type: specificSearchType  // Add search type to distinguish name vs EIN
        };

        console.log('Sending search request:', searchRequest);

        const response = await fetch('/api/search/batch', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify(searchRequest),
        });

        if (!response.ok) {
          throw new Error('Failed to search organizations');
        }

        const data = await response.json();
        results = data.results || [];
      }

      setStep2Results(results);
      setStep3SelectedKeys([]); // Reset selection
      setCurrentStep(2); // Move to Step 3

      message.success(`Found ${results.length} organizations matching your criteria`);
    } catch (error) {
      message.error('Failed to find organizations: ' + error.message);
      console.error(error);
    }
  };

  // Convert month number to English name
  const monthToName = (monthNumber) => {
    const date = new Date();
    date.setMonth(monthNumber - 1);
    return date.toLocaleString('en-US', { month: 'long' });
  };

  const renderStepContent = () => {
    switch (currentStep) {
      case 0:
        return (
          <Card title="Step 1: Select Time Range" className="step-card">
            <Paragraph>
              Please select the fiscal year you want to query. This is the foundation for all subsequent filtering.
              According to WRDS standards, the fiscal year is based on the calendar year in which the reporting period ends.
            </Paragraph>

            <Row gutter={16} align="bottom" style={{ marginBottom: 20 }}>
              <Col span={8}>
                <label style={{ display: 'block', marginBottom: 8, fontWeight: 500 }}>
                  Fiscal Year:
                </label>
                {loadingYears ? (
                  <Spin />
                ) : (
                  <Select
                    style={{ width: '100%' }}
                    placeholder="Select Year"
                    onChange={handleYearChange}
                    value={selectedYear}
                    showSearch
                    filterOption={(input, option) =>
                      option.children.toLowerCase().indexOf(input.toLowerCase()) >= 0
                    }
                  >
                    {availableYears.map(year => (
                      <Select.Option key={year} value={year}>FY {year}</Select.Option>
                    ))}
                  </Select>
                )}
              </Col>

              <Col span={8}>
                <label style={{ display: 'block', marginBottom: 8, fontWeight: 500 }}>
                  FY Ending Month (Optional):
                </label>
                <Select
                  style={{ width: '100%' }}
                  placeholder="Any Month"
                  value={selectedMonth}
                  onChange={handleMonthChange}
                  disabled={!selectedYear || loadingMonths}
                  loading={loadingMonths}
                  allowClear
                >
                  {availableMonths.map(month => (
                    <Select.Option key={month} value={month}>
                      {monthToName(month)}
                    </Select.Option>
                  ))}
                </Select>
              </Col>
            </Row>

            {selectedYear && (
              <div className="selection-info">
                <Paragraph>
                  <strong>Selected:</strong> FY {selectedYear}
                  {selectedMonth && ` ending in ${monthToName(selectedMonth)}`}
                </Paragraph>
                <Paragraph type="secondary">
                  This will filter organizations with fiscal years ending in {selectedYear}
                  {selectedMonth && ` specifically in ${monthToName(selectedMonth)}`}
                  {!selectedMonth && `, across all ending months`}
                </Paragraph>
                {availableMonths.length > 0 && (
                  <Paragraph type="secondary" style={{ fontSize: '12px', fontStyle: 'italic' }}>
                    Available ending months for FY {selectedYear}: {availableMonths.map(m => monthToName(m)).join(', ')}
                  </Paragraph>
                )}
              </div>
            )}

            <div className="step-actions">
              <Button type="primary" onClick={handleNextStep} disabled={!selectedYear}>
                Next Step
              </Button>
              <Button onClick={() => navigate('/')} style={{ marginLeft: 8 }}>
                Back to Home
              </Button>
            </div>
          </Card>
        );

      case 1:
        return (
          <Card title="Step 2: Universe Screening" className="step-card">
            <Paragraph>
              You have selected fiscal year: <strong>FY {selectedYear}</strong>.
              Now, narrow down the universe of organizations by applying filters.
            </Paragraph>

            <Radio.Group value={filterMode} onChange={(e) => setFilterMode(e.target.value)} style={{ marginBottom: 20 }}>
              <Radio.Button value="criteria">Filter by Criteria</Radio.Button>
              <Radio.Button value="search">Search for Specific Companies</Radio.Button>
            </Radio.Group>

            <Divider />

            {filterMode === 'criteria' ? (
              <div className="range-filters">
                <div style={{ marginBottom: 16 }}>
                  <Checkbox 
                    checked={activeFilters.geographic} 
                    onChange={e => handleFilterToggle('geographic', e.target.checked)}
                    style={{ marginBottom: 16 }}
                  >
                    <Title level={4} style={{ display: 'inline', margin: 0 }}>Geographic Filtering</Title>
                  </Checkbox>
                </div>
                <div style={{ marginLeft: 24, opacity: activeFilters.geographic ? 1 : 0.5 }}>
                  <Row gutter={[16, 16]}>
                    <Col span={12}>
                      <label>State:</label>
                      <Select
                        style={{ width: '100%' }}
                        placeholder="Select State"
                        value={geoFilters.st}
                        onChange={(value) => setGeoFilters(prev => ({ ...prev, st: value }))}
                        disabled={!activeFilters.geographic}
                        loading={loadingOptions.states}
                        allowClear
                      >
                        {availableStates.map(state => (
                          <Select.Option key={state} value={state}>{state}</Select.Option>
                        ))}
                      </Select>
                      {availableStates.length === 0 && selectedYear && (
                        <div style={{ fontSize: '12px', color: '#999', marginTop: 4 }}>
                          No states found for FY {selectedYear}. Check console for details.
                        </div>
                      )}
                    </Col>
                    <Col span={12}>
                      <label>City:</label>
                      <Select
                        style={{ width: '100%' }}
                        placeholder="Select City"
                        value={geoFilters.city}
                        onChange={(value) => setGeoFilters(prev => ({ ...prev, city: value }))}
                        disabled={!activeFilters.geographic || !geoFilters.st}
                        loading={loadingOptions.cities}
                        allowClear
                      >
                        {availableCities.map(city => (
                          <Select.Option key={city} value={city}>{city}</Select.Option>
                        ))}
                      </Select>
                    </Col>
                  </Row>
                </div>
                
                <Divider />
                
                <div style={{ marginBottom: 16 }}>
                  <Checkbox 
                    checked={activeFilters.financial} 
                    onChange={e => handleFilterToggle('financial', e.target.checked)}
                    style={{ marginBottom: 16 }}
                  >
                    <Title level={4} style={{ display: 'inline', margin: 0 }}>Financial Scale Filtering</Title>
                  </Checkbox>
                </div>
                <div style={{ marginLeft: 24, opacity: activeFilters.financial ? 1 : 0.5 }}>
                  <Row gutter={[16, 16]}>
                    <Col span={12}>
                      <label>Total Revenue (Min):</label>
                      <InputNumber
                        style={{ width: '100%' }}
                        placeholder="e.g., 1000000"
                        value={financialFilters.min_revenue}
                        onChange={(value) => setFinancialFilters(prev => ({ ...prev, min_revenue: value }))}
                        disabled={!activeFilters.financial}
                        formatter={value => `$ ${value}`.replace(/\B(?=(\d{3})+(?!\d))/g, ',')}
                        parser={value => value.replace(/\$\s?|(,*)/g, '')}
                      />
                    </Col>
                    <Col span={12}>
                      <label>Total Revenue (Max):</label>
                      <InputNumber
                        style={{ width: '100%' }}
                        placeholder="e.g., 50000000"
                        value={financialFilters.max_revenue}
                        onChange={(value) => setFinancialFilters(prev => ({ ...prev, max_revenue: value }))}
                        disabled={!activeFilters.financial}
                        formatter={value => `$ ${value}`.replace(/\B(?=(\d{3})+(?!\d))/g, ',')}
                        parser={value => value.replace(/\$\s?|(,*)/g, '')}
                      />
                    </Col>
                  </Row>
                </div>
                
                <Divider />
                
                <div style={{ marginBottom: 16 }}>
                  <Checkbox 
                    checked={activeFilters.operational} 
                    onChange={e => handleFilterToggle('operational', e.target.checked)}
                    style={{ marginBottom: 16 }}
                  >
                    <Title level={4} style={{ display: 'inline', margin: 0 }}>Operational Scale Filtering</Title>
                  </Checkbox>
                </div>
                <div style={{ marginLeft: 24, opacity: activeFilters.operational ? 1 : 0.5 }}>
                  <Row gutter={[16, 16]}>
                    <Col span={12}>
                      <label>ILU (Independent Living Units) Min:</label>
                      <InputNumber
                        style={{ width: '100%' }}
                        placeholder="e.g., 50"
                        value={operationalFilters.min_ilu}
                        onChange={(value) => setOperationalFilters(prev => ({ ...prev, min_ilu: value }))}
                        disabled={!activeFilters.operational}
                      />
                    </Col>
                    <Col span={12}>
                      <label>ILU (Independent Living Units) Max:</label>
                      <InputNumber
                        style={{ width: '100%' }}
                        placeholder="e.g., 500"
                        value={operationalFilters.max_ilu}
                        onChange={(value) => setOperationalFilters(prev => ({ ...prev, max_ilu: value }))}
                        disabled={!activeFilters.operational}
                      />
                    </Col>
                  </Row>
                </div>
              </div>
            ) : (
              <div className="precise-search">
                <Title level={4}>Search for Specific Companies</Title>
                <Radio.Group
                  value={specificSearchType}
                  onChange={e => setSpecificSearchType(e.target.value)}
                  style={{ marginBottom: 16 }}
                >
                  <Radio.Button value="name">Search by Name(s)</Radio.Button>
                  <Radio.Button value="ein">Search by EIN(s)</Radio.Button>
                </Radio.Group>
                <Input.TextArea
                  rows={4}
                  placeholder={
                    specificSearchType === 'name'
                      ? "Enter organization names, one per line.\ne.g.,\nGOOD SAMARITAN SOCIETY\nSALVATION ARMY"
                      : "Enter EINs, one per line.\ne.g.,\n12-3456789\n98-7654321"
                  }
                  value={searchText}
                  onChange={(e) => setSearchText(e.target.value)}
                />
                <Paragraph type="secondary" style={{ marginTop: 8 }}>
                  {specificSearchType === 'name' 
                    ? "Enter organization names to search for specific companies by name."
                    : "Enter EINs (Employer Identification Numbers) to search for specific companies."
                  }
                </Paragraph>
              </div>
            )}

            <div className="step-actions">
              <Button onClick={handlePreviousStep}>Previous Step</Button>
              <Button type="primary" onClick={handleStep2Next} style={{ marginLeft: 8 }}>
                Find Companies
              </Button>
            </div>
          </Card>
        );

      case 2:
        const step3Columns = [
          { title: 'Organization Name', dataIndex: 'campus', key: 'campus' },
          { title: 'City', dataIndex: 'city', key: 'city' },
          { title: 'State', dataIndex: 'st', key: 'st' },
          { title: 'EIN', dataIndex: 'ein', key: 'ein' },
        ];

        return (
          <Card title="Step 3: Targeting & Confirmation" className="step-card">
            <Paragraph>
              Found <strong>{step2Results.length}</strong> organizations based on your criteria.
              Please select the ones you want to include in your analysis.
            </Paragraph>
            <Alert
              message="You can select all results or choose specific ones from the table below."
              type="info"
              showIcon
              style={{ marginBottom: 20 }}
            />
            <Table
              rowSelection={{
                type: 'checkbox',
                onChange: (selectedRowKeys, selectedRows) => {
                  setStep3SelectedKeys(selectedRowKeys);
                },
                selectedRowKeys: step3SelectedKeys,
              }}
              columns={step3Columns}
              dataSource={step2Results}
              rowKey="ein" // Use EIN as unique identifier
              pagination={{ pageSize: 10 }}
              scroll={{ x: 800 }}
            />
            <div className="step-actions">
              <Button onClick={handlePreviousStep}>Previous Step</Button>
              <Button
                type="primary"
                onClick={() => setCurrentStep(3)}
                style={{ marginLeft: 8 }}
                disabled={step3SelectedKeys.length === 0}
              >
                Next Step ({step3SelectedKeys.length} selected)
              </Button>
            </div>
          </Card>
        );

      case 3:
        return (
          <Card title="Step 4: Variable Selection" className="step-card">
            <Paragraph>
              Select the data fields and variables you need
            </Paragraph>
            <Divider />

            <div className="variable-selection">
              <div className="filter-section">
                <h4>Data Field Selection</h4>
                <p>Choose fields to include in the results</p>
                <Button type="default" size="small">
                  Select Fields
                </Button>
              </div>
            </div>

            <div className="step-actions">
              <Button onClick={handlePreviousStep}>Previous Step</Button>
              <Button type="primary" onClick={() => setCurrentStep(4)} style={{ marginLeft: 8 }}>
                Next Step
              </Button>
            </div>
          </Card>
        );

      case 4:
        return (
          <Card title="Step 5: Data Export" className="step-card">
            <Paragraph>
              Configure data export format and options
            </Paragraph>
            <Divider />

            <div className="export-options">
              <div className="filter-section">
                <h4>Export Options</h4>
                <p>Choose data export format and file type</p>
                <Button type="default" size="small">
                  Configure Export
                </Button>
              </div>
            </div>

            <div className="step-actions">
              <Button onClick={handlePreviousStep}>Previous Step</Button>
              <Button type="primary" style={{ marginLeft: 8 }}>
                Execute Query
              </Button>
            </div>
          </Card>
        );

      default:
        return <div>Unknown step</div>;
    }
  };

  return (
    <div className="query-form-container">
             <div className="query-form-header">
         <Title level={2}>WRDS-Style Data Query System</Title>
         <Paragraph>
           Professional nonprofit financial data query platform with multi-step precise filtering and data export
         </Paragraph>
       </div>

      <div className="query-form-content">
                 <Steps current={currentStep} style={{ marginBottom: 24 }}>
           <Step title="Time Selection" description="Select fiscal year" />
           <Step title="Range Filtering" description="Geographic, financial, etc." />
           <Step title="Precise Targeting" description="Select organizations" />
           <Step title="Variable Selection" description="Select fields" />
           <Step title="Data Export" description="Get results" />
         </Steps>

        <div className="step-content">
          {renderStepContent()}
        </div>
      </div>

      <style jsx>{`
        .query-form-container {
          max-width: 1200px;
          margin: 0 auto;
          padding: 20px;
        }

        .query-form-header {
          text-align: center;
          margin-bottom: 30px;
        }

        .query-form-content {
          background: #fff;
          border-radius: 8px;
          padding: 24px;
          box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }

        .step-card {
          margin-bottom: 20px;
        }

        .year-selection {
          margin: 20px 0;
        }

        .loading-container {
          text-align: center;
          padding: 40px;
        }

        .select-container {
          margin-bottom: 20px;
        }

        .select-container label {
          display: block;
          margin-bottom: 8px;
          font-weight: 500;
        }

        .selection-info {
          background: #f6ffed;
          border: 1px solid #b7eb8f;
          border-radius: 6px;
          padding: 16px;
          margin: 16px 0;
        }

        .step-actions {
          margin-top: 24px;
          text-align: right;
        }

        .filter-section {
          background: #fafafa;
          border: 1px solid #d9d9d9;
          border-radius: 6px;
          padding: 16px;
          margin-bottom: 16px;
        }

        .filter-section h4 {
          margin: 0 0 8px 0;
          color: #1890ff;
        }

        .filter-section p {
          margin: 0 0 12px 0;
          color: #666;
        }

        .range-filters, .precise-filters, .variable-selection, .export-options {
          margin: 20px 0;
        }
      `}</style>
    </div>
  );
};

export default QueryForm; 