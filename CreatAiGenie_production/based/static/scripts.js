function openTab(evt, tabName) {
    var i, tabContent, tabLinks;
    tabContent = document.getElementsByClassName("tab-content");
    for (i = 0; i < tabContent.length; i++) {
        tabContent[i].style.display = "none";
    }
    tabLinks = document.getElementsByClassName("tab-link");
    for (i = 0; i < tabLinks.length; i++) {
        tabLinks[i].classList.remove("active");
    }
    document.getElementById(tabName).style.display = "block";
    evt.currentTarget.classList.add("active");

    if (tabName === 'Signagetemplate') {
        fetchSignageTemplates();
    }
}

document.addEventListener("DOMContentLoaded", function() {
    const tabLinks = document.querySelectorAll('.tab-link');
    if (tabLinks.length > 0) {
        tabLinks[0].click(); // Open the first tab by default
    }

    const loginForm = document.getElementById('login-form');
    if (loginForm) {
        loginForm.addEventListener('submit', handleLogin);
    }

    const summarizeForm = document.getElementById('summarize-text-form');
    if (summarizeForm) {
        summarizeForm.addEventListener('submit', handleSummarize);
    }

    const generateImageForm = document.getElementById('generate-image-form');
    if (generateImageForm) {
        generateImageForm.addEventListener('submit', handleGenerateImage);
    }

    const uploadFileForm = document.getElementById('upload-file-form');
    if (uploadFileForm) {
        uploadFileForm.addEventListener('submit', handleFileUpload);
    }
});

document.getElementById('login-form').addEventListener('submit', function(event) {
    event.preventDefault();
    const email = document.getElementById('email').value;
    const password = document.getElementById('password').value;

    fetch('http://127.0.0.1:8000/auth/jwt/create/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ email, password }),
    })
    .then(response => response.json())
    .then(data => {
        if (data.access) {
            localStorage.setItem('authToken', data.access);
            localStorage.setItem('refreshToken', data.refresh);
            alert('Login successful');
            document.querySelector('.tab-link').click(); // Optionally open a tab
        } else {
            document.getElementById('login-error').textContent = 'Login failed. Please check your credentials.';
        }
    })
    .catch(error => {
        console.error('Error:', error.message);
        document.getElementById('login-error').textContent = 'An unexpected error occurred.';
    });
});

function fetchWithAuth(url, options = {}) {
    const token = localStorage.getItem('authToken');
    if (!token) {
        alert('Authentication token is missing. Please log in.');
        document.querySelector('.tab-link[data-tab="login"]').click(); // Redirect to login tab
        return Promise.reject(new Error('No authentication token found'));
    }

    return fetch(url, {
        ...options,
        headers: {
            ...options.headers,
            'Authorization': `Bearer ${token}`,  // Ensure 'Bearer' prefix
        },
    }).then(response => {
        if (response.status === 401) {  // Unauthorized
            alert('Session expired. Please log in again.');
            document.querySelector('.tab-link[data-tab="login"]').click(); // Redirect to login tab
            return Promise.reject(new Error('Unauthorized'));
        }
        return response;
    });
}

document.getElementById('summarize-text-form').addEventListener('submit', function(event) {
    event.preventDefault();
    const text = document.getElementById('text').value;

    fetchWithAuth('http://127.0.0.1:8000/summarize-text/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ text }),  // Ensure 'text' matches the serializer field name
    })
    .then(response => response.json())
    .then(data => {
        if (data['summary-result']) {
            document.getElementById('summary-result').textContent = data['summary-result'];
        } else {
            document.getElementById('summary-result').textContent = 'Failed to generate summary.';
        }
    })
    .catch(error => {
        console.error('Error:', error.message);
        document.getElementById('summary-result').textContent = 'An unexpected error occurred.';
    });
});

document.getElementById('generate-image-form').addEventListener('submit', function(event) {
    event.preventDefault();
    const prompt = document.getElementById('prompt').value;

    fetchWithAuth('http://127.0.0.1:8000/generate-image/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ prompt }),
    })
    .then(response => response.json())
    .then(data => {
        if (data.image_url) {
            const img = document.getElementById('generated-image');
            img.src = data.image_url;
            img.style.display = 'block';
        } else {
            console.error('Failed to generate image.');
        }
    })
    .catch(error => {
        console.error('Error:', error.message);
    });
});

