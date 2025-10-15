const API_URL = "http://127.0.0.1:8000/chat/send-message";

async function sendMessage() {
  const input = document.getElementById("userInput");
  const chatBox = document.getElementById("chatBox");
  const text = input.value.trim();

  if (text === "") return;

  // მომხმარებლის შეტყობინების დამატება
  const userMsg = document.createElement("div");
  userMsg.classList.add("message", "user");
  userMsg.textContent = text;
  chatBox.appendChild(userMsg);

  // შეყვანის ველის გასუფთავება და ჩატბოქსის დაქროლვა
  input.value = "";
  chatBox.scrollTop = chatBox.scrollHeight;
  
  try {
    const response = await fetch(API_URL, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message: text })
    });

    if (!response.ok) {
      // თუ სერვერმა დააბრუნა არასწორი სტატუს კოდი (მაგ: 500, 404)
      const errorData = await response.json().catch(() => ({}));
      const errorMessage = errorData.detail || `HTTP შეცდომა: ${response.status}`;
      throw new Error(errorMessage);
    }

    const data = await response.json();

    // ბოტის შეტყობინების დამატება
    const botMsg = document.createElement("div");
    botMsg.classList.add("message", "bot");
    botMsg.textContent = data.reply || "ვერ მივიღე პასუხი.";
    chatBox.appendChild(botMsg);

  } catch (error) {
    // ქსელის ან CORS შეცდომები აქ დაიჭერება
    const errorMsg = document.createElement("div");
    errorMsg.classList.add("message", "bot");
    errorMsg.textContent = "შეცდომა: " + error.message;
    chatBox.appendChild(errorMsg);
  }

  // შეტყობინების გაგზავნის შემდეგ დაქროლვა
  chatBox.scrollTop = chatBox.scrollHeight;
}

document.getElementById("sendBtn").addEventListener("click", sendMessage);
document.getElementById("userInput").addEventListener("keypress", (e) => {
  if (e.key === "Enter") sendMessage();
});