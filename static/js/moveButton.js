document.addEventListener("DOMContentLoaded", function () {
  const clearButton = document.querySelector(".clear-button");

  const suggestionsBox = document.querySelector(".chat-suggestions");

  if (clearButton && suggestionsBox) {
    clearButton.parentNode.removeChild(clearButton);

    const clearButtonContainer = document.createElement("div");
    clearButtonContainer.className = "clear-button-container";
    clearButtonContainer.style.textAlign = "center";
    clearButtonContainer.style.marginTop = "2rem";

    clearButtonContainer.appendChild(clearButton);

    clearButton.style.position = "static";
    clearButton.style.transform = "none";
    clearButton.style.margin = "0 auto";

    suggestionsBox.parentNode.insertBefore(
      clearButtonContainer,
      suggestionsBox.nextSibling
    );
  } else {
    console.error("Could not find clear button or suggestions box");
  }
});
