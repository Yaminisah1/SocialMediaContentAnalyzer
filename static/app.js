const dropZone = document.getElementById("drop-zone");
const fileInput = document.getElementById("file-input");
const selectedFileText = document.getElementById("selected-file");
const analyzeBtn = document.getElementById("analyze-btn");
const copyBtn = document.getElementById("copy-btn");
const statusEl = document.getElementById("status");
const loadingEl = document.getElementById("loading");
const resultsEl = document.getElementById("results");

const summaryEl = document.getElementById("summary");
const sourceMetaEl = document.getElementById("source-meta");
const scoreEl = document.getElementById("score");
const wordsEl = document.getElementById("words");
const hashtagsEl = document.getElementById("hashtags");
const mentionsEl = document.getElementById("mentions");
const suggestionsEl = document.getElementById("suggestions");
const extractedTextEl = document.getElementById("extracted-text");

const allowedExtensions = ["pdf", "png", "jpg", "jpeg", "tiff", "bmp", "webp"];
let selectedFile = null;

function setStatus(message, tone = "") {
  statusEl.textContent = message;
  statusEl.classList.remove("error", "ok");
  if (tone === "error") {
    statusEl.classList.add("error");
  }
  if (tone === "ok") {
    statusEl.classList.add("ok");
  }
}

function showLoading(isLoading) {
  loadingEl.classList.toggle("hidden", !isLoading);
}

function clearResults() {
  resultsEl.classList.add("hidden");
  suggestionsEl.innerHTML = "";
  extractedTextEl.textContent = "";
}

function validateFile(file) {
  if (!file) {
    return "No file selected.";
  }
  const ext = file.name.split(".").pop()?.toLowerCase() || "";
  if (!allowedExtensions.includes(ext)) {
    return "Unsupported file type. Upload PDF or image files only.";
  }
  if (file.size > 10 * 1024 * 1024) {
    return "File too large. Max size is 10 MB.";
  }
  return "";
}

function setFile(file) {
  const error = validateFile(file);
  if (error) {
    selectedFile = null;
    selectedFileText.textContent = "No file selected";
    analyzeBtn.disabled = true;
    setStatus(error, "error");
    return;
  }

  selectedFile = file;
  analyzeBtn.disabled = false;
  selectedFileText.textContent = `Selected: ${file.name} (${Math.ceil(file.size / 1024)} KB)`;
  setStatus("File ready for analysis.", "ok");
}

function populateResults(payload) {
  const { analysis } = payload;
  summaryEl.textContent = analysis.summary;
  sourceMetaEl.textContent = `Source: ${payload.source_type.toUpperCase()} | File: ${payload.filename}`;
  scoreEl.textContent = analysis.score;

  wordsEl.textContent = analysis.metrics.word_count;
  hashtagsEl.textContent = analysis.metrics.hashtag_count;
  mentionsEl.textContent = analysis.metrics.mention_count;

  extractedTextEl.textContent = payload.extracted_text;

  suggestionsEl.innerHTML = "";
  analysis.suggestions.forEach((item) => {
    const li = document.createElement("li");
    li.textContent = item;
    suggestionsEl.appendChild(li);
  });

  resultsEl.classList.remove("hidden");
}

["dragenter", "dragover"].forEach((eventName) => {
  dropZone.addEventListener(eventName, (e) => {
    e.preventDefault();
    e.stopPropagation();
    dropZone.classList.add("active");
  });
});

["dragleave", "drop"].forEach((eventName) => {
  dropZone.addEventListener(eventName, (e) => {
    e.preventDefault();
    e.stopPropagation();
    dropZone.classList.remove("active");
  });
});

dropZone.addEventListener("drop", (e) => {
  const [file] = e.dataTransfer.files;
  clearResults();
  setFile(file || null);
});

fileInput.addEventListener("change", (e) => {
  const [file] = e.target.files;
  clearResults();
  setFile(file || null);
});

analyzeBtn.addEventListener("click", async () => {
  if (!selectedFile) {
    setStatus("Choose a file before analyzing.", "error");
    return;
  }

  clearResults();
  showLoading(true);
  setStatus("Processing upload...", "");
  analyzeBtn.disabled = true;

  const formData = new FormData();
  formData.append("file", selectedFile);

  try {
    const response = await fetch("/api/analyze", {
      method: "POST",
      body: formData,
    });

    const payload = await response.json();
    if (!response.ok) {
      throw new Error(payload.error || "Unable to process file.");
    }

    populateResults(payload);
    setStatus(`Completed analysis for ${payload.filename}.`, "ok");
  } catch (error) {
    setStatus(error.message || "Unexpected error.", "error");
  } finally {
    showLoading(false);
    analyzeBtn.disabled = !selectedFile;
  }
});

copyBtn.addEventListener("click", async () => {
  const text = extractedTextEl.textContent.trim();
  if (!text) {
    setStatus("No extracted text available to copy.", "error");
    return;
  }

  try {
    await navigator.clipboard.writeText(text);
    setStatus("Extracted text copied to clipboard.", "ok");
  } catch (_err) {
    setStatus("Copy failed. Browser permissions may block clipboard access.", "error");
  }
});