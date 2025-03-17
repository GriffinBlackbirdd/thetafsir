// ===== SCROLL ANIMATIONS =====
const observerOptions = {
  root: null,
  rootMargin: "0px",
  threshold: 0.1,
};

// Fade in elements when they enter viewport
function fadeInOnScroll() {
  const elementsToAnimate = [
    ...document.querySelectorAll(".section-header"),
    ...document.querySelectorAll(".benefit-item"),
    ...document.querySelectorAll(".about-text p"),
    ...document.querySelectorAll(".quran-quote"),
    ...document.querySelectorAll(".app-visual"),
    ...document.querySelectorAll(".hero-feature"),
    ...document.querySelectorAll(".chat-simulation"),
    ...document.querySelectorAll(".ai-info h3"),
    ...document.querySelectorAll(".ai-info p"),
  ];

  const observer = new IntersectionObserver((entries) => {
    entries.forEach((entry) => {
      if (entry.isIntersecting) {
        // Add animation class
        entry.target.classList.add("animate");
        // Stop observing after animation is triggered
        observer.unobserve(entry.target);
      }
    });
  }, observerOptions);

  // Add observer to each element
  elementsToAnimate.forEach((element) => {
    // Add base animation class
    element.classList.add("fade-animation");
    observer.observe(element);
  });
}

// Add staggered animations to feature cards
function staggerBenefitItems() {
  const benefitItems = document.querySelectorAll(".benefit-item");
  benefitItems.forEach((item, index) => {
    item.style.transitionDelay = `${index * 0.1}s`;
  });

  const heroFeatures = document.querySelectorAll(".hero-feature");
  heroFeatures.forEach((feature, index) => {
    feature.style.transitionDelay = `${index * 0.1}s`;
  });
}

// Add animation styles
function addAnimationStyles() {
  const styleEl = document.createElement("style");
  styleEl.textContent = `
      .fade-animation {
          opacity: 0;
          transform: translateY(30px);
          transition: opacity 0.8s ease, transform 0.8s ease;
      }

      .fade-animation.animate {
          opacity: 1;
          transform: translateY(0);
      }
  `;
  document.head.appendChild(styleEl);
}

// Initialize animations
addAnimationStyles();
fadeInOnScroll();
staggerBenefitItems();

// ===== DYNAMIC YEAR =====
document.getElementById("year").textContent = new Date().getFullYear();

// ===== WINDOW RESIZE HANDLER =====
function handleResize() {
  // Adjust any responsive elements that need JavaScript
  if (window.innerWidth <= 768) {
    // Mobile specific adjustments
  } else {
    // Desktop specific adjustments
  }
}

window.addEventListener("resize", handleResize);

// Initial call to set correct states
handleResize();

