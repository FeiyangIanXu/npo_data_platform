import React, { useEffect, useState } from 'react';
import {
  Alert,
  Button,
  Card,
  Checkbox,
  Col,
  Descriptions,
  Divider,
  Empty,
  Input,
  InputNumber,
  Radio,
  Row,
  Select,
  Space,
  Spin,
  Steps,
  Table,
  Tag,
  Typography,
  message,
} from 'antd';
import { DownloadOutlined, ReloadOutlined, SearchOutlined } from '@ant-design/icons';
import { useNavigate } from 'react-router-dom';

import {
  QUERY_DATASET,
  batchSearchOrganizations,
  downloadExport,
  filterOrganizations,
  getAvailableCities,
  getAvailableMonths,
  getRevenueBands,
  getAvailableStates,
  getAvailableYears,
  getDatasetFields,
} from '../api/queryApi';

const { Paragraph, Text, Title } = Typography;
const { TextArea } = Input;

const DEFAULT_SELECTED_FIELDS = [
  'ein',
  'campus',
  'city',
  'st',
  'fiscal_year',
  'fiscal_month',
  'propublica_form_type',
  'part_i_summary_12_total_revenue_cy',
  'employees',
  'propublica_filing_date',
];

const FORM_TYPE_OPTIONS = ['990', '990EO', '990PF'];
const STEP_ITEMS = [
  { title: 'Time', description: 'Year / month' },
  { title: 'Screen', description: 'Filter scope' },
  { title: 'Target', description: 'Pick orgs' },
  { title: 'Fields', description: 'Choose columns' },
  { title: 'Export', description: 'Download' },
];

function createInitialSession() {
  return {
    dataset: QUERY_DATASET,
    fiscalYear: null,
    fiscalMonth: null,
    filterMode: 'criteria',
    geoFilters: { st: null, city: null },
    financialFilters: { revenue_band_key: null, min_revenue: null, max_revenue: null },
    workforceFilters: { min_employees: null, max_employees: null },
    filingFilters: { form_types: [] },
    searchType: 'name',
    searchText: '',
    candidateResults: [],
    selectedEins: [],
    selectedFields: [],
    exportFormat: 'csv',
  };
}

function monthToName(monthNumber) {
  if (!monthNumber) {
    return '-';
  }
  const date = new Date();
  date.setMonth(monthNumber - 1);
  return date.toLocaleString('en-US', { month: 'long' });
}

function formatCurrency(value) {
  if (value === null || value === undefined || value === '') {
    return '-';
  }
  const numericValue = Number(value);
  if (Number.isNaN(numericValue)) {
    return String(value);
  }
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD',
    maximumFractionDigits: 0,
  }).format(numericValue);
}

function formatDate(value) {
  if (!value) {
    return '-';
  }
  const parsedDate = new Date(value);
  if (Number.isNaN(parsedDate.getTime())) {
    return String(value);
  }
  return parsedDate.toLocaleDateString('en-US');
}

function formatRevenueBandLabel(band) {
  if (!band) {
    return '';
  }
  return `${band.label} (${formatCurrency(band.min_revenue)} - ${formatCurrency(band.max_revenue)})`;
}

function humanizeFieldName(fieldName) {
  const overrides = {
    campus: 'Organization Name',
    ein: 'EIN',
    st: 'State',
    city: 'City',
    fiscal_year: 'Fiscal Year',
    fiscal_month: 'Fiscal Month',
    employees: 'Employees',
    propublica_form_type: 'Form Type',
    propublica_organization_name: 'ProPublica Organization Name',
    propublica_filing_date: 'Latest Filing Date',
    propublica_tax_prd: 'Tax Period',
    propublica_record_status: 'Record Status',
    propublica_filing_count: 'Filing Count',
    propublica_has_2024_plus: 'Has 2024+ Filing',
    propublica_has_2025_plus: 'Has 2025+ Filing',
    propublica_source: 'Source',
    part_i_summary_12_total_revenue_cy: 'Total Revenue',
    part_ix_statement_of_functional_expenses_25_total_functional_expenses_cy: 'Total Functional Expenses',
    part_x_balance_sheet_16_total_assets_eoy: 'Total Assets',
    part_x_balance_sheet_22_net_assets_or_fund_balances_eoy: 'Net Assets',
  };
  if (overrides[fieldName]) {
    return overrides[fieldName];
  }
  return fieldName
    .split('_')
    .filter(Boolean)
    .map((segment) => segment.charAt(0).toUpperCase() + segment.slice(1))
    .join(' ');
}

