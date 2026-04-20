import axios from 'axios';

export const QUERY_DATASET = 'propublica';

const API_BASE_URL = '/api';

const apiClient = axios.create({
  baseURL: API_BASE_URL,
});

function withDataset(params = {}) {
  return {
    ...params,
    dataset: QUERY_DATASET,
  };
}

function getFilenameFromHeaders(headers, fallback) {
  const disposition = headers['content-disposition'] || '';
  const match = disposition.match(/filename="?([^"]+)"?/i);
  return match?.[1] || fallback;
}

function triggerBrowserDownload(blob, filename) {
  const url = window.URL.createObjectURL(blob);
  const link = document.createElement('a');
  link.href = url;
  link.download = filename;
  document.body.appendChild(link);
  link.click();
  link.remove();
  window.URL.revokeObjectURL(url);
}

export async function getAvailableYears() {
  const response = await apiClient.get('/available-years', {
    params: withDataset(),
  });
  return response.data;
}

export async function getAvailableMonths(year) {
  const response = await apiClient.get('/available-months', {
    params: withDataset({ year }),
  });
  return response.data;
}

export async function getAvailableStates(fiscalYear) {
  const response = await apiClient.get('/available-states', {
    params: withDataset({ fiscal_year: fiscalYear }),
  });
  return response.data;
}

export async function getAvailableCities(fiscalYear, state) {
  const response = await apiClient.get('/available-cities', {
    params: withDataset({ fiscal_year: fiscalYear, state }),
  });
  return response.data;
}

export async function getRevenueBands(fiscalYears, fiscalMonth = null) {
  const fiscalYearList = Array.isArray(fiscalYears) ? fiscalYears : [fiscalYears];
  const params = {
    fiscal_years: fiscalYearList.filter(Boolean).join(','),
  };
  if (fiscalMonth !== null && fiscalMonth !== undefined) {
    params.fiscal_month = fiscalMonth;
  }

  const response = await apiClient.get('/filter/revenue-bands', {
    params: withDataset(params),
  });
  return response.data;
}

export async function filterOrganizations(payload) {
  const response = await apiClient.post('/filter/enhanced', {
    dataset: QUERY_DATASET,
    ...payload,
  });
  return response.data;
}

export async function batchSearchOrganizations(payload) {
  const response = await apiClient.post('/search/batch', {
    dataset: QUERY_DATASET,
    ...payload,
  });
  return response.data;
}

export async function getDatasetFields() {
  const response = await apiClient.get('/fields', {
    params: withDataset(),
  });
  return response.data;
}

export async function downloadExport(format, payload) {
  const extensionMap = {
    csv: 'csv',
    json: 'json',
    excel: 'xlsx',
  };

  const response = await apiClient.post(
    `/export/${format}`,
    {
      dataset: QUERY_DATASET,
      ...payload,
    },
    {
      responseType: 'blob',
    }
  );

  const extension = extensionMap[format] || format;
  const filename = getFilenameFromHeaders(
    response.headers,
    `${QUERY_DATASET}_nonprofits_export.${extension}`
  );
  triggerBrowserDownload(response.data, filename);
  return response;
}
