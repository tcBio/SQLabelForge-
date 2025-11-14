// SQLabelForge UI Application
const API_BASE = '/api';

// Application State
const AppState = {
    currentStep: 'query',
    dataset: null,
    currentRecordIndex: 0,
    labels: {},
    labelDefinitions: [],
    sessionId: null,
};

// Utility Functions
const showLoading = () => {
    document.getElementById('loading-overlay').style.display = 'flex';
};

const hideLoading = () => {
    document.getElementById('loading-overlay').style.display = 'none';
};

const showToast = (message, type = 'success') => {
    const container = document.getElementById('toast-container');
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    toast.textContent = message;
    container.appendChild(toast);

    setTimeout(() => {
        toast.remove();
    }, 3000);
};

const apiCall = async (endpoint, options = {}) => {
    try {
        const response = await fetch(`${API_BASE}${endpoint}`, {
            ...options,
            headers: {
                'Content-Type': 'application/json',
                ...options.headers,
            },
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'API request failed');
        }

        return await response.json();
    } catch (error) {
        console.error('API Error:', error);
        throw error;
    }
};

// Step Navigation
const navigateToStep = (step) => {
    // Update nav buttons
    document.querySelectorAll('.step-btn').forEach(btn => {
        btn.classList.toggle('active', btn.dataset.step === step);
    });

    // Update content sections
    document.querySelectorAll('.step-content').forEach(section => {
        section.classList.toggle('active', section.id === `step-${step}`);
    });

    AppState.currentStep = step;
};

document.querySelectorAll('.step-btn').forEach(btn => {
    btn.addEventListener('click', () => {
        navigateToStep(btn.dataset.step);
    });
});

// Health Check
document.getElementById('health-check-btn').addEventListener('click', async () => {
    try {
        showLoading();
        const health = await apiCall('/health');
        const indicator = document.getElementById('health-indicator');

        if (health.status === 'healthy') {
            indicator.classList.add('online');
            indicator.classList.remove('offline');
            showToast('System is healthy', 'success');
        } else {
            indicator.classList.add('offline');
            indicator.classList.remove('online');
            showToast('System is unhealthy', 'error');
        }
    } catch (error) {
        showToast(`Health check failed: ${error.message}`, 'error');
    } finally {
        hideLoading();
    }
});

// Query Builder
const parseQueryParameters = () => {
    const query = document.getElementById('sql-query').value;
    const paramRegex = /:(\w+)/g;
    const params = [];
    let match;

    while ((match = paramRegex.exec(query)) !== null) {
        if (!params.includes(match[1])) {
            params.push(match[1]);
        }
    }

    return params;
};

const renderQueryParameters = (params) => {
    const container = document.getElementById('query-params');
    const containerDiv = document.getElementById('query-params-container');

    if (params.length === 0) {
        containerDiv.style.display = 'none';
        return;
    }

    containerDiv.style.display = 'block';
    container.innerHTML = params.map(param => `
        <div class="form-group">
            <label for="param-${param}">${param}</label>
            <input type="text" id="param-${param}" class="form-control" placeholder="Enter value for ${param}">
        </div>
    `).join('');
};

document.getElementById('parse-params-btn').addEventListener('click', () => {
    const params = parseQueryParameters();
    renderQueryParameters(params);
    showToast(`Found ${params.length} parameters`, 'success');
});

document.getElementById('execute-query-btn').addEventListener('click', async () => {
    try {
        showLoading();

        const query = document.getElementById('sql-query').value;
        if (!query.trim()) {
            throw new Error('Query cannot be empty');
        }

        // Collect parameters
        const params = parseQueryParameters();
        const paramValues = {};
        params.forEach(param => {
            const input = document.getElementById(`param-${param}`);
            if (input) {
                paramValues[param] = input.value;
            }
        });

        // Execute query
        const result = await apiCall('/query/execute-raw', {
            method: 'POST',
            body: JSON.stringify({
                query: query,
                parameters: paramValues,
            }),
        });

        AppState.dataset = result.data;
        AppState.sessionId = result.session_id;
        AppState.labels = {};
        AppState.currentRecordIndex = 0;

        // Show result info
        document.getElementById('query-result-info').style.display = 'block';
        document.getElementById('query-result-text').textContent =
            `Retrieved ${result.row_count} rows with ${result.column_count} columns`;

        showToast('Query executed successfully!', 'success');

        // Navigate to preview
        setTimeout(() => {
            renderPreview();
            navigateToStep('preview');
        }, 1000);

    } catch (error) {
        showToast(`Query failed: ${error.message}`, 'error');
    } finally {
        hideLoading();
    }
});