// Chat Simulation Animation
function initChatSimulation() {
  // Elements
  const chatMessages = document.querySelector(".chat-messages");
  const aiMessage = document.querySelector(".ai-message");
  const typingIndicator = document.querySelector(".typing-indicator");
  const suggestionChips = document.querySelectorAll(".suggestion-chip");

  // Predefined responses
  const responses = [
    `The Quran highly values seeking knowledge. In Surah Al-Alaq (96:1-5), the first revelation to Prophet Muhammad ﷺ begins with "Read!" (اقْرَأْ). In Surah Ta-Ha (20:114), Allah says "...say, 'My Lord, increase me in knowledge.'" The Quran also states in Surah Az-Zumar (39:9): "Are those who know equal to those who do not know?"`,

    `Fasting (Sawm) is one of the Five Pillars of Islam. The Quran states in Surah Al-Baqarah (2:183): "O you who believe, fasting is prescribed for you as it was prescribed for those before you, that you may become righteous." Fasting during Ramadan helps develop self-discipline, empathy for the less fortunate, and spiritual growth.`,

    `The five daily prayers (Salah) are Fajr (dawn), Dhuhr (noon), Asr (afternoon), Maghrib (sunset), and Isha (night). The Quran mentions in Surah Al-Isra (17:78): "Establish prayer at the decline of the sun until the darkness of the night and the Quran of dawn. Indeed, the recitation of dawn is ever witnessed."`,

    `Hajj is the annual Islamic pilgrimage to Mecca, required once in a lifetime for those who are physically and financially able. The rituals include Tawaf (circling the Kaaba), Sa'i (walking between Safa and Marwa), standing at Arafat, and stoning the pillars representing Satan.`,
  ];

  // Function to simulate typing and response
  function simulateResponse() {
    // Wait for 2 seconds, then show response
    setTimeout(() => {
      // Hide typing indicator
      typingIndicator.style.display = "none";

      // Show actual response
      const messageContent = aiMessage.querySelector(".message-content");
      messageContent.innerHTML = responses[0]; // Use the first response

      // Show suggestion chips after response is shown
      setTimeout(() => {
        suggestionChips.forEach((chip) => {
          chip.style.opacity = "1";
          chip.style.transform = "translateY(0)";
        });
      }, 500);
    }, 3000);
  }

  // Function to change questions and responses
  function cycleMessages() {
    let currentIndex = 0;
    const questions = [
      "What does the Quran say about seeking knowledge?",
      "Tell me about fasting in Islam",
      "What are the five daily prayers?",
      "Can you explain the rituals of Hajj?",
    ];

    // Change question and response every 12 seconds
    setInterval(() => {
      // Update to next message
      currentIndex = (currentIndex + 1) % questions.length;

      // Update user message
      const userMessage = document.querySelector(
        ".user-message .message-content"
      );
      userMessage.textContent = questions[currentIndex];
      userMessage.style.animation = "none";
      setTimeout(() => {
        userMessage.style.animation = "slideFromRight 0.4s forwards";
      }, 10);

      // Show typing indicator
      typingIndicator.style.display = "flex";

      // Hide suggestion chips
      suggestionChips.forEach((chip) => {
        chip.style.opacity = "0";
        chip.style.transform = "translateY(1rem)";
      });

      // Show AI response after delay
      setTimeout(() => {
        typingIndicator.style.display = "none";

        // Update AI message
        const messageContent = aiMessage.querySelector(".message-content");
        messageContent.innerHTML = responses[currentIndex];
        messageContent.style.animation = "none";
        setTimeout(() => {
          messageContent.style.animation = "slideFromLeft 0.5s forwards";
        }, 10);

        // Show suggestion chips after response is shown
        setTimeout(() => {
          suggestionChips.forEach((chip) => {
            chip.style.opacity = "1";
            chip.style.transform = "translateY(0)";
          });
        }, 500);
      }, 3000);
    }, 12000);
  }

  // Initialize the message cycling
  function initMessageCycle() {
    // Start with initial response
    simulateResponse();

    // Add click events to suggestion chips
    suggestionChips.forEach((chip, index) => {
      chip.addEventListener("click", () => {
        // Update user message with chip text
        const userMessage = document.querySelector(
          ".user-message .message-content"
        );
        userMessage.textContent = chip.textContent;
        userMessage.style.animation = "none";
        setTimeout(() => {
          userMessage.style.animation = "slideFromRight 0.4s forwards";
        }, 10);

        // Show typing indicator
        typingIndicator.style.display = "flex";

        // Hide suggestion chips
        suggestionChips.forEach((c) => {
          c.style.opacity = "0";
          c.style.transform = "translateY(1rem)";
        });

        // Show corresponding AI response after delay
        setTimeout(() => {
          typingIndicator.style.display = "none";

          // Use index or default to first response
          const messageContent = aiMessage.querySelector(".message-content");
          messageContent.innerHTML = responses[index] || responses[0];
          messageContent.style.animation = "none";
          setTimeout(() => {
            messageContent.style.animation = "slideFromLeft 0.5s forwards";
          }, 10);

          // Show suggestion chips after response is shown
          setTimeout(() => {
            suggestionChips.forEach((c) => {
              c.style.opacity = "1";
              c.style.transform = "translateY(0)";
            });
          }, 500);
        }, 3000);
      });
    });

    // Start message cycling after initial interaction
    setTimeout(() => {
      cycleMessages();
    }, 15000);
  }

  // Start the chat simulation
  initMessageCycle();
}

