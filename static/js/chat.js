document.addEventListener("DOMContentLoaded", function () {
  // Get DOM elements
  const messageForm = document.getElementById("message-form");
  const userInput = document.getElementById("user-input");
  const messagesContainer = document.getElementById("messages");
  const suggestions = document.querySelectorAll(".suggestion-item");

  // Flag to track if a request is in progress
  let isRequestInProgress = false;

  // Holy words to highlight
  const holyWords = [
    "Allah",
    "God",
    "Quran",
    "Qur'an",
    "Hadith",
    "Muhammad",
    "Prophet",
    "Islam",
    "Muslim",
    "Salah",
    "Prayer",
    "Hajj",
    "Zakat",
    "Sawm",
    "Fasting",
    "Ramadan",
    "Eid",
    "Bismillah",
    "Subhanallah",
    "Alhamdulillah",
    "Allahu Akbar",
    "Sunnah",
    "Sahih",
    "Surah",
    "Ayah",
    "Verse",
    "Jannah",
    "Paradise",
    "Iman",
    "Faith",
    "Taqwa",
    "Masjid",
    "Mosque",
    "Ka'bah",
    "Kaaba",
    "Ihsan",
    "Dua",
    "Supplication",
    "Dhikr",
    "Remembrance",
    "Ummah",
    "Community",
  ];

  // Format response text with markdown and highlights
  function formatResponse(text) {
    if (!text) return "";

    // Create a regex pattern for holy words (case insensitive, whole words only)
    const holyWordsPattern = new RegExp(
      "\\b(" + holyWords.join("|") + ")\\b",
      "gi"
    );

    // Apply formatting
    let formattedText = text
      // Format headings
      .replace(/^# (.*?)$/gm, '<h2 class="response-heading">$1</h2>')
      .replace(/^## (.*?)$/gm, '<h3 class="response-subheading">$1</h3>')
      .replace(/^### (.*?)$/gm, '<h4 class="response-subheading-small">$1</h4>')

      // Format bold
      .replace(/\*\*(.*?)\*\*/g, "<strong>$1</strong>")

      // Format italic
      .replace(/\*(.*?)\*/g, "<em>$1</em>")

      // Format lists
      .replace(/^\- (.*?)$/gm, "<li>$1</li>")
      .replace(/(<li>.*?<\/li>(\n|$))+/g, "<ul>$&</ul>")
      .replace(/^\d+\. (.*?)$/gm, "<li>$1</li>")
      .replace(/(<li>.*?<\/li>(\n|$))+/g, "<ol>$&</ol>")

      // Format blockquotes (for Quran verses, hadith)
      .replace(
        /^> (.*?)$/gm,
        '<blockquote class="islamic-quote">$1</blockquote>'
      )

      // Format code blocks
      .replace(/```(.*?)\n([\s\S]*?)```/g, "<pre><code>$2</code></pre>")

      // Format inline code
      .replace(/`(.*?)`/g, "<code>$1</code>")

      // Format paragraphs (any text not inside a tag)
      .replace(/^(?!<[a-z])(.*?)$/gm, function (match) {
        return match.trim() === "" ? "" : "<p>" + match + "</p>";
      })

      // Fix nested paragraphs (cleanup)
      .replace(/<p><(h|ul|ol|blockquote|pre)/g, "<$1")
      .replace(/<\/(h|ul|ol|blockquote|pre)><\/p>/g, "</$1>")

      // Fix empty paragraphs
      .replace(/<p><\/p>/g, "");

    // Highlight holy words (after other formatting to avoid processing inside HTML tags)
    formattedText = formattedText.replace(
      holyWordsPattern,
      '<span class="holy-word">$&</span>'
    );

    return formattedText;
  }

  // Process user message
  function processUserMessage(message) {
    if (isRequestInProgress) return; // Prevent multiple requests

    // Add user message
    const userMessageEl = document.createElement("div");
    userMessageEl.className = "message user-message";
    userMessageEl.innerHTML = `
      <div class="message-content">
        <p>${message}</p>
      </div>
    `;
    messagesContainer.appendChild(userMessageEl);
    scrollToBottom();

    // Show thinking indicator with crescent moon icon
    const aiThinkingMessageEl = document.createElement("div");
    aiThinkingMessageEl.className = "message ai-message thinking-message";
    aiThinkingMessageEl.innerHTML = `
      <div class="message-avatar crescent-avatar">
        <i class="fas fa-moon"></i>
      </div>
      <div class="message-content thinking-content">
        <div class="thinking-text">Thinking<span class="dot">.</span><span class="dot">.</span><span class="dot">.</span></div>
        <div class="thinking-subtext">Searching Islamic knowledge...</div>
      </div>
    `;
    messagesContainer.appendChild(aiThinkingMessageEl);
    scrollToBottom();

    // Start thinking animation
    startThinkingAnimation();

    // Set request flag
    isRequestInProgress = true;

    // Send message to API
    fetch("/api/ask", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ question: message }),
    })
      .then((response) => response.json())
      .then((data) => {
        // Remove thinking indicator
        aiThinkingMessageEl.remove();

        // Check if the user needs to purchase credits
        if (data.status === "credits_required") {
          // Add message about requiring credits
          const creditsRequiredMessageEl = document.createElement("div");
          creditsRequiredMessageEl.className = "message ai-message";
          creditsRequiredMessageEl.innerHTML = `
            <div class="message-avatar crescent-avatar">
              <i class="fas fa-moon"></i>
            </div>
            <div class="message-content">
              <p>You've used all your free credits. Please upgrade to continue using TafsirAI.</p>
            </div>
          `;
          messagesContainer.appendChild(creditsRequiredMessageEl);
          scrollToBottom();

          // Show the credit required modal if it exists in global scope
          if (window.showCreditRequiredModal) {
            window.showCreditRequiredModal();
          }

          // Reset request flag
          isRequestInProgress = false;
          return;
        }

        // Create AI response element
        const aiMessageEl = document.createElement("div");
        aiMessageEl.className = "message ai-message";

        // Format the response
        let responseText =
          data.response || "Sorry, I couldn't process your request.";
        let formattedText = formatResponse(responseText);

        // Create the response content
        aiMessageEl.innerHTML = `
          <div class="message-avatar crescent-avatar">
            <i class="fas fa-moon"></i>
          </div>
          <div class="message-content" id="latest-response">
            ${formattedText}
          </div>
        `;

        // Append to messages container
        messagesContainer.appendChild(aiMessageEl);
        scrollToBottom();

        // Log to console to verify it was added
        console.log(
          "Added AI response:",
          responseText.substring(0, 50) + "..."
        );

        // Update credit display if the function exists in global scope
        if (
          window.updateCreditDisplay &&
          data.credits_remaining !== undefined
        ) {
          window.updateCreditDisplay(
            data.credits_remaining,
            data.has_lifetime_access
          );
        }

        // Reset request flag
        isRequestInProgress = false;
      })
      .catch((error) => {
        console.error("Error:", error);

        // Remove thinking indicator
        aiThinkingMessageEl.remove();

        // Add error message
        const errorMessageEl = document.createElement("div");
        errorMessageEl.className = "message ai-message";
        errorMessageEl.innerHTML = `
          <div class="message-avatar crescent-avatar">
            <i class="fas fa-moon"></i>
          </div>
          <div class="message-content">
            <p>I'm sorry, there was an error processing your request. Please try again.</p>
          </div>
        `;
        messagesContainer.appendChild(errorMessageEl);
        scrollToBottom();

        // Reset request flag
        isRequestInProgress = false;
      });
  }

  // Thinking animation
  function startThinkingAnimation() {
    const dots = document.querySelectorAll(".thinking-message .dot");
    let dotIndex = 0;

    // Clear any existing interval
    if (window.thinkingInterval) {
      clearInterval(window.thinkingInterval);
    }

    // Set new interval
    window.thinkingInterval = setInterval(() => {
      // Reset all dots
      dots.forEach((dot) => {
        dot.style.opacity = "0.3";
        dot.style.transform = "translateY(0)";
      });

      // Highlight current dot
      dots[dotIndex].style.opacity = "1";
      dots[dotIndex].style.transform = "translateY(-5px)";

      // Move to next dot
      dotIndex = (dotIndex + 1) % dots.length;
    }, 500);
  }

  // Stop thinking animation
  function stopThinkingAnimation() {
    if (window.thinkingInterval) {
      clearInterval(window.thinkingInterval);
    }
  }

  // Handle form submission
  messageForm.addEventListener("submit", function (e) {
    e.preventDefault();
    const message = userInput.value.trim();
    if (message && !isRequestInProgress) {
      processUserMessage(message);
      userInput.value = "";
    }
  });

  // Handle suggestion clicks
  suggestions.forEach((suggestion) => {
    suggestion.addEventListener("click", function () {
      if (isRequestInProgress) return; // Prevent if request in progress

      const message = this.querySelector("span").textContent;
      processUserMessage(message);
    });
  });

  // Scroll to bottom helper
  function scrollToBottom() {
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
  }

  // Focus input field
  userInput.focus();

  // Replace all existing robot icons with crescent icons
  function replaceRobotIcons() {
    const robotIcons = document.querySelectorAll(".message-avatar i.fa-robot");
    robotIcons.forEach((icon) => {
      icon.classList.remove("fa-robot");
      icon.classList.add("fa-moon");
      icon.parentElement.classList.add("crescent-avatar");
    });
  }

  // Call once on page load
  replaceRobotIcons();

  // On window resize, ensure scrolling is at bottom
  window.addEventListener("resize", function () {
    scrollToBottom();
  });

  // Add a simple status indicator to the page
  const statusIndicator = document.createElement("div");
  statusIndicator.style.position = "fixed";
  statusIndicator.style.bottom = "10px";
  statusIndicator.style.right = "10px";
  statusIndicator.style.width = "10px";
  statusIndicator.style.height = "10px";
  statusIndicator.style.borderRadius = "50%";
  statusIndicator.style.backgroundColor = "#90EE90"; // Light green
  statusIndicator.style.display = "none";
  document.body.appendChild(statusIndicator);

  // Show status indicator when request is in progress
  function updateStatusIndicator() {
    statusIndicator.style.display = isRequestInProgress ? "block" : "none";
  }

  // Set interval to check status
  setInterval(updateStatusIndicator, 500);

  // Handle the clear chat button
  const clearChatButton = document.getElementById("clear-chat");
  if (clearChatButton) {
    clearChatButton.addEventListener("click", function () {
      // Clear all messages except the welcome message
      while (messagesContainer.children.length > 1) {
        messagesContainer.removeChild(messagesContainer.lastChild);
      }

      // Reset any animations or states
      stopThinkingAnimation();
      isRequestInProgress = false;

      // Reset input field
      userInput.value = "";
      userInput.focus();
    });
  }

  // Handle dropdown toggle
  const userDropdown = document.getElementById("user-dropdown");
  if (userDropdown) {
    userDropdown.addEventListener("click", function () {
      this.classList.toggle("active");
      const dropdownMenu = document.getElementById("dropdown-menu");
      if (dropdownMenu) {
        dropdownMenu.style.opacity = this.classList.contains("active")
          ? "1"
          : "0";
        dropdownMenu.style.visibility = this.classList.contains("active")
          ? "visible"
          : "hidden";
        dropdownMenu.style.transform = this.classList.contains("active")
          ? "translateY(0)"
          : "translateY(10px)";
      }
    });

    // Close dropdown when clicking outside
    document.addEventListener("click", function (event) {
      if (!userDropdown.contains(event.target)) {
        userDropdown.classList.remove("active");
        const dropdownMenu = document.getElementById("dropdown-menu");
        if (dropdownMenu) {
          dropdownMenu.style.opacity = "0";
          dropdownMenu.style.visibility = "hidden";
          dropdownMenu.style.transform = "translateY(10px)";
        }
      }
    });
  }
});