// Data Preview
const renderPreview = () => {
    const dataset = AppState.dataset;
    if (!dataset || dataset.length === 0) {
        showToast('No data to preview', 'warning');
        return;
    }

    // Update row count
    document.getElementById('preview-row-count').textContent = `${dataset.length} rows`;

    // Render table header
    const columns = Object.keys(dataset[0]);
    const thead = document.getElementById('preview-thead');
    thead.innerHTML = `<tr>${columns.map(col => `<th>${col}</th>`).join('')}</tr>`;

    // Render table body (first 100 rows for performance)
    const tbody = document.getElementById('preview-tbody');
    const previewData = dataset.slice(0, 100);
    tbody.innerHTML = previewData.map(row => `
        <tr>${columns.map(col => `<td>${row[col] !== null ? row[col] : '<em>null</em>'}</td>`).join('')}</tr>
    `).join('');

    if (dataset.length > 100) {
        tbody.innerHTML += `<tr><td colspan="${columns.length}" style="text-align: center; font-style: italic; color: var(--text-secondary);">
            Showing first 100 rows of ${dataset.length} total
        </td></tr>`;
    }
};

document.getElementById('back-to-query-btn').addEventListener('click', () => {
    navigateToStep('query');
});

document.getElementById('proceed-to-label-btn').addEventListener('click', () => {
    initializeLabelingInterface();
    navigateToStep('label');
});

// Labeling Interface
const initializeLabelingInterface = () => {
    // Initialize with default labels if none exist
    if (AppState.labelDefinitions.length === 0) {
        AppState.labelDefinitions = [
            { name: 'Positive', shortcut: '1' },
            { name: 'Negative', shortcut: '2' },
        ];
    }

    renderLabelDefinitions();
    renderLabelButtons();
    updateLabelingStats();
    renderCurrentRecord();
};

const renderLabelDefinitions = () => {
    const container = document.getElementById('label-definitions');
    container.innerHTML = AppState.labelDefinitions.map((label, index) => `
        <div class="label-input-group">
            <input type="text" class="form-control" placeholder="Label name" value="${label.name}"
                onchange="updateLabelDefinition(${index}, 'name', this.value)">
            <input type="text" class="form-control" placeholder="Shortcut" value="${label.shortcut}"
                onchange="updateLabelDefinition(${index}, 'shortcut', this.value)">
            <button class="btn-icon" onclick="removeLabelDefinition(${index})">×</button>
        </div>
    `).join('');
};

const updateLabelDefinition = (index, field, value) => {
    AppState.labelDefinitions[index][field] = value;
    renderLabelButtons();
};

window.removeLabelDefinition = (index) => {
    AppState.labelDefinitions.splice(index, 1);
    renderLabelDefinitions();
    renderLabelButtons();
};

document.getElementById('add-label-btn').addEventListener('click', () => {
    AppState.labelDefinitions.push({ name: '', shortcut: '' });
    renderLabelDefinitions();
});

const renderLabelButtons = () => {
    const container = document.getElementById('label-buttons');
    container.innerHTML = AppState.labelDefinitions.map(label => `
        <button class="label-btn" onclick="applyLabel('${label.name}')">
            <span class="label-btn-text">${label.name}</span>
            <span class="label-btn-shortcut">Press ${label.shortcut}</span>
        </button>
    `).join('');
};

const renderCurrentRecord = () => {
    const dataset = AppState.dataset;
    if (!dataset || dataset.length === 0) {
        return;
    }

    const record = dataset[AppState.currentRecordIndex];
    const container = document.getElementById('current-record');

    container.innerHTML = Object.entries(record).map(([key, value]) => `
        <div class="record-field">
            <div class="field-label">${key}</div>
            <div class="field-value">${value !== null ? value : '<em>null</em>'}</div>
        </div>
    `).join('');

    // Update badge
    document.getElementById('current-record-badge').textContent =
        `Row ${AppState.currentRecordIndex + 1} / ${dataset.length}`;

    // Highlight selected label if exists
    const currentLabel = AppState.labels[AppState.currentRecordIndex];
    document.querySelectorAll('.label-btn').forEach(btn => {
        btn.classList.toggle('selected', btn.textContent.includes(currentLabel));
    });
};

window.applyLabel = (label) => {
    AppState.labels[AppState.currentRecordIndex] = label;
    updateLabelingStats();
    showToast(`Labeled as: ${label}`, 'success');

    // Auto-advance to next unlabeled record
    const nextUnlabeled = findNextUnlabeledRecord();
    if (nextUnlabeled !== -1) {
        AppState.currentRecordIndex = nextUnlabeled;
        renderCurrentRecord();
    } else {
        showToast('All records labeled!', 'success');
    }
};

