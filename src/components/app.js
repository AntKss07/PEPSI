/**
 * Health Report PDF Extractor - Frontend Logic
 */

// DOM Elements
const dropzone = document.getElementById('dropzone');
const fileInput = document.getElementById('fileInput');
const fileInfo = document.getElementById('fileInfo');
const fileName = document.getElementById('fileName');
const fileSize = document.getElementById('fileSize');
const removeFile = document.getElementById('removeFile');
const processBtn = document.getElementById('processBtn');
const processingStatus = document.getElementById('processingStatus');
const resultsSection = document.getElementById('resultsSection');
const resultsStats = document.getElementById('resultsStats');
const jsonOutput = document.getElementById('jsonOutput');
const copyBtn = document.getElementById('copyBtn');
const downloadBtn = document.getElementById('downloadBtn');
const debugToggle = document.getElementById('debugToggle');
const debugPanel = document.getElementById('debugPanel');
const debugTableBody = document.getElementById('debugTableBody');
const toast = document.getElementById('toast');

// State
let selectedFile = null;
let extractedData = null;

// API Base URL
const API_BASE = '';

// Utility functions
function formatFileSize(bytes) {
    if (bytes < 1024) return bytes + ' B';
    if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB';
    return (bytes / (1024 * 1024)).toFixed(1) + ' MB';
}

function showToast(message, type = 'success') {
    toast.textContent = message;
    toast.className = `toast ${type} show`;
    setTimeout(() => {
        toast.classList.remove('show');
    }, 3000);
}

function syntaxHighlight(json) {
    if (typeof json !== 'string') {
        json = JSON.stringify(json, null, 2);
    }

    return json.replace(
        /("(\\u[a-zA-Z0-9]{4}|\\[^u]|[^\\"])*"(?:\s*:)?|\b(true|false|null)\b|-?\d+(?:\.\d*)?(?:[eE][+\-]?\d+)?)/g,
        function (match) {
            let cls = 'json-number';
            if (/^"/.test(match)) {
                if (/:$/.test(match)) {
                    cls = 'json-key';
                } else {
                    cls = 'json-string';
                }
            } else if (/true|false/.test(match)) {
                cls = 'json-boolean';
            } else if (/null/.test(match)) {
                cls = 'json-null';
            }
            return '<span class="' + cls + '">' + match + '</span>';
        }
    );
}

// File handling
function handleFile(file) {
    if (!file) return;

    if (!file.type.includes('pdf')) {
        showToast('Please select a PDF file', 'error');
        return;
    }

    selectedFile = file;

    // Update UI
    dropzone.querySelector('.dropzone-content').hidden = true;
    fileInfo.hidden = false;
    fileName.textContent = file.name;
    fileSize.textContent = formatFileSize(file.size);
    processBtn.disabled = false;
}

function clearFile() {
    selectedFile = null;
    fileInput.value = '';
    dropzone.querySelector('.dropzone-content').hidden = false;
    fileInfo.hidden = true;
    processBtn.disabled = true;
}

// Drag and drop handlers
dropzone.addEventListener('click', () => fileInput.click());

dropzone.addEventListener('dragover', (e) => {
    e.preventDefault();
    dropzone.classList.add('dragover');
});

dropzone.addEventListener('dragleave', () => {
    dropzone.classList.remove('dragover');
});

dropzone.addEventListener('drop', (e) => {
    e.preventDefault();
    dropzone.classList.remove('dragover');
    const file = e.dataTransfer.files[0];
    handleFile(file);
});

fileInput.addEventListener('change', (e) => {
    const file = e.target.files[0];
    handleFile(file);
});

removeFile.addEventListener('click', (e) => {
    e.stopPropagation();
    clearFile();
});

// Process PDF
async function processPDF() {
    if (!selectedFile) return;

    // Show loading state
    processBtn.disabled = true;
    processBtn.hidden = true;
    processingStatus.hidden = false;

    try {
        const formData = new FormData();
        formData.append('file', selectedFile);

        const response = await fetch(`${API_BASE}/api/extract`, {
            method: 'POST',
            body: formData
        });

        const result = await response.json();

        if (!result.success) {
            throw new Error(result.error || 'Extraction failed');
        }

        // Store extracted data
        extractedData = result.data;

        // Show results
        showResults(result);
        showToast(`Extracted ${result.extracted_fields} fields successfully!`);

    } catch (error) {
        console.error('Error:', error);
        showToast(error.message || 'Failed to process PDF', 'error');
    } finally {
        processBtn.hidden = false;
        processBtn.disabled = false;
        processingStatus.hidden = true;
    }
}

