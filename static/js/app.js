// BitNet.cpp App JavaScript

// API endpoint
const API_URL = '';

// DOM elements
const availableModelsSelect = document.getElementById('available-models');
const installedModelsSelect = document.getElementById('installed-models');
const chatModelSelect = document.getElementById('chat-model');
const quantTypeSelect = document.getElementById('quant-type');
const downloadModelButton = document.getElementById('download-model');
const removeModelButton = document.getElementById('remove-model');
const modelDetailsDiv = document.getElementById('model-details');
const chatMessagesDiv = document.getElementById('chat-messages');
const userInputTextarea = document.getElementById('user-input');
const sendMessageButton = document.getElementById('send-message');
const systemMessageTextarea = document.getElementById('system-message');
const temperatureRange = document.getElementById('temperature');
const temperatureValue = document.getElementById('temperature-value');
const maxTokensInput = document.getElementById('max-tokens');
const threadsInput = document.getElementById('threads');

// Chat messages
let messages = [];

// Initialize the app
async function init() {
    // Load available models
    await loadAvailableModels();
    
    // Load installed models
    await loadInstalledModels();
    
    // Set up event listeners
    setupEventListeners();
    
    // Update temperature value display
    updateTemperatureValue();
}

// Load available models from API
async function loadAvailableModels() {
    try {
        const response = await fetch(`${API_URL}/models/available`);
        const models = await response.json();
        
        // Clear select
        availableModelsSelect.innerHTML = '';
        
        // Add models to select
        for (const [modelId, info] of Object.entries(models)) {
            const option = document.createElement('option');
            option.value = modelId;
            option.textContent = `${info.model_name} - ${info.description}`;
            availableModelsSelect.appendChild(option);
        }
    } catch (error) {
        console.error('Error loading available models:', error);
    }
}

// Load installed models from API
async function loadInstalledModels() {
    try {
        const response = await fetch(`${API_URL}/models/installed`);
        const models = await response.json();
        
        // Clear selects
        installedModelsSelect.innerHTML = '';
        chatModelSelect.innerHTML = '';
        
        // Add models to selects
        for (const [modelName, info] of Object.entries(models)) {
            // Installed models select
            const option1 = document.createElement('option');
            option1.value = modelName;
            option1.textContent = modelName;
            installedModelsSelect.appendChild(option1);
            
            // Chat model select
            const option2 = document.createElement('option');
            option2.value = modelName;
            option2.textContent = modelName;
            chatModelSelect.appendChild(option2);
        }
        
        // Show model info for first installed model
        if (installedModelsSelect.options.length > 0) {
            showModelInfo(installedModelsSelect.value);
        }
    } catch (error) {
        console.error('Error loading installed models:', error);
    }
}

// Set up event listeners
function setupEventListeners() {
    // Download model button
    downloadModelButton.addEventListener('click', downloadModel);
    
    // Remove model button
    removeModelButton.addEventListener('click', removeModel);
    
    // Installed models select
    installedModelsSelect.addEventListener('change', () => {
        showModelInfo(installedModelsSelect.value);
    });
    
    // Send message button
    sendMessageButton.addEventListener('click', sendMessage);
    
    // User input textarea (send on Enter)
    userInputTextarea.addEventListener('keydown', (event) => {
        if (event.key === 'Enter' && !event.shiftKey) {
            event.preventDefault();
            sendMessage();
        }
    });
    
    // Temperature range
    temperatureRange.addEventListener('input', updateTemperatureValue);
}

// Update temperature value display
function updateTemperatureValue() {
    temperatureValue.textContent = temperatureRange.value;
}

// Download a model
async function downloadModel() {
    const modelId = availableModelsSelect.value;
    const quantType = quantTypeSelect.value || null;
    
    if (!modelId) {
        alert('Please select a model to download');
        return;
    }
    
    try {
        // Disable button
        downloadModelButton.disabled = true;
        downloadModelButton.innerHTML = '<span class="loading"></span> Downloading...';
        
        // Send download request
        const response = await fetch(`${API_URL}/models/download`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                model_id: modelId,
                quant_type: quantType
            })
        });
        
        const result = await response.json();
        
        // Show result
        alert(result.message);
        
        // Reload installed models
        await loadInstalledModels();
    } catch (error) {
        console.error('Error downloading model:', error);
        alert('Error downloading model. See console for details.');
    } finally {
        // Re-enable button
        downloadModelButton.disabled = false;
        downloadModelButton.textContent = 'Download';
    }
}

