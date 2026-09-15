(() => {
  "use strict";

  const translations = {
    en: {
      title: "Many Paths", subtitle: "A spiritual companion", eyebrow: "Wisdom without hierarchy",
      welcome: "Bring the question that is alive in you.",
      intro: "Explore Hindu, Buddhist and other major spiritual traditions side by side. No path is presented as superior.",
      placeholder: "Ask a spiritual question…", ask: "Ask", clear: "Clear conversation",
      privacy: "Everything stays on this device.",
      disclaimer: "Curated perspectives for reflection—not divine authority, medical advice or crisis support.",
      unknown: "I do not yet have a reviewed answer for that question. I have saved the topic only on this device so the knowledge base can be expanded later.",
      tryTopics: "Try asking about self, suffering, God, meditation, karma, death, purpose, prayer, forgiveness or inner peace.",
      sources: "Sources to explore", reflection: "For reflection", common: "Common ground and differences",
      clearConfirm: "Clear this conversation?"
    },
    ta: {
      title: "பல பாதைகள்", subtitle: "ஓர் ஆன்மிகத் துணை", eyebrow: "படிநிலையற்ற ஞானம்",
      welcome: "உங்களுக்குள் உயிரோடு இருக்கும் கேள்வியைக் கேளுங்கள்.",
      intro: "இந்து, பௌத்த மற்றும் பிற முக்கிய ஆன்மிக மரபுகளின் பார்வைகளைச் சமமாக ஆராயுங்கள்.",
      placeholder: "ஓர் ஆன்மிகக் கேள்வியைக் கேளுங்கள்…", ask: "கேள்", clear: "உரையாடலை அழி",
      privacy: "அனைத்தும் இந்தச் சாதனத்திலேயே இருக்கும்.",
      disclaimer: "இவை சிந்தனைக்காகத் தொகுக்கப்பட்ட பார்வைகள்—தெய்வீக அதிகாரமோ, மருத்துவ ஆலோசனையோ, அவசர உதவியோ அல்ல.",
      unknown: "இந்தக் கேள்விக்கு சரிபார்க்கப்பட்ட பதில் இன்னும் இல்லை. அறிவுத் தொகுப்பை பின்னர் விரிவாக்குவதற்காக இந்தத் தலைப்பு இந்தச் சாதனத்தில் மட்டும் சேமிக்கப்பட்டுள்ளது.",
      tryTopics: "சுயம், துன்பம், கடவுள், தியானம், கர்மா, மரணம், வாழ்க்கை நோக்கம், பிரார்த்தனை, மன்னிப்பு அல்லது மன அமைதி பற்றிக் கேளுங்கள்.",
      sources: "மேலும் அறிய மூலங்கள்", reflection: "சிந்திக்க", common: "பொதுமையும் வேறுபாடுகளும்",
      clearConfirm: "இந்த உரையாடலை அழிக்கவா?"
    }
  };

  const stopWords = new Set("a an and are as at be can do does for from how i in is it me my of on or should the to what when where which who why with you your பற்றி என்ன எப்படி ஏன் ஒரு இது என நான் நாம் என் இல் உம் ஆக உள்ளது வேண்டும்".split(/\s+/));
  const els = {
    form: document.querySelector("#chat-form"), question: document.querySelector("#question"),
    messages: document.querySelector("#messages"), send: document.querySelector("#send"),
    language: document.querySelector("#language"), clear: document.querySelector("#clear"), intro: document.querySelector("#intro")
  };
  const kb = Array.isArray(window.MANY_PATHS_KB) ? window.MANY_PATHS_KB : [];
  let language = localStorage.getItem("many-paths-language") || "en";
  let history = readJson("many-paths-history", []).slice(-12);

  function readJson(key, fallback) {
    try { const value = JSON.parse(localStorage.getItem(key) || "null"); return value ?? fallback; }
    catch { return fallback; }
  }
  function t(key) { return translations[language]?.[key] || translations.en[key] || key; }
  function normalize(value) {
    return String(value || "").normalize("NFKD").toLowerCase().replace(/[^\p{L}\p{N}\s]/gu, " ").replace(/\s+/g, " ").trim();
  }
  function tokens(value) { return [...new Set(normalize(value).split(" ").filter((word) => word.length > 1 && !stopWords.has(word)))]; }

  function findAnswer(query) {
    const normalized = normalize(query);
    const queryTokens = tokens(query);
    const ranked = kb.map((entry) => {
      const title = normalize(`${entry.title.en} ${entry.title.ta}`);
      const questions = normalize([...(entry.questions.en || []), ...(entry.questions.ta || [])].join(" "));
      const keywords = (entry.keywords || []).map(normalize);
      let score = 0;
      if ((entry.questions.en || []).concat(entry.questions.ta || []).some((q) => normalize(q) === normalized)) score += 100;
      for (const token of queryTokens) {
        if (keywords.includes(token)) score += 8;
        else if (keywords.some((keyword) => keyword.includes(token) || token.includes(keyword))) score += 4;
        if (title.includes(token)) score += 5;
        if (questions.includes(token)) score += 3;
      }
      if (normalized.length > 5 && (questions.includes(normalized) || title.includes(normalized))) score += 10;
      return { entry, score };
    }).sort((a, b) => b.score - a.score);
    return ranked[0]?.score >= 6 ? ranked[0].entry : null;
  }

  function formatAnswer(entry) {
    const lines = [entry.summary[language] || entry.summary.en, ""];
    for (const view of entry.perspectives) {
      lines.push(`${view.tradition[language] || view.tradition.en}: ${view.text[language] || view.text.en}`, "");
    }
    lines.push(`${t("common")}: ${entry.common[language] || entry.common.en}`, "");
    if (entry.sources?.length) lines.push(`${t("sources")}: ${entry.sources.join("; ")}`, "");
    lines.push(`${t("reflection")}: ${entry.reflection[language] || entry.reflection.en}`);
    return lines.join("\n").trim();
  }

  function saveHistory() { localStorage.setItem("many-paths-history", JSON.stringify(history.slice(-12))); }
  function recordUnanswered(question) {
    const items = readJson("many-paths-unanswered", []);
    if (!items.some((item) => normalize(item.question) === normalize(question))) {
      items.push({ question, language, date: new Date().toISOString().slice(0, 10) });
      localStorage.setItem("many-paths-unanswered", JSON.stringify(items.slice(-100)));
    }
  }
  function addMessage(role, text, className = "") {
    const node = document.createElement("div");
    node.className = `message ${role} ${className}`.trim(); node.textContent = text;
    els.messages.appendChild(node); els.messages.classList.add("has-messages");
    els.messages.scrollTop = els.messages.scrollHeight; return node;
  }
  function renderHistory() {
    els.messages.replaceChildren(); history.forEach((item) => addMessage(item.role, item.content));
    els.intro.hidden = history.length > 0;
  }
  function applyLanguage(nextLanguage) {
    language = translations[nextLanguage] ? nextLanguage : "en"; document.documentElement.lang = language;
    els.language.value = language; localStorage.setItem("many-paths-language", language);
    document.querySelectorAll("[data-i18n]").forEach((node) => { node.textContent = t(node.dataset.i18n); });
    document.querySelectorAll("[data-i18n-placeholder]").forEach((node) => { node.placeholder = t(node.dataset.i18nPlaceholder); });
    document.querySelectorAll(".suggestion").forEach((button) => { button.textContent = button.dataset[`question${language === "ta" ? "Ta" : "En"}`]; });
  }
  function resizeComposer() { els.question.style.height = "auto"; els.question.style.height = `${Math.min(els.question.scrollHeight, 180)}px`; }
  function submitQuestion(question) {
    history.push({ role: "user", content: question }); addMessage("user", question); els.intro.hidden = true;
    const entry = findAnswer(question);
    const answer = entry ? formatAnswer(entry) : `${t("unknown")}\n\n${t("tryTopics")}`;
    if (!entry) recordUnanswered(question);
    history.push({ role: "assistant", content: answer }); saveHistory(); addMessage("assistant", answer, entry ? "" : "error");
    els.question.focus();
  }

  els.form.addEventListener("submit", (event) => {
    event.preventDefault(); const question = els.question.value.trim(); if (!question) return;
    els.question.value = ""; resizeComposer(); submitQuestion(question);
  });
  els.question.addEventListener("input", resizeComposer);
  els.question.addEventListener("keydown", (event) => { if (event.key === "Enter" && !event.shiftKey) { event.preventDefault(); els.form.requestSubmit(); } });
  els.language.addEventListener("change", () => applyLanguage(els.language.value));
  els.clear.addEventListener("click", () => {
    if (history.length && !window.confirm(t("clearConfirm"))) return;
    history = []; localStorage.removeItem("many-paths-history"); els.messages.replaceChildren();
    els.messages.classList.remove("has-messages"); els.intro.hidden = false;
  });
  document.querySelectorAll(".suggestion").forEach((button) => button.addEventListener("click", () => {
    els.question.value = button.dataset[`question${language === "ta" ? "Ta" : "En"}`]; resizeComposer(); els.question.focus();
  }));

  applyLanguage(language); renderHistory(); resizeComposer();
  if ("serviceWorker" in navigator) window.addEventListener("load", () => navigator.serviceWorker.register("./sw.js").catch(() => {}));
})();
