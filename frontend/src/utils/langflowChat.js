const LANGFLOW_SCRIPT_ID = 'langflow-embedded-chat-script';
const LANGFLOW_SCRIPT_SRC = 'https://cdn.jsdelivr.net/gh/logspace-ai/langflow-embedded-chat@v1.0.7/dist/build/static/js/bundle.min.js';
const LANGFLOW_WINDOW_TITLE = 'SafePath Agent';
const LANGFLOW_FLOW_ID = '125fb9da-a804-4347-ae7d-b7c8b350c015';
const LANGFLOW_HOST_URL = 'http://localhost:7860';
// const LANGFLOW_API_KEY = 'sk-XZOSAs4iJxFFXp0081ugpVHcgqko-eR68ZHlaoyNcAY';

function mountChatWidget(containerId) {
  const chatContainer = document.getElementById(containerId);

  if (chatContainer) {
    chatContainer.innerHTML = `
      <langflow-chat
        window_title="${LANGFLOW_WINDOW_TITLE}"
        flow_id="${LANGFLOW_FLOW_ID}"
        host_url="${LANGFLOW_HOST_URL}"

        chat_position="top-left" 
  
        width="450" 
        height="600"

        chat_window_style='{"boxShadow": "0px 4px 12px rgba(255,255,255)", "borderRadius": "12px"}'
        chat_trigger_style='{"backgroundColor": "#6366f1"}'>
      </langflow-chat>
    `;
  }
}

export function mountLangflowChat(containerId) {
  if (typeof document === 'undefined') {
    return;
  }

  if (window.customElements && window.customElements.get('langflow-chat')) {
    mountChatWidget(containerId);
    return;
  }

  const existingScript = document.getElementById(LANGFLOW_SCRIPT_ID);

  if (existingScript) {
    existingScript.addEventListener('load', () => mountChatWidget(containerId), { once: true });
    return;
  }

  const script = document.createElement('script');
  script.id = LANGFLOW_SCRIPT_ID;
  script.src = LANGFLOW_SCRIPT_SRC;
  script.onload = () => mountChatWidget(containerId);

  document.body.appendChild(script);
}