// ===== PRELOADER =====
document.addEventListener("DOMContentLoaded", function () {
  const preloader = document.querySelector(".preloader");
  const appContainer = document.querySelector(".app-container");

  // Show preloader for minimum time (2 seconds)
  setTimeout(() => {
    preloader.classList.add("fade-out");
    appContainer.classList.add("visible");

    // Remove preloader from DOM after fade out animation
    setTimeout(() => {
      preloader.style.display = "none";
    }, 500);
  }, 2000);

  // ===== MOBILE MENU TOGGLE =====
  const menuToggle = document.getElementById("menu-toggle");
  const navLinks = document.querySelector(".nav-links");

  // Create nav overlay
  const navOverlay = document.createElement("div");
  navOverlay.className = "nav-overlay";
  document.body.appendChild(navOverlay);

  function toggleMenu() {
    menuToggle.classList.toggle("active");
    navLinks.classList.toggle("active");
    navOverlay.classList.toggle("active");

    // Prevent body scrolling when menu is open
    document.body.style.overflow = menuToggle.classList.contains("active")
      ? "hidden"
      : "";
  }

  menuToggle.addEventListener("click", toggleMenu);
  navOverlay.addEventListener("click", toggleMenu);

  // Close menu when clicking a nav link
  document.querySelectorAll(".nav-link").forEach((link) => {
    link.addEventListener("click", () => {
      if (menuToggle.classList.contains("active")) {
        toggleMenu();
      }
    });
  });

  // ===== STICKY NAVIGATION =====
  const nav = document.querySelector(".main-nav");
  let lastScrollY = window.scrollY;

  function handleScroll() {
    const currentScrollY = window.scrollY;

    // Add/remove scrolled class based on scroll position
    if (currentScrollY > 50) {
      nav.classList.add("scrolled");
    } else {
      nav.classList.remove("scrolled");
    }

    lastScrollY = currentScrollY;
  }

  window.addEventListener("scroll", handleScroll);

  // ===== SMOOTH SCROLLING =====
  document.querySelectorAll('a[href^="#"]').forEach((anchor) => {
    anchor.addEventListener("click", function (e) {
      e.preventDefault();

      const targetId = this.getAttribute("href");

      if (targetId === "#") return;

      const targetElement = document.querySelector(targetId);

      if (targetElement) {
        // Calculate offset for fixed navbar
        const navHeight = nav.offsetHeight;
        const targetPosition =
          targetElement.getBoundingClientRect().top + window.scrollY;

        window.scrollTo({
          top: targetPosition - navHeight,
          behavior: "smooth",
        });
      }
    });
  });

  // Initialize chat simulation when AI assistant section is visible
  const observer = new IntersectionObserver(
    (entries) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          initChatSimulation();
          observer.unobserve(entry.target);
        }
      });
    },
    { threshold: 0.3 }
  );

  const aiSection = document.getElementById("ai-assistant");
  if (aiSection) {
    observer.observe(aiSection);
  }

  // Add animation for benefit items
  const benefitItems = document.querySelectorAll(".benefit-item");

  if (benefitItems.length > 0) {
    benefitItems.forEach((item, index) => {
      // Add staggered animation delay
      item.style.opacity = "0";
      item.style.transform = "translateX(-20px)";
      item.style.transition = "opacity 0.5s ease, transform 0.5s ease";
      item.style.transitionDelay = `${index * 0.15}s`;

      // Create observer for each item
      const observer = new IntersectionObserver(
        (entries) => {
          entries.forEach((entry) => {
            if (entry.isIntersecting) {
              entry.target.style.opacity = "1";
              entry.target.style.transform = "translateX(0)";
              observer.unobserve(entry.target);
            }
          });
        },
        { threshold: 0.1 }
      );

      observer.observe(item);
    });
  }
});