function showResults(result) {
    // Update stats
    resultsStats.innerHTML = `
        Extracted data from <strong>${result.filename}</strong>
    `;

    // Display JSON with syntax highlighting
    jsonOutput.innerHTML = syntaxHighlight(JSON.stringify(result.data, null, 2));

    // Generate and display Text Report
    const textReport = generateTextReport(result.data);
    document.getElementById('textOutput').textContent = textReport;

    // Populate debug table
    populateDebugTable(result.data);

    // Show results section
    resultsSection.hidden = false;
    resultsSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
}

function generateTextReport(data) {
    let report = "HEALTH AND WELLNESS - PDF EXTRACTION REPORT\n";
    report += "=".repeat(70) + "\n\n";

    if (Array.isArray(data)) {
        data.forEach(item => {
            report += `--- ${item.question} ---\n`;
            report += `${item.content}\n\n`;
            report += "=".repeat(40) + "\n\n";
        });
    }
    return report;
}

function populateDebugTable(data) {
    debugTableBody.innerHTML = '';

    if (Array.isArray(data)) {
        let lastPage = "";
        data.forEach(item => {
            // Extract page name (e.g., "Page 1") from question for grouping
            const pageMatch = item.question.match(/Page \d+/);
            const currentPage = pageMatch ? pageMatch[0] : "";

            if (currentPage && currentPage !== lastPage) {
                const headerRow = document.createElement('tr');
                headerRow.style.backgroundColor = 'var(--bg-hover)';
                headerRow.innerHTML = `
                    <td colspan="3" style="font-weight: bold; color: var(--accent-primary); border-top: 2px solid var(--border-color)">${currentPage}</td>
                `;
                debugTableBody.appendChild(headerRow);
                lastPage = currentPage;
            }

            addTableRow(item.question, item.content);
        });
    }
}

function addTableRow(key, value) {
    const row = document.createElement('tr');
    const hasValue = value && String(value).trim().length > 0;
    const displayValue = value ? String(value) : '-';

    row.innerHTML = `
        <td style="padding-left: 20px;">${key}</td>
        <td style="white-space: pre-wrap; font-family: 'Monaco', monospace; font-size: 0.8rem;">${displayValue}</td>
        <td class="${hasValue ? 'status-filled' : 'status-empty'}">
            ${hasValue ? '✓' : '—'}
        </td>
    `;
    debugTableBody.appendChild(row);
}

processBtn.addEventListener('click', processPDF);

// Copy button
copyBtn.addEventListener('click', async () => {
    if (!extractedData) return;

    try {
        await navigator.clipboard.writeText(JSON.stringify(extractedData, null, 2));
        showToast('Copied to clipboard!');
    } catch (err) {
        showToast('Failed to copy', 'error');
    }
});

// Download button
downloadBtn.addEventListener('click', () => {
    if (!extractedData) return;

    const blob = new Blob([JSON.stringify(extractedData, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'extracted_health_report.json';
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);

    showToast('JSON file downloaded!');
});

// Debug toggle
debugToggle.addEventListener('change', () => {
    debugPanel.hidden = !debugToggle.checked;
});

// View Reference
const viewReferenceBtn = document.getElementById('viewReferenceBtn');
viewReferenceBtn.addEventListener('click', async () => {
    try {
        const response = await fetch(`${API_BASE}/api/reference`);
        const result = await response.json();

        if (result.success) {
            // We'll reuse the results section to show the reference
            extractedData = result.data;
            showResults({
                success: true,
                filename: 'doc_creator.py (Reference)',
                total_fields: result.data.length,
                extracted_fields: result.data.length,
                data: result.data
            });
            showToast('Loaded reference structure from doc_creator.py');
        }
    } catch (err) {
        showToast('Failed to load reference', 'error');
    }
});

// Tab switching logic
document.querySelectorAll('.tab-btn').forEach(btn => {
    btn.addEventListener('click', () => {
        // Toggle buttons
        document.querySelectorAll('.tab-btn').forEach(b => {
            b.classList.remove('active');
            b.style.borderBottomColor = 'transparent';
        });
        btn.classList.add('active');
        btn.style.borderBottomColor = 'var(--accent-primary)';

        // Toggle content
        document.querySelectorAll('.tab-content').forEach(c => c.hidden = true);
        document.getElementById(btn.dataset.target).hidden = false;
    });
});

// Initialize
async function init() {
    console.log('Health Report PDF Extractor initialized');

    // Check API health
    try {
        const response = await fetch(`${API_BASE}/api/health`);
        const health = await response.json();
        console.log('API Status:', health);
    } catch (err) {
        console.warn('API health check failed:', err);
    }
}

init();
