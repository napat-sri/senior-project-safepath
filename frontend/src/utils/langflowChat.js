import { getUserId } from './identity';

const LANGFLOW_SCRIPT_ID = 'langflow-embedded-chat-script';
const LANGFLOW_SCRIPT_SRC = 'https://cdn.jsdelivr.net/gh/logspace-ai/langflow-embedded-chat@v1.0.7/dist/build/static/js/bundle.min.js';
const LANGFLOW_WINDOW_TITLE = 'SafePath Bot';
const LANGFLOW_FLOW_ID = process.env.VUE_APP_LANGFLOW_CHATBOT_FLOW_ID;
const LANGFLOW_API_KEY = process.env.VUE_APP_LANGFLOW_API_KEY;
//console.log("FLOW_ID: ", LANGFLOW_FLOW_ID);
//console.log("API_KEY: ", LANGFLOW_API_KEY);
const LANGFLOW_HOST_URL = process.env.VUE_APP_LANGFLOW_HOST
//console.log("HOST_URL: ", LANGFLOW_HOST_URL)

function mountChatWidget(containerId) {
  const chatContainer = document.getElementById(containerId);

  if (chatContainer) {
    // Chat session_id = "chat_" + guest id. The guest id identifies the visitor
    // (filter Session ID in TEXT mode by it to see all their activity), while the
    // "chat_" prefix namespaces this flow so it never shares an Agent-memory
    // bucket with the route flow ("route_...") — that shared-session bleed is
    // what makes the chatbot hallucinate route JSON. getUserId() returns the
    // guest id today; once auth lands it returns the member id — no change here.
    const sessionId = `chat_${getUserId()}`;
    chatContainer.innerHTML = `
      <langflow-chat
        window_title="${LANGFLOW_WINDOW_TITLE}"
        flow_id="${LANGFLOW_FLOW_ID}"
        host_url="${LANGFLOW_HOST_URL}"
        api_key="${LANGFLOW_API_KEY}"
        session_id="${sessionId}"

        chat_position="top-left"
  
        width="450" 
        height="600"

        chat_window_style='{"boxShadow": "0px 4px 12px rgba(0,0,0,0.5)", "borderRadius": "12px"}'
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