// Remove a model
async function removeModel() {
    const modelName = installedModelsSelect.value;
    
    if (!modelName) {
        alert('Please select a model to remove');
        return;
    }
    
    if (!confirm(`Are you sure you want to remove ${modelName}?`)) {
        return;
    }
    
    try {
        // Disable button
        removeModelButton.disabled = true;
        removeModelButton.innerHTML = '<span class="loading"></span> Removing...';
        
        // Send remove request
        const response = await fetch(`${API_URL}/models/${modelName}`, {
            method: 'DELETE'
        });
        
        const result = await response.json();
        
        // Show result
        alert(result.message);
        
        // Reload installed models
        await loadInstalledModels();
    } catch (error) {
        console.error('Error removing model:', error);
        alert('Error removing model. See console for details.');
    } finally {
        // Re-enable button
        removeModelButton.disabled = false;
        removeModelButton.textContent = 'Remove';
    }
}

// Show model info
async function showModelInfo(modelName) {
    if (!modelName) {
        modelDetailsDiv.textContent = 'No model selected';
        return;
    }
    
    try {
        // Show loading
        modelDetailsDiv.innerHTML = '<span class="loading"></span> Loading...';
        
        // Get model info
        const response = await fetch(`${API_URL}/models/${modelName}`);
        const info = await response.json();
        
        // Show info
        modelDetailsDiv.innerHTML = `
            <strong>ID:</strong> ${info.model_id}<br>
            <strong>Name:</strong> ${info.model_name}<br>
            <strong>Quantization:</strong> ${info.quant_type}<br>
            <strong>Description:</strong> ${info.description}
        `;
    } catch (error) {
        console.error('Error loading model info:', error);
        modelDetailsDiv.textContent = 'Error loading model info';
    }
}

// Send a message
async function sendMessage() {
    const model = chatModelSelect.value;
    const userInput = userInputTextarea.value.trim();
    
    if (!model) {
        alert('Please select a model');
        return;
    }
    
    if (!userInput) {
        return;
    }
    
    // Clear user input
    userInputTextarea.value = '';
    
    // Get system message if present
    const systemMessage = systemMessageTextarea.value.trim();
    
    // Add system message if not already added and not empty
    if (systemMessage && messages.length === 0) {
        messages.push({
            role: 'system',
            content: systemMessage
        });
        
        // Add system message to chat
        addMessageToChat('system', systemMessage);
    }
    
    // Add user message
    messages.push({
        role: 'user',
        content: userInput
    });
    
    // Add user message to chat
    addMessageToChat('user', userInput);
    
    // Disable send button
    sendMessageButton.disabled = true;
    sendMessageButton.innerHTML = '<span class="loading"></span> Generating...';
    
    try {
        // Get parameters
        const temperature = parseFloat(temperatureRange.value);
        const maxTokens = parseInt(maxTokensInput.value);
        const threads = parseInt(threadsInput.value);
        
        // Send chat completion request
        const response = await fetch(`${API_URL}/chat/completions`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                model: model,
                messages: messages,
                temperature: temperature,
                n_predict: maxTokens,
                threads: threads,
                ctx_size: 2048,
                stream: false
            })
        });
        
        const result = await response.json();
        
        // Get assistant response
        const assistantResponse = result.choices[0].message.content;
        
        // Add assistant message
        messages.push({
            role: 'assistant',
            content: assistantResponse
        });
        
        // Add assistant message to chat
        addMessageToChat('assistant', assistantResponse);
    } catch (error) {
        console.error('Error sending message:', error);
        addMessageToChat('system', 'Error: Failed to generate response');
    } finally {
        // Re-enable send button
        sendMessageButton.disabled = false;
        sendMessageButton.textContent = 'Send';
    }
}

// Add a message to the chat
function addMessageToChat(role, content) {
    // Create message element
    const messageDiv = document.createElement('div');
    messageDiv.classList.add('message');
    
    // Add role-specific class
    if (role === 'user') {
        messageDiv.classList.add('user-message');
    } else if (role === 'assistant') {
        messageDiv.classList.add('assistant-message');
    } else if (role === 'system') {
        messageDiv.classList.add('system-message');
    }
    
    // Set content
    messageDiv.textContent = content;
    
    // Add to chat
    chatMessagesDiv.appendChild(messageDiv);
    
    // Scroll to bottom
    chatMessagesDiv.scrollTop = chatMessagesDiv.scrollHeight;
}

// Initialize the app when the page loads
document.addEventListener('DOMContentLoaded', init);
