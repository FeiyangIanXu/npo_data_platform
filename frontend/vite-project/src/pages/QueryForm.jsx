import React, { useState, useEffect } from 'react';
import { Steps, Select, Button, Card, Spin, message, Typography, Row, Col, Divider } from 'antd';
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
           <Card title="Step 2: Range Filtering" className="step-card">
             <Paragraph>
               You have selected fiscal year: <strong>FY {selectedYear}</strong>
             </Paragraph>
            <Divider />
            
            <div className="range-filters">
              <Row gutter={[16, 16]}>
                                 <Col span={12}>
                   <div className="filter-section">
                     <h4>Geographic Filtering</h4>
                     <p>Filter by state, city, and other geographic locations</p>
                     <Button type="default" size="small">
                       Configure Geographic Filter
                     </Button>
                   </div>
                 </Col>
                 <Col span={12}>
                   <div className="filter-section">
                     <h4>Financial Scale Filtering</h4>
                     <p>Filter by revenue, expenses, and other financial metrics</p>
                     <Button type="default" size="small">
                       Configure Financial Filter
                     </Button>
                   </div>
                 </Col>
              </Row>
            </div>
            
                         <div className="step-actions">
               <Button onClick={handlePreviousStep}>Previous Step</Button>
               <Button type="primary" onClick={() => setCurrentStep(2)} style={{ marginLeft: 8 }}>
                 Next Step
               </Button>
             </div>
          </Card>
        );
        
             case 2:
         return (
           <Card title="Step 3: Precise Targeting" className="step-card">
             <Paragraph>
               Within the selected range, further pinpoint specific organizations
             </Paragraph>
             <Divider />
             
             <div className="precise-filters">
               <div className="filter-section">
                 <h4>Organization Name Search</h4>
                 <p>Enter organization name keywords for precise search</p>
                 <Button type="default" size="small">
                   Search Organizations
                 </Button>
               </div>
             </div>
             
             <div className="step-actions">
               <Button onClick={handlePreviousStep}>Previous Step</Button>
               <Button type="primary" onClick={() => setCurrentStep(3)} style={{ marginLeft: 8 }}>
                 Next Step
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
        return <div>未知步骤</div>;
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