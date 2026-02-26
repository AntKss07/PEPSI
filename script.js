// Paths to the default JSON files
const EXTRACTED_JSON_PATH = 'data/Health and wellness guide example_extracted.json';
const MAPPED_JSON_PATH = 'data/mapped_data.json';

// Theme Toggle
const themeToggle = document.getElementById('theme-toggle');
themeToggle.addEventListener('click', () => {
    const isDark = document.documentElement.getAttribute('data-theme') !== 'light';
    document.documentElement.setAttribute('data-theme', isDark ? 'light' : 'dark');
});

// JSON Syntax Highlighter
function syntaxHighlight(json) {
    if (typeof json != 'string') {
        json = JSON.stringify(json, undefined, 2);
    }
    json = json.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
    return json.replace(/("(\\u[a-zA-Z0-9]{4}|\\[^u]|[^\\"])*"(\s*:)?|\b(true|false|null)\b|-?\d+(?:\.\d*)?(?:[eE][+\-]?\d+)?)/g, function (match) {
        var cls = 'json-number';
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
    });
}

// Function to load and render JSON
async function loadJSON(url, contentElId, loaderElId) {
    const loader = document.getElementById(loaderElId);
    const content = document.getElementById(contentElId);
    
    try {
        const response = await fetch(url);
        if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
        
        const data = await response.json();
        
        // Hide loader, show content
        loader.classList.add('hidden');
        content.classList.remove('hidden');
        
        // Render JSON with basic formatting
        content.innerHTML = syntaxHighlight(data);
        
        // Store raw string for toggle all function
        content.setAttribute('data-raw', JSON.stringify(data, null, 2));
        content.setAttribute('data-compact', JSON.stringify(data));
        content.setAttribute('data-state', 'expanded');
    } catch (e) {
        console.warn(`Could not fetch ${url}. Please use the file upload fallback. Error:`, e);
        loader.querySelector('p').textContent = `Could not load ${url} automatically. Please select the file manually.`;
    }
}

// File Input Handler
function handleFileInput(inputId, contentElId, loaderElId) {
    document.getElementById(inputId).addEventListener('change', function(e) {
        const file = e.target.files[0];
        if (!file) return;

        const reader = new FileReader();
        reader.onload = function(e) {
            try {
                const data = JSON.parse(e.target.result);
                const loader = document.getElementById(loaderElId);
                const content = document.getElementById(contentElId);
                
                loader.classList.add('hidden');
                content.classList.remove('hidden');
                
                content.innerHTML = syntaxHighlight(data);
                content.setAttribute('data-raw', JSON.stringify(data, null, 2));
                content.setAttribute('data-compact', JSON.stringify(data));
                content.setAttribute('data-state', 'expanded');
            } catch (err) {
                alert("Invalid JSON file");
            }
        };
        reader.readAsText(file);
    });
}

// Initialize File Inputs
handleFileInput('extracted-file-input', 'extracted-content', 'extracted-loader');
handleFileInput('mapped-file-input', 'mapped-content', 'mapped-loader');

// Button Event Listeners
document.querySelectorAll('.btn-parse').forEach(btn => {
    btn.addEventListener('click', (e) => {
        const targetId = e.target.getAttribute('data-target');
        const contentEl = document.getElementById(targetId);
        
        if (contentEl.classList.contains('hidden')) return;
        
        // Add a simple pulse effect
        contentEl.style.opacity = '0.5';
        setTimeout(() => contentEl.style.opacity = '1', 200);
    });
});

document.querySelectorAll('.btn-collapse').forEach(btn => {
    btn.addEventListener('click', (e) => {
        const targetId = e.target.getAttribute('data-target');
        const contentEl = document.getElementById(targetId);
        
        if (contentEl.classList.contains('hidden')) return;
        
        const currentState = contentEl.getAttribute('data-state');
        if (currentState === 'expanded') {
            const raw = contentEl.getAttribute('data-compact');
            contentEl.innerHTML = syntaxHighlight(JSON.parse(raw));
            contentEl.setAttribute('data-state', 'collapsed');
        } else {
            const raw = contentEl.getAttribute('data-raw');
            contentEl.innerHTML = syntaxHighlight(JSON.parse(raw));
            contentEl.setAttribute('data-state', 'expanded');
        }
    });
});

// Load default files automatically
// Use setTimeout to allow visual entry animations (if added)
setTimeout(() => {
    loadJSON(EXTRACTED_JSON_PATH, 'extracted-content', 'extracted-loader');
    loadJSON(MAPPED_JSON_PATH, 'mapped-content', 'mapped-loader');
}, 500);