document.getElementById('generate-extract-form').addEventListener('submit', function(event) {
    event.preventDefault();  // Prevent the default form submission behavior

    const adCopy = document.getElementById('texts').value;  // Get the input value
    const resultParagraph = document.getElementById('extract_keywords');

    // Show a loading state
    resultParagraph.textContent = 'Extracting keywords...';
    resultParagraph.className = 'loading';  // Add a class for styling loading state

    // Perform the fetch request
    fetchWithAuth('http://127.0.0.1:8000/extract-keywords/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken') // Include CSRF token if needed
        },
        body: JSON.stringify({ ad_copy: adCopy })  // Send the ad copy in the request body
    })
    .then(response => response.json())
    .then(data => {
        if (data.keywords) {
            // Join the keywords array into a comma-separated string
            resultParagraph.textContent = 'Extracted Keywords: ' + data.keywords.join(', ');
            resultParagraph.className = 'success';  // Add a class for styling success state
        } else {
            resultParagraph.textContent = 'Failed to generate keywords.';
            resultParagraph.className = 'error';  // Add a class for styling error state
        }
    })
    .catch(error => {
        console.error('Error:', error.message);  // Log the error to the console
        resultParagraph.textContent = 'An unexpected error occurred.';
        resultParagraph.className = 'error';  // Add a class for styling error state
    });
});

// Function to get CSRF token from cookies (if using Django)
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

document.getElementById('upload-file-form').addEventListener('submit', function(event) {
    event.preventDefault();
    const formData = new FormData(this);

    fetchWithAuth('http://127.0.0.1:8000/upload-file/', {
        method: 'POST',
        body: formData,
    })
    .then(response => response.json())
    .then(data => {
        document.getElementById('file-text').textContent = data.text || 'No text extracted.';
        if (data.summary) {
            document.getElementById('file-text').textContent += `\nSummary: ${data.summary}`;
        }
    })
    .catch(error => {
        console.error('Error:', error.message);
    });
});

function fetchSignageTemplates() {
    fetchWithAuth('http://127.0.0.1:8000/signagetemps/')
    .then(response => response.json())
    .then(data => {
        // Assuming you want to display signage templates
        const signageContainer = document.getElementById('Signagetemplate');
        signageContainer.innerHTML = ''; // Clear previous content
        
        data.results.forEach(template => {
            const templateDiv = document.createElement('div');
            templateDiv.classList.add('signage-template');
            templateDiv.innerHTML = `
                <h3>${template.title}</h3>
                <p>${template.description}</p>
                <img src="${template.signage_image}" alt="${template.title}" style="max-width: 100%; height: auto;">
                <p>Width: ${template.width}px</p>
                <p>Height: ${template.height}px</p>
                <p>Created At: ${new Date(template.created_at).toLocaleString()}</p>
                <p>Updated At: ${new Date(template.updated_at).toLocaleString()}</p>
            `;
            signageContainer.appendChild(templateDiv);
        });
    })
    .catch(error => {
        console.error('Error:', error.message);
    });
}

document.getElementById('signage-detail-form').addEventListener('submit', function(event) {
    event.preventDefault();
    const signageId = document.getElementById('signage-id').value;

    fetchSignageTemplateById(signageId);
});

function fetchSignageTemplateById(signageId) {
    fetchWithAuth(`http://127.0.0.1:8000/signagetempsid/${signageId}/`)
        .then(response => {
            if (!response.ok) {
                throw new Error(`Failed to fetch template: ${response.statusText}`);
            }
            return response.json();
        })
        .then(data => {
            const signageContainer = document.getElementById('signage-detail');
            signageContainer.innerHTML = ''; // Clear previous content

            if (data.signage_template) {
                const template = data.signage_template;
                const templateDiv = document.createElement('div');
                templateDiv.classList.add('signage-template');
                templateDiv.innerHTML = `
                    <h3>${template.title}</h3>
                    <p>${template.description}</p>
                    <img src="${template.signage_image}" alt="${template.title}" style="max-width: 100%; height: auto;">
                    <p>Width: ${template.width}px</p>
                    <p>Height: ${template.height}px</p>
                    <p>Created At: ${new Date(template.created_at).toLocaleString()}</p>
                    <p>Updated At: ${new Date(template.updated_at).toLocaleString()}</p>
                    <h4>Category:</h4>
                    <p>Name: ${template.category.name}</p>
                    <img src="${template.category.image}" alt="${template.category.name}" style="max-width: 100%; height: auto;">
                    <p>Description: ${template.category.description}</p>
                `;
                signageContainer.appendChild(templateDiv);
            } else {
                signageContainer.innerHTML = `<p>Template not found.</p>`;
            }
        })
        .catch(error => {
            console.error('Error:', error.message);
            document.getElementById('signage-detail').innerHTML = 'An unexpected error occurred or template not found.';
        });
}