function categorizeField(fieldName) {
  const basicFields = ['ein', 'campus', 'propublica_organization_name', 'city', 'st', 'fiscal_year', 'fiscal_month'];
  if (basicFields.includes(fieldName)) {
    return 'Basic Info';
  }
  if (fieldName === 'employees') {
    return 'Workforce';
  }
  if (
    fieldName.includes('revenue') ||
    fieldName.includes('expenses') ||
    fieldName.includes('assets') ||
    fieldName.includes('balance_sheet') ||
    fieldName.includes('net_assets')
  ) {
    return 'Financials';
  }
  if (fieldName.startsWith('propublica_')) {
    return 'Filing Metadata';
  }
  return 'Other';
}

function renderFieldValue(fieldName, value) {
  if (fieldName === 'part_i_summary_12_total_revenue_cy') {
    return formatCurrency(value);
  }
  if (fieldName === 'propublica_filing_date') {
    return formatDate(value);
  }
  if (fieldName === 'fiscal_month') {
    return value ? `${value} (${monthToName(value)})` : '-';
  }
  if (typeof value === 'boolean') {
    return value ? 'Yes' : 'No';
  }
  if (value === null || value === undefined || value === '') {
    return '-';
  }
  return String(value);
}

function QueryForm() {
  const navigate = useNavigate();

  const [currentStep, setCurrentStep] = useState(0);
  const [querySession, setQuerySession] = useState(createInitialSession);
  const [availableYears, setAvailableYears] = useState([]);
  const [availableMonths, setAvailableMonths] = useState([]);
  const [availableStates, setAvailableStates] = useState([]);
  const [availableCities, setAvailableCities] = useState([]);
  const [availableRevenueBands, setAvailableRevenueBands] = useState([]);
  const [availableFields, setAvailableFields] = useState([]);
  const [loadingYears, setLoadingYears] = useState(true);
  const [loadingFields, setLoadingFields] = useState(true);
  const [loadingOptions, setLoadingOptions] = useState({ months: false, states: false, cities: false, revenueBands: false });
  const [actionLoading, setActionLoading] = useState({ step2: false, export: false });

  const updateSession = (updater) => {
    setQuerySession((previousSession) => {
      if (typeof updater === 'function') {
        return updater(previousSession);
      }
      return { ...previousSession, ...updater };
    });
  };

  useEffect(() => {
    const loadInitialContext = async () => {
      try {
        setLoadingYears(true);
        setLoadingFields(true);
        const [yearsResponse, fieldsResponse] = await Promise.all([
          getAvailableYears(),
          getDatasetFields(),
        ]);
        setAvailableYears(yearsResponse.years || []);
        setAvailableFields(fieldsResponse.fields || []);
      } catch (error) {
        console.error('Failed to load initial query context:', error);
        message.error('Failed to load the ProPublica query context. Please confirm the backend is running.');
      } finally {
        setLoadingYears(false);
        setLoadingFields(false);
      }
    };

    loadInitialContext();
  }, []);

  useEffect(() => {
    if (!availableFields.length) {
      return;
    }

    const availableNames = availableFields.map((field) => field.name);
    setQuerySession((previousSession) => {
      const selectedFields = previousSession.selectedFields.filter((field) => availableNames.includes(field));
      const defaultFields = DEFAULT_SELECTED_FIELDS.filter((field) => availableNames.includes(field));
      const nextSelectedFields = selectedFields.length > 0
        ? selectedFields
        : defaultFields.length > 0
          ? defaultFields
          : availableNames.slice(0, Math.min(8, availableNames.length));

      if (JSON.stringify(nextSelectedFields) === JSON.stringify(previousSession.selectedFields)) {
        return previousSession;
      }

      return {
        ...previousSession,
        selectedFields: nextSelectedFields,
      };
    });
  }, [availableFields]);

  useEffect(() => {
    if (!querySession.fiscalYear) {
      setAvailableMonths([]);
      setAvailableStates([]);
      setAvailableCities([]);
      setAvailableRevenueBands([]);
      return;
    }

    const loadYearBoundOptions = async () => {
      try {
        setLoadingOptions((previousState) => ({ ...previousState, months: true, states: true }));
        const [monthsResponse, statesResponse] = await Promise.all([
          getAvailableMonths(querySession.fiscalYear),
          getAvailableStates(querySession.fiscalYear),
        ]);
        const nextMonths = monthsResponse.months || [];
        const nextStates = statesResponse.states || [];
        setAvailableMonths(nextMonths);
        setAvailableStates(nextStates);

        setQuerySession((previousSession) => {
          const monthIsStillValid = nextMonths.includes(previousSession.fiscalMonth);
          const stateIsStillValid = nextStates.includes(previousSession.geoFilters.st);

          return {
            ...previousSession,
            fiscalMonth: monthIsStillValid ? previousSession.fiscalMonth : null,
            geoFilters: {
              st: stateIsStillValid ? previousSession.geoFilters.st : null,
              city: stateIsStillValid ? previousSession.geoFilters.city : null,
            },
            candidateResults: [],
            selectedEins: [],
          };
        });
      } catch (error) {
        console.error('Failed to load year-bound options:', error);
        message.error('Failed to load year-specific months and states.');
      } finally {
        setLoadingOptions((previousState) => ({ ...previousState, months: false, states: false }));
      }
    };

    loadYearBoundOptions();
  }, [querySession.fiscalYear]);

  useEffect(() => {
    if (!querySession.fiscalYear || !querySession.geoFilters.st) {
      setAvailableCities([]);
      setQuerySession((previousSession) => {
        if (previousSession.geoFilters.city === null) {
          return previousSession;
        }
        return {
          ...previousSession,
          geoFilters: {
            ...previousSession.geoFilters,
            city: null,
          },
        };
      });
      return;
    }

    const loadCities = async () => {
      try {
        setLoadingOptions((previousState) => ({ ...previousState, cities: true }));
        const response = await getAvailableCities(querySession.fiscalYear, querySession.geoFilters.st);
        const nextCities = response.cities || [];
        setAvailableCities(nextCities);

        setQuerySession((previousSession) => {
          if (previousSession.geoFilters.city && !nextCities.includes(previousSession.geoFilters.city)) {
            return {
              ...previousSession,
              geoFilters: {
                ...previousSession.geoFilters,
                city: null,
              },
            };
          }
          return previousSession;
        });
      } catch (error) {
        console.error('Failed to load cities:', error);
        message.error('Failed to load city options for the selected year and state.');
      } finally {
        setLoadingOptions((previousState) => ({ ...previousState, cities: false }));
      }
    };

    loadCities();
  }, [querySession.fiscalYear, querySession.geoFilters.st]);

  useEffect(() => {
    if (!querySession.fiscalYear) {
      setAvailableRevenueBands([]);
      return;
    }

    const loadRevenueBands = async () => {
      try {
        setLoadingOptions((previousState) => ({ ...previousState, revenueBands: true }));
        const response = await getRevenueBands(querySession.fiscalYear, querySession.fiscalMonth);
        const nextBands = response.bands || [];
        setAvailableRevenueBands(nextBands);

        setQuerySession((previousSession) => {
          const currentBandExists = nextBands.some((band) => band.key === previousSession.financialFilters.revenue_band_key);
          if (currentBandExists) {
            return previousSession;
          }

          return {
            ...previousSession,
            financialFilters: {
              revenue_band_key: null,
              min_revenue: null,
              max_revenue: null,
            },
          };
        });
      } catch (error) {
        console.error('Failed to load revenue bands:', error);
        message.error('Failed to load revenue bands for the selected time scope.');
      } finally {
        setLoadingOptions((previousState) => ({ ...previousState, revenueBands: false }));
      }
    };

    loadRevenueBands();
  }, [querySession.fiscalYear, querySession.fiscalMonth]);

  const selectedOrganizations = querySession.candidateResults.filter((organization) =>
    querySession.selectedEins.includes(organization.ein)
  );

  const sortedFields = [...availableFields].sort((leftField, rightField) => {
    const leftCategory = categorizeField(leftField.name);
    const rightCategory = categorizeField(rightField.name);
    if (leftCategory !== rightCategory) {
      return leftCategory.localeCompare(rightCategory);
    }
    return humanizeFieldName(leftField.name).localeCompare(humanizeFieldName(rightField.name));
  });

  const fieldGroups = sortedFields.reduce((groups, field) => {
    const category = categorizeField(field.name);
    if (!groups[category]) {
      groups[category] = [];
    }
    groups[category].push(field);
    return groups;
  }, {});

  const previewColumns = querySession.selectedFields.map((fieldName) => ({
    title: humanizeFieldName(fieldName),
    dataIndex: fieldName,
    key: fieldName,
    ellipsis: true,
    render: (value) => renderFieldValue(fieldName, value),
  }));

  const confirmationColumns = [
    { title: 'Organization Name', dataIndex: 'campus', key: 'campus', width: 260, ellipsis: true, render: (value) => value || '-' },
    { title: 'EIN', dataIndex: 'ein', key: 'ein', width: 120, render: (value) => value || '-' },
    { title: 'State', dataIndex: 'st', key: 'st', width: 90, render: (value) => value || '-' },
    { title: 'City', dataIndex: 'city', key: 'city', width: 150, ellipsis: true, render: (value) => value || '-' },
    { title: 'Fiscal Year', dataIndex: 'fiscal_year', key: 'fiscal_year', width: 110, render: (value) => value || '-' },
    { title: 'Fiscal Month', dataIndex: 'fiscal_month', key: 'fiscal_month', width: 140, render: (value) => value ? `${value} (${monthToName(value)})` : '-' },
    { title: 'Form Type', dataIndex: 'propublica_form_type', key: 'propublica_form_type', width: 120, render: (value) => value ? <Tag color="blue">{value}</Tag> : '-' },
    { title: 'Revenue', dataIndex: 'part_i_summary_12_total_revenue_cy', key: 'part_i_summary_12_total_revenue_cy', width: 160, render: (value) => formatCurrency(value) },
    { title: 'Employees', dataIndex: 'employees', key: 'employees', width: 110, render: (value) => value ?? '-' },
    { title: 'Latest Filing Date', dataIndex: 'propublica_filing_date', key: 'propublica_filing_date', width: 150, render: (value) => formatDate(value) },
  ];

  const handleResetQuery = () => {
    const nextSession = createInitialSession();
    const availableNames = availableFields.map((field) => field.name);
    const defaultFields = DEFAULT_SELECTED_FIELDS.filter((field) => availableNames.includes(field));
    nextSession.selectedFields = defaultFields.length > 0
      ? defaultFields
      : availableNames.slice(0, Math.min(8, availableNames.length));
    setQuerySession(nextSession);
    setCurrentStep(0);
    setAvailableMonths([]);
    setAvailableStates([]);
    setAvailableCities([]);
  };

  const handleTimeStepNext = () => {
    if (!querySession.fiscalYear) {
      message.warning('Please select a fiscal year before continuing.');
      return;
    }
    setCurrentStep(1);
  };

  const handleStep2Submit = async () => {
    if (!querySession.fiscalYear) {
      message.warning('Fiscal year is required.');
      return;
    }

    try {
      setActionLoading((previousState) => ({ ...previousState, step2: true }));
      let results = [];

      if (querySession.filterMode === 'criteria') {
        const payload = {
          fiscal_year: querySession.fiscalYear,
          fiscal_month: querySession.fiscalMonth,
        };

        if (querySession.geoFilters.st || querySession.geoFilters.city) {
          payload.geo_filters = {
            st: querySession.geoFilters.st,
            city: querySession.geoFilters.city,
          };
        }

        if (querySession.financialFilters.min_revenue !== null || querySession.financialFilters.max_revenue !== null) {
          payload.financial_filters = {
            min_revenue: querySession.financialFilters.min_revenue,
            max_revenue: querySession.financialFilters.max_revenue,
          };
        }

        if (querySession.workforceFilters.min_employees !== null || querySession.workforceFilters.max_employees !== null) {
          payload.workforce_filters = {
            min_employees: querySession.workforceFilters.min_employees,
            max_employees: querySession.workforceFilters.max_employees,
          };
        }

        if (querySession.filingFilters.form_types.length > 0) {
          payload.filing_filters = {
            form_types: querySession.filingFilters.form_types,
          };
        }

        const response = await filterOrganizations(payload);
        results = response.results || [];
      } else {
        const searchTerms = querySession.searchText.split('\n').map((term) => term.trim()).filter(Boolean);
        if (searchTerms.length === 0) {
          message.warning('Please enter at least one organization name or EIN.');
          return;
        }

        const response = await batchSearchOrganizations({
          fiscal_year: querySession.fiscalYear,
          fiscal_month: querySession.fiscalMonth,
          search_terms: searchTerms,
          search_type: querySession.searchType,
        });
        results = response.results || [];
      }

      updateSession({
        candidateResults: results,
        selectedEins: [],
      });
      setCurrentStep(2);

      if (results.length === 0) {
        message.warning('No ProPublica records matched the current query. You can go back and adjust the filters.');
      } else {
        message.success(`Found ${results.length} ProPublica records.`);
      }
    } catch (error) {
      console.error('Failed to run step 2 query:', error);
      const errorMessage = error?.response?.data?.detail || error.message || 'Unable to query ProPublica records.';
      message.error(errorMessage);
    } finally {
      setActionLoading((previousState) => ({ ...previousState, step2: false }));
    }
  };

  const handleExport = async () => {
    if (querySession.selectedEins.length === 0) {
      message.warning('Please select at least one organization before exporting.');
      return;
    }
    if (querySession.selectedFields.length === 0) {
      message.warning('Please select at least one field before exporting.');
      return;
    }

    try {
      setActionLoading((previousState) => ({ ...previousState, export: true }));
      await downloadExport(querySession.exportFormat, {
        filters: {
          ein: querySession.selectedEins,
        },
        fields: querySession.selectedFields,
        limit: querySession.selectedEins.length,
      });
      message.success(`Exported ${querySession.selectedEins.length} ProPublica records.`);
    } catch (error) {
      console.error('Export failed:', error);
      const errorMessage = error?.response?.data?.detail || error.message || 'Export failed.';
      message.error(errorMessage);
    } finally {
      setActionLoading((previousState) => ({ ...previousState, export: false }));
    }
  };

  const renderFieldGroupCard = (groupName, fields) => {
    const groupFieldNames = fields.map((field) => field.name);
    const allSelected = groupFieldNames.every((fieldName) => querySession.selectedFields.includes(fieldName));

    return (
      <Card
        key={groupName}
        size="small"
        title={`${groupName} (${fields.length})`}
        extra={
          <Space size="small">
            <Button
              size="small"
              type={allSelected ? 'default' : 'link'}
              onClick={() => {
                setQuerySession((previousSession) => ({
                  ...previousSession,
                  selectedFields: Array.from(new Set([...previousSession.selectedFields, ...groupFieldNames])),
                }));
              }}
            >
              Select all
            </Button>
            <Button
              size="small"
              type="link"
              onClick={() => {
                setQuerySession((previousSession) => ({
                  ...previousSession,
                  selectedFields: previousSession.selectedFields.filter((fieldName) => !groupFieldNames.includes(fieldName)),
                }));
              }}
            >
              Clear
            </Button>
          </Space>
        }
        style={{ height: '100%' }}
      >
        <Checkbox.Group
          value={querySession.selectedFields}
          onChange={(checkedValues) => {
            const retainedFields = querySession.selectedFields.filter((fieldName) => !groupFieldNames.includes(fieldName));
            updateSession({
              selectedFields: [...retainedFields, ...checkedValues],
            });
          }}
          style={{ width: '100%' }}
        >
          <Space direction="vertical" style={{ width: '100%' }}>
            {fields.map((field) => (
              <Checkbox key={field.name} value={field.name}>
                <Space size="small" wrap>
                  <Text>{humanizeFieldName(field.name)}</Text>
                  <Tag>{field.type}</Tag>
                </Space>
              </Checkbox>
            ))}
          </Space>
        </Checkbox.Group>
      </Card>
    );
  };

  const renderStepContent = () => {
    if (loadingYears && currentStep === 0) {
      return (
        <Card className="query-step-card">
          <div className="query-loading-state">
            <Spin size="large" />
            <Text>Loading ProPublica query context...</Text>
          </div>
        </Card>
      );
    }

    switch (currentStep) {
      case 0:
        return (
          <Card title="Step 1: Select Time Range" className="query-step-card">
            <Paragraph>
              This validation flow is locked to the ProPublica dataset. Start by choosing the fiscal year,
              then optionally narrow to a fiscal end month.
            </Paragraph>

            <Alert
              type="info"
              showIcon
              message="Dataset locked to ProPublica"
              description="Every query in this MVP will use dataset=propublica so we can validate the parallel backend path cleanly."
              style={{ marginBottom: 24 }}
            />

            <Row gutter={[16, 16]}>
              <Col xs={24} md={12}>
                <Text strong>Fiscal Year</Text>
                <Select
                  style={{ width: '100%', marginTop: 8 }}
                  placeholder="Select fiscal year"
                  value={querySession.fiscalYear}
                  onChange={(value) => {
                    updateSession((previousSession) => ({
                      ...previousSession,
                      fiscalYear: value,
                      fiscalMonth: null,
                      geoFilters: { st: null, city: null },
                      financialFilters: { revenue_band_key: null, min_revenue: null, max_revenue: null },
                      candidateResults: [],
                      selectedEins: [],
                    }));
                  }}
                  options={availableYears.map((year) => ({ label: `FY ${year}`, value: year }))}
                />
              </Col>
              <Col xs={24} md={12}>
                <Text strong>Fiscal Month (Optional)</Text>
                <Select
                  style={{ width: '100%', marginTop: 8 }}
                  placeholder="Any month"
                  value={querySession.fiscalMonth}
                  onChange={(value) => {
                    updateSession((previousSession) => ({
                      ...previousSession,
                      fiscalMonth: value,
                      financialFilters: { revenue_band_key: null, min_revenue: null, max_revenue: null },
                      candidateResults: [],
                      selectedEins: [],
                    }));
                  }}
                  allowClear
                  loading={loadingOptions.months}
                  disabled={!querySession.fiscalYear}
                  options={availableMonths.map((month) => ({ label: `${month} (${monthToName(month)})`, value: month }))}
                />
              </Col>
            </Row>

            <Descriptions bordered size="small" style={{ marginTop: 24 }}>
              <Descriptions.Item label="Dataset">{querySession.dataset}</Descriptions.Item>
              <Descriptions.Item label="Fiscal Year">
                {querySession.fiscalYear ? `FY ${querySession.fiscalYear}` : '-'}
              </Descriptions.Item>
              <Descriptions.Item label="Fiscal Month">
                {querySession.fiscalMonth ? `${querySession.fiscalMonth} (${monthToName(querySession.fiscalMonth)})` : 'Any'}
              </Descriptions.Item>
            </Descriptions>

            <div className="query-step-actions">
              <Button type="primary" onClick={handleTimeStepNext} disabled={!querySession.fiscalYear}>
                Next Step
              </Button>
              <Button onClick={() => navigate('/')}>Back to Home</Button>
            </div>
          </Card>
        );

      case 1:
        return (
          <Card title="Step 2: Universe Screening" className="query-step-card">
            <Paragraph>
              Narrow the ProPublica universe either by structured filters or by a targeted name/EIN search.
            </Paragraph>

            <Radio.Group
              value={querySession.filterMode}
              onChange={(event) => updateSession({ filterMode: event.target.value })}
              optionType="button"
              buttonStyle="solid"
            >
              <Radio.Button value="criteria">Filter by Criteria</Radio.Button>
              <Radio.Button value="search">Search by Name / EIN</Radio.Button>
            </Radio.Group>

            <Divider />

            {querySession.filterMode === 'criteria' ? (
              <Space direction="vertical" size="large" style={{ width: '100%' }}>
                <Card size="small" title="Geography">
                  <Row gutter={[16, 16]}>
                    <Col xs={24} md={12}>
                      <Text strong>State</Text>
                      <Select
                        style={{ width: '100%', marginTop: 8 }}
                        placeholder="Any state"
                        value={querySession.geoFilters.st}
                        allowClear
                        loading={loadingOptions.states}
                        onChange={(value) => {
                          updateSession((previousSession) => ({
                            ...previousSession,
                            geoFilters: { st: value, city: null },
                          }));
                        }}
                        options={availableStates.map((state) => ({ label: state, value: state }))}
                      />
                    </Col>
                    <Col xs={24} md={12}>
                      <Text strong>City</Text>
                      <Select
                        style={{ width: '100%', marginTop: 8 }}
                        placeholder="Any city"
                        value={querySession.geoFilters.city}
                        allowClear
                        loading={loadingOptions.cities}
                        disabled={!querySession.geoFilters.st}
                        onChange={(value) => {
                          updateSession((previousSession) => ({
                            ...previousSession,
                            geoFilters: { ...previousSession.geoFilters, city: value },
                          }));
                        }}
                        options={availableCities.map((city) => ({ label: city, value: city }))}
                      />
                    </Col>
                  </Row>
                </Card>

                <Card size="small" title="Financials">
                  <Text strong>Financial Scale Band</Text>
                  <Select
                    style={{ width: '100%', marginTop: 8 }}
                    placeholder="Any revenue band"
                    value={querySession.financialFilters.revenue_band_key}
                    allowClear
                    loading={loadingOptions.revenueBands}
                    onChange={(value) => {
                      const selectedBand = availableRevenueBands.find((band) => band.key === value);
                      updateSession((previousSession) => ({
                        ...previousSession,
                        financialFilters: selectedBand
                          ? {
                              revenue_band_key: selectedBand.key,
                              min_revenue: selectedBand.min_revenue,
                              max_revenue: selectedBand.max_revenue,
                            }
                          : {
                              revenue_band_key: null,
                              min_revenue: null,
                              max_revenue: null,
                            },
                      }));
                    }}
                    options={availableRevenueBands.map((band) => ({
                      label: formatRevenueBandLabel(band),
                      value: band.key,
                    }))}
                  />
                  <Text type="secondary" style={{ display: 'block', marginTop: 8 }}>
                    5M revenue increments are generated dynamically up to the maximum revenue in the selected time scope.
                  </Text>
                </Card>

                <Card size="small" title="Workforce">
                  <Row gutter={[16, 16]}>
                    <Col xs={24} md={12}>
                      <Text strong>Minimum Employees</Text>
                      <InputNumber
                        style={{ width: '100%', marginTop: 8 }}
                        placeholder="e.g. 50"
                        value={querySession.workforceFilters.min_employees}
                        onChange={(value) => {
                          updateSession((previousSession) => ({
                            ...previousSession,
                            workforceFilters: { ...previousSession.workforceFilters, min_employees: value },
                          }));
                        }}
                      />
                    </Col>
                    <Col xs={24} md={12}>
                      <Text strong>Maximum Employees</Text>
                      <InputNumber
                        style={{ width: '100%', marginTop: 8 }}
                        placeholder="e.g. 10000"
                        value={querySession.workforceFilters.max_employees}
                        onChange={(value) => {
                          updateSession((previousSession) => ({
                            ...previousSession,
                            workforceFilters: { ...previousSession.workforceFilters, max_employees: value },
                          }));
                        }}
                      />
                    </Col>
                  </Row>
                </Card>

                <Card size="small" title="Filing Metadata">
                  <Text strong>Form Type</Text>
                  <Select
                    mode="multiple"
                    style={{ width: '100%', marginTop: 8 }}
                    placeholder="Any form type"
                    value={querySession.filingFilters.form_types}
                    onChange={(value) => {
                      updateSession((previousSession) => ({
                        ...previousSession,
                        filingFilters: { ...previousSession.filingFilters, form_types: value },
                      }));
                    }}
                    options={FORM_TYPE_OPTIONS.map((formType) => ({ label: formType, value: formType }))}
                  />
                </Card>
              </Space>
            ) : (
              <Card size="small" title="Targeted Search">
                <Space direction="vertical" size="middle" style={{ width: '100%' }}>
                  <Radio.Group
                    value={querySession.searchType}
                    onChange={(event) => updateSession({ searchType: event.target.value })}
                    optionType="button"
                    buttonStyle="solid"
                  >
                    <Radio.Button value="name">Search by Name</Radio.Button>
                    <Radio.Button value="ein">Search by EIN</Radio.Button>
                  </Radio.Group>

                  <TextArea
                    rows={6}
                    value={querySession.searchText}
                    onChange={(event) => updateSession({ searchText: event.target.value })}
                    placeholder={querySession.searchType === 'name' ? 'Enter one organization name per line' : 'Enter one EIN per line'}
                  />

                  <Text type="secondary">
                    {querySession.searchType === 'name'
                      ? 'Batch name search uses the ProPublica organization name field.'
                      : 'Batch EIN search matches against the ProPublica EIN field.'}
                  </Text>
                </Space>
              </Card>
            )}

            <div className="query-step-actions">
              <Button onClick={() => setCurrentStep(0)}>Previous Step</Button>
              <Button type="primary" icon={<SearchOutlined />} onClick={handleStep2Submit} loading={actionLoading.step2}>
                Find Organizations
              </Button>
            </div>
          </Card>
        );

      case 2:
        return (
          <Card title="Step 3: Target Confirmation" className="query-step-card">
            <Paragraph>
              Review the matching ProPublica records and select the exact organizations to keep in the query set.
            </Paragraph>

            <Descriptions bordered size="small" style={{ marginBottom: 24 }}>
              <Descriptions.Item label="Candidate Results">{querySession.candidateResults.length}</Descriptions.Item>
              <Descriptions.Item label="Selected Organizations">{querySession.selectedEins.length}</Descriptions.Item>
              <Descriptions.Item label="Dataset">{querySession.dataset}</Descriptions.Item>
            </Descriptions>

            {querySession.candidateResults.length === 0 ? (
              <Empty description="No organizations are currently loaded. Go back to Step 2 and adjust the query." />
            ) : (
              <Table
                columns={confirmationColumns}
                dataSource={querySession.candidateResults}
                rowKey="ein"
                pagination={{ pageSize: 10, showSizeChanger: false }}
                scroll={{ x: 1400 }}
                rowSelection={{
                  type: 'checkbox',
                  selectedRowKeys: querySession.selectedEins,
                  preserveSelectedRowKeys: true,
                  onChange: (selectedRowKeys) => {
                    updateSession({ selectedEins: selectedRowKeys });
                  },
                }}
              />
            )}

            <div className="query-step-actions">
              <Button onClick={() => setCurrentStep(1)}>Previous Step</Button>
              <Button type="primary" onClick={() => setCurrentStep(3)} disabled={querySession.selectedEins.length === 0}>
                Next Step
              </Button>
            </div>
          </Card>
        );

      case 3:
        return (
          <Card title="Step 4: Variable Selection" className="query-step-card">
            <Paragraph>
              Pick the fields that should appear in the final ProPublica export. The preview table below updates in real time.
            </Paragraph>

            <Alert
              type="info"
              showIcon
              message="Field selection controls export output"
              description="The selected fields below will be passed to the backend export endpoint, not just shown in the browser preview."
              style={{ marginBottom: 24 }}
            />

            {loadingFields ? (
              <div className="query-loading-state">
                <Spin />
                <Text>Loading field metadata...</Text>
              </div>
            ) : (
              <Row gutter={[16, 16]}>
                {Object.entries(fieldGroups).map(([groupName, fields]) => (
                  <Col xs={24} lg={12} key={groupName}>
                    {renderFieldGroupCard(groupName, fields)}
                  </Col>
                ))}
              </Row>
            )}

            <Divider />

            <Space direction="vertical" size="small" style={{ width: '100%', marginBottom: 16 }}>
              <Title level={5} style={{ marginBottom: 0 }}>Preview</Title>
              <Text type="secondary">
                Showing {selectedOrganizations.length} selected organizations across {querySession.selectedFields.length} fields.
              </Text>
            </Space>

            {selectedOrganizations.length === 0 ? (
              <Empty description="No organizations selected yet." />
            ) : (
              <Table
                columns={previewColumns}
                dataSource={selectedOrganizations}
                rowKey="ein"
                pagination={{ pageSize: 5, showSizeChanger: false }}
                scroll={{ x: 1000 }}
              />
            )}

            <div className="query-step-actions">
              <Button onClick={() => setCurrentStep(2)}>Previous Step</Button>
              <Button type="primary" onClick={() => setCurrentStep(4)} disabled={querySession.selectedFields.length === 0}>
                Next Step
              </Button>
            </div>
          </Card>
        );

      case 4:
        return (
          <Card title="Step 5: Export Output" className="query-step-card">
            <Paragraph>
              Export the selected ProPublica organizations using the exact field set you chose in Step 4.
            </Paragraph>

            <Descriptions bordered size="small" column={1} style={{ marginBottom: 24 }}>
              <Descriptions.Item label="Dataset">{querySession.dataset}</Descriptions.Item>
              <Descriptions.Item label="Fiscal Scope">
                {querySession.fiscalYear ? `FY ${querySession.fiscalYear}` : '-'}
                {querySession.fiscalMonth ? `, month ${querySession.fiscalMonth} (${monthToName(querySession.fiscalMonth)})` : ', all months'}
              </Descriptions.Item>
              <Descriptions.Item label="Selected Organizations">{querySession.selectedEins.length}</Descriptions.Item>
              <Descriptions.Item label="Selected Fields">{querySession.selectedFields.length}</Descriptions.Item>
              <Descriptions.Item label="Export Fields">
                <Space size={[4, 8]} wrap>
                  {querySession.selectedFields.map((fieldName) => (
                    <Tag key={fieldName}>{humanizeFieldName(fieldName)}</Tag>
                  ))}
                </Space>
              </Descriptions.Item>
            </Descriptions>

            <Card size="small" title="Output Format" style={{ marginBottom: 24 }}>
              <Radio.Group
                value={querySession.exportFormat}
                onChange={(event) => updateSession({ exportFormat: event.target.value })}
                optionType="button"
                buttonStyle="solid"
              >
                <Radio.Button value="csv">CSV</Radio.Button>
                <Radio.Button value="json">JSON</Radio.Button>
                <Radio.Button value="excel">Excel</Radio.Button>
              </Radio.Group>
            </Card>

            {selectedOrganizations.length > 0 && (
              <Card size="small" title="Final Preview" style={{ marginBottom: 24 }}>
                <Table
                  columns={previewColumns}
                  dataSource={selectedOrganizations.slice(0, 5)}
                  rowKey="ein"
                  pagination={false}
                  scroll={{ x: 1000 }}
                />
              </Card>
            )}

            <div className="query-step-actions">
              <Button onClick={() => setCurrentStep(3)}>Previous Step</Button>
              <Button icon={<ReloadOutlined />} onClick={handleResetQuery}>
                Restart Query
              </Button>
              <Button
                type="primary"
                icon={<DownloadOutlined />}
                onClick={handleExport}
                loading={actionLoading.export}
                disabled={querySession.selectedEins.length === 0 || querySession.selectedFields.length === 0}
              >
                Download {querySession.exportFormat.toUpperCase()}
              </Button>
            </div>
          </Card>
        );

      default:
        return null;
    }
  };

  return (
    <div className="query-form-page">
      <div className="query-form-header">
        <Space align="center" size="middle" wrap>
          <Title level={2} style={{ margin: 0 }}>WRDS-Style Query System</Title>
          <Tag color="geekblue">ProPublica Parallel Validation Path</Tag>
        </Space>
        <Paragraph type="secondary" style={{ marginTop: 8 }}>
          This MVP validates the frontend-to-backend query loop against the ProPublica dataset before any main-pipeline merge.
        </Paragraph>
      </div>

      <Card className="query-shell-card">
        <Steps current={currentStep} items={STEP_ITEMS} responsive className="query-steps" />
        <Divider />
        {renderStepContent()}
      </Card>

      <style>{`
        .query-form-page {
          max-width: 1320px;
          margin: 0 auto;
        }

        .query-form-header {
          margin-bottom: 24px;
        }

        .query-shell-card {
          border-radius: 16px;
        }

        .query-steps .ant-steps-item-content {
          min-width: 110px;
        }

        .query-steps .ant-steps-item-title,
        .query-steps .ant-steps-item-description {
          white-space: normal !important;
          overflow: visible !important;
          text-overflow: unset !important;
          word-break: break-word;
          line-height: 1.35;
        }

        .query-steps .ant-steps-item-description {
          max-width: 120px;
        }

        .query-step-card {
          border-radius: 12px;
        }

        .query-step-actions {
          display: flex;
          gap: 12px;
          justify-content: flex-end;
          flex-wrap: wrap;
          margin-top: 24px;
        }

        .query-loading-state {
          display: flex;
          flex-direction: column;
          align-items: center;
          justify-content: center;
          gap: 12px;
          min-height: 220px;
        }

        @media (max-width: 768px) {
          .query-steps .ant-steps-item-content {
            min-width: 0;
          }

          .query-steps .ant-steps-item-title {
            font-size: 13px;
          }

          .query-steps .ant-steps-item-description {
            font-size: 12px;
            max-width: 90px;
          }

          .query-step-actions {
            justify-content: stretch;
          }

          .query-step-actions .ant-btn {
            width: 100%;
          }
        }
      `}</style>
    </div>
  );
}

export default QueryForm;
