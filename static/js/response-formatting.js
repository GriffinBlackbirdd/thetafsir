// Enhanced Response Formatting for Islamic AI Chat
document.addEventListener("DOMContentLoaded", function () {
  // Configuration: Holy terms to highlight
  const holyTerms = {
    // Allah and variations
    Allah: "highest",
    God: "highest",

    // Prophet Muhammad and honorifics
    Muhammad: "prophet",
    "Prophet Muhammad": "prophet",
    Prophet: "prophet",
    "Messenger of Allah": "prophet",
    ﷺ: "pbuh",
    "peace be upon him": "pbuh",
    PBUH: "pbuh",
    "(SAW)": "pbuh",
    "(pbuh)": "pbuh",

    // Quran and scripture
    Quran: "scripture",
    "Qur'an": "scripture",
    "Holy Quran": "scripture",
    Surah: "scripture",
    Ayah: "scripture",
    Ayat: "scripture",

    // Islamic concepts and pillars
    Salah: "concept",
    Salat: "concept",
    Zakat: "concept",
    Sawm: "concept",
    Hajj: "concept",
    Shahada: "concept",
    Iman: "concept",
    Ihsan: "concept",
    "Ka'ba": "concept",
    Kaaba: "concept",

    // Arabic expressions
    Bismillah: "arabic",
    Alhamdulillah: "arabic",
    SubhanAllah: "arabic",
    "Insha'Allah": "arabic",
    "Masha'Allah": "arabic",
    Astaghfirullah: "arabic",
    "Allahu Akbar": "arabic",
  };

  // Helper function: Formats the message with proper styling
  function formatMessage(text) {
    if (!text) return "";

    // 1. Handle basic markdown-style formatting
    let formattedText = text
      // Bold text
      .replace(/\*\*(.*?)\*\*/g, "<strong>$1</strong>")
      // Italic text
      .replace(/\*(.*?)\*/g, "<em>$1</em>")
      // Headers - h3
      .replace(/^### (.*?)$/gm, "<h3>$1</h3>")
      // Headers - h2
      .replace(/^## (.*?)$/gm, "<h2>$1</h2>")
      // Headers - h1
      .replace(/^# (.*?)$/gm, "<h1>$1</h1>")
      // Lists - ordered
      .replace(/^\d+\.\s+(.*?)$/gm, "<li>$1</li>")
      // Lists - unordered
      .replace(/^[\*\-]\s+(.*?)$/gm, "<li>$1</li>")
      // Block quotes
      .replace(/^>\s+(.*?)$/gm, "<blockquote>$1</blockquote>")
      // Code blocks
      .replace(/```([\s\S]*?)```/g, "<pre><code>$1</code></pre>")
      // Inline code
      .replace(/`([^`]+)`/g, "<code>$1</code>")
      // Horizontal rules
      .replace(/^---$/gm, "<hr>");

    // 2. Wrap adjacent list items in <ul> or <ol> tags
    formattedText = formattedText.replace(
      /<li>.*?<\/li>(\s*<li>.*?<\/li>)+/g,
      function (match) {
        return "<ul>" + match + "</ul>";
      }
    );

    // 3. Handle paragraphs by splitting by newline and wrapping content
    let paragraphs = formattedText.split(/\n\n+/);
    formattedText = paragraphs
      .map((para) => {
        // Skip if already wrapped in HTML tags
        if (para.trim().startsWith("<") && !para.trim().startsWith("<li>")) {
          return para;
        }
        // Skip empty paragraphs
        if (para.trim() === "") {
          return "";
        }
        // Wrap in paragraph tags
        return "<p>" + para + "</p>";
      })
      .join("");

    // 4. Highlight holy terms with appropriate styling
    Object.keys(holyTerms).forEach((term) => {
      const className = holyTerms[term];
      const regex = new RegExp(`\\b${term}\\b`, "gi");
      formattedText = formattedText.replace(regex, (match) => {
        return `<span class="holy-term ${className}">${match}</span>`;
      });
    });

    // 5. Add Arabic script special styling
    // Match Arabic text (Unicode range for Arabic characters)
    const arabicRegex =
      /[\u0600-\u06FF\u0750-\u077F\u08A0-\u08FF\uFB50-\uFDFF\uFE70-\uFEFF]+/g;
    formattedText = formattedText.replace(arabicRegex, (match) => {
      return `<span class="arabic-text">${match}</span>`;
    });

    return formattedText;
  }

  // Override the existing fetch response handler to use our formatter
  const originalFetch = window.fetch;
  window.fetch = function (url, options) {
    return originalFetch.apply(this, arguments).then((response) => {
      // Only intercept our API responses
      if (url.includes("/api/ask")) {
        // Clone the response so we can modify it
        const clonedResponse = response.clone();

        // Process the JSON response
        return clonedResponse
          .json()
          .then((data) => {
            // Create a modified response with formatted content
            if (data && data.response) {
              data.response = formatMessage(data.response);

              // Create a new response object with the modified data
              const modifiedResponse = new Response(JSON.stringify(data), {
                status: response.status,
                statusText: response.statusText,
                headers: response.headers,
              });

              return modifiedResponse;
            }
            return response;
          })
          .catch(() => {
            // If JSON parsing fails, return the original response
            return response;
          });
      }
      return response;
    });
  };

  // Inject necessary CSS for styling holy terms and formatting
  const styleElement = document.createElement("style");
  styleElement.textContent = `
    /* Formatting styles */
    .message-content h1, .message-content h2, .message-content h3 {
      margin: 1.5rem 0 1rem;
      color: var(--gold-primary);
      font-weight: 600;
    }

    .message-content h1 {
      font-size: 2.2rem;
      border-bottom: 1px solid rgba(192, 163, 110, 0.3);
      padding-bottom: 0.5rem;
    }

    .message-content h2 {
      font-size: 1.9rem;
    }

    .message-content h3 {
      font-size: 1.7rem;
    }

    .message-content p {
      margin-bottom: 1.5rem;
      line-height: 1.8;
    }

    .message-content ul, .message-content ol {
      margin: 1rem 0 1.5rem 2rem;
      padding-left: 1rem;
    }

    .message-content li {
      margin-bottom: 0.8rem;
    }

    .message-content blockquote {
      border-left: 3px solid var(--gold-primary);
      padding: 1rem 1.5rem;
      margin: 1.5rem 0;
      background: rgba(35, 10, 42, 0.5);
      border-radius: 0 0.8rem 0.8rem 0;
    }

    .message-content hr {
      border: none;
      height: 1px;
      background: linear-gradient(90deg, transparent, var(--gold-primary), transparent);
      margin: 2rem 0;
    }

    /* Holy terms highlighting */
    .holy-term {
      display: inline-block;
      padding: 0 0.3rem;
      border-radius: 0.3rem;
      transition: all 0.2s ease;
    }

    .holy-term:hover {
      transform: translateY(-2px);
    }

    .holy-term.highest {
      color: #f8d77e;
      font-weight: 600;
      background: rgba(248, 215, 126, 0.1);
      border-bottom: 1px solid rgba(248, 215, 126, 0.3);
    }

    .holy-term.prophet {
      color: #a8e6cf;
      background: rgba(168, 230, 207, 0.1);
      border-bottom: 1px solid rgba(168, 230, 207, 0.3);
    }

    .holy-term.pbuh {
      color: #a8e6cf;
      font-style: italic;
      background: rgba(168, 230, 207, 0.05);
    }

    .holy-term.scripture {
      color: #deb887;
      background: rgba(222, 184, 135, 0.1);
      border-bottom: 1px solid rgba(222, 184, 135, 0.3);
    }

    .holy-term.concept {
      color: #ffaaa5;
      background: rgba(255, 170, 165, 0.1);
      border-bottom: 1px solid rgba(255, 170, 165, 0.3);
    }

    .holy-term.arabic {
      color: #c0a36e;
      background: rgba(192, 163, 110, 0.1);
      border-bottom: 1px solid rgba(192, 163, 110, 0.3);
    }

    /* Arabic text styling */
    .arabic-text {
      font-family: var(--font-arabic);
      font-size: 1.8rem;
      direction: rtl;
      text-align: right;
      display: inline-block;
      margin: 0.5rem 0;
      line-height: 1.8;
      color: var(--gold-primary);
    }

    /* Improve code blocks */
    .message-content pre {
      background: rgba(23, 5, 26, 0.8);
      padding: 1.5rem;
      border-radius: 1rem;
      overflow-x: auto;
      margin: 1.5rem 0;
      border: 1px solid rgba(192, 163, 110, 0.3);
    }

    .message-content code {
      font-family: monospace;
      font-size: 0.9em;
      background: rgba(23, 5, 26, 0.8);
      padding: 0.3rem 0.6rem;
      border-radius: 0.4rem;
      border: 1px solid rgba(192, 163, 110, 0.2);
    }
  `;
  document.head.appendChild(styleElement);

  // Add event listener to format existing messages
  function formatExistingMessages() {
    const aiMessages = document.querySelectorAll(
      ".ai-message .message-content"
    );
    aiMessages.forEach((message) => {
      // Only format if not already formatted (check for HTML tags)
      if (
        message.innerHTML &&
        !message.innerHTML.includes('<span class="holy-term')
      ) {
        const originalText = message.textContent;
        message.innerHTML = formatMessage(originalText);
      }
    });
  }

  // Format existing messages on load and periodically check for new ones
  formatExistingMessages();
  setInterval(formatExistingMessages, 2000);
});