const findNextUnlabeledRecord = () => {
    const dataset = AppState.dataset;
    for (let i = AppState.currentRecordIndex + 1; i < dataset.length; i++) {
        if (!AppState.labels[i]) {
            return i;
        }
    }
    return -1;
};

const updateLabelingStats = () => {
    const totalRows = AppState.dataset ? AppState.dataset.length : 0;
    const labeledRows = Object.keys(AppState.labels).length;
    const remainingRows = totalRows - labeledRows;
    const progress = totalRows > 0 ? (labeledRows / totalRows * 100) : 0;

    document.getElementById('total-rows').textContent = totalRows;
    document.getElementById('labeled-rows').textContent = labeledRows;
    document.getElementById('remaining-rows').textContent = remainingRows;
    document.getElementById('label-progress').style.width = `${progress}%`;
};

// Navigation
document.getElementById('prev-record-btn').addEventListener('click', () => {
    if (AppState.currentRecordIndex > 0) {
        AppState.currentRecordIndex--;
        renderCurrentRecord();
    }
});

document.getElementById('next-record-btn').addEventListener('click', () => {
    if (AppState.currentRecordIndex < AppState.dataset.length - 1) {
        AppState.currentRecordIndex++;
        renderCurrentRecord();
    }
});

document.getElementById('skip-record-btn').addEventListener('click', () => {
    const nextUnlabeled = findNextUnlabeledRecord();
    if (nextUnlabeled !== -1) {
        AppState.currentRecordIndex = nextUnlabeled;
        renderCurrentRecord();
    } else {
        showToast('No more unlabeled records', 'info');
    }
});

// Keyboard Shortcuts
document.addEventListener('keydown', (e) => {
    if (AppState.currentStep !== 'label' || !AppState.dataset) {
        return;
    }

    // Prevent shortcuts when typing in input fields
    if (e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA') {
        return;
    }

    // Arrow keys for navigation
    if (e.key === 'ArrowLeft') {
        e.preventDefault();
        document.getElementById('prev-record-btn').click();
    } else if (e.key === 'ArrowRight') {
        e.preventDefault();
        document.getElementById('next-record-btn').click();
    } else if (e.key === ' ') {
        e.preventDefault();
        document.getElementById('skip-record-btn').click();
    } else {
        // Number keys for quick labeling
        const label = AppState.labelDefinitions.find(l => l.shortcut === e.key);
        if (label) {
            e.preventDefault();
            applyLabel(label.name);
        }
    }
});

// Export
document.getElementById('back-to-label-btn').addEventListener('click', () => {
    navigateToStep('label');
});

const updateExportSummary = () => {
    const totalRows = AppState.dataset ? AppState.dataset.length : 0;
    const labeledRows = Object.keys(AppState.labels).length;
    const completion = totalRows > 0 ? Math.round(labeledRows / totalRows * 100) : 0;

    document.getElementById('export-total-rows').textContent = totalRows;
    document.getElementById('export-labeled-rows').textContent = labeledRows;
    document.getElementById('export-completion').textContent = `${completion}%`;
};

// Update export summary when navigating to export step
document.querySelector('[data-step="export"]').addEventListener('click', () => {
    updateExportSummary();
});

document.getElementById('export-dataset-btn').addEventListener('click', async () => {
    try {
        showLoading();

        const format = document.getElementById('export-format').value;
        const filename = document.getElementById('export-filename').value || 'labeled_dataset';
        const includeUnlabeled = document.getElementById('include-unlabeled').checked;

        // Prepare export data
        const exportData = AppState.dataset.map((row, index) => ({
            ...row,
            label: AppState.labels[index] || null,
        }));

        // Filter if needed
        const filteredData = includeUnlabeled
            ? exportData
            : exportData.filter(row => row.label !== null);

        // Download as JSON (can be enhanced to support other formats)
        const blob = new Blob([JSON.stringify(filteredData, null, 2)], { type: 'application/json' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `${filename}.${format === 'json' ? 'json' : 'csv'}`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);

        showToast('Dataset exported successfully!', 'success');

    } catch (error) {
        showToast(`Export failed: ${error.message}`, 'error');
    } finally {
        hideLoading();
    }
});

// Strategy change handler
document.getElementById('label-strategy').addEventListener('change', (e) => {
    const strategy = e.target.value;
    const rulePanel = document.getElementById('rule-based-panel');

    if (strategy === 'rule_based') {
        rulePanel.style.display = 'block';
    } else {
        rulePanel.style.display = 'none';
    }
});

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    console.log('SQLabelForge UI initialized');
    // Perform initial health check
    document.getElementById('health-check-btn').click();
});
