/* ==========================================================
   Waveform — front-end only.
   Everywhere marked "WIRE BACKEND" is where this should call
   your actual API (e.g. a FastAPI/Flask route that wraps
   run_pipeline() from main.py) instead of the mock data below.
   ========================================================== */

document.addEventListener("DOMContentLoaded", () => {

  /* ---------------- source tabs (URL / file) ---------------- */
  const intakeTabs = document.querySelectorAll(".intake-tab");
  const fieldGroups = {
    url: document.querySelector('[data-field="url"]'),
    file: document.querySelector('[data-field="file"]'),
  };

  intakeTabs.forEach(tab => {
    tab.addEventListener("click", () => {
      intakeTabs.forEach(t => { t.classList.remove("is-active"); t.setAttribute("aria-selected", "false"); });
      tab.classList.add("is-active");
      tab.setAttribute("aria-selected", "true");

      const source = tab.dataset.source;
      Object.entries(fieldGroups).forEach(([key, el]) => {
        el.classList.toggle("is-hidden", key !== source);
      });
    });
  });

  /* ---------------- file drop label ---------------- */
  const fileInput = document.getElementById("source-file");
  const fileLabel = document.getElementById("file-drop-label");
  fileInput.addEventListener("change", () => {
    fileLabel.textContent = fileInput.files.length
      ? fileInput.files[0].name
      : "Choose a file or drop it here";
  });

  /* ---------------- pipeline simulation ---------------- */
  const form = document.getElementById("intake-form");
  const processBtn = document.getElementById("process-btn");
  const processing = document.getElementById("processing");
  const stageItems = document.querySelectorAll("#stage-list li");
  const heroSection = document.getElementById("workspace");
  const dashboard = document.getElementById("dashboard");

  const STAGE_DURATIONS = [900, 1500, 1100, 1000, 800]; // ms per stage, purely cosmetic

  form.addEventListener("submit", (e) => {
    e.preventDefault();

    const activeSource = document.querySelector(".intake-tab.is-active").dataset.source;
    const urlVal = document.getElementById("source-url").value.trim();
    const fileVal = fileInput.files[0];

    if (activeSource === "url" && !urlVal) {
      document.getElementById("source-url").focus();
      return;
    }
    if (activeSource === "file" && !fileVal) {
      fileLabel.textContent = "Pick a file first";
      return;
    }

    const language = document.getElementById("language").value;

    form.hidden = true;
    processing.hidden = false;
    processBtn.disabled = true;

    runStages(0, () => {
      // WIRE BACKEND: replace runStages()/mockResult() with something like:
      //   const res = await fetch("/api/process", {
      //     method: "POST",
      //     body: buildFormData({ source: activeSource, urlVal, fileVal, language })
      //   });
      //   const result = await res.json();
      showDashboard(mockResult(activeSource === "url" ? urlVal : fileVal.name, language));
    });
  });

  function runStages(i, done) {
    if (i >= stageItems.length) { done(); return; }
    stageItems.forEach(li => li.classList.remove("is-active"));
    stageItems[i].classList.add("is-active");
    setTimeout(() => {
      stageItems[i].classList.remove("is-active");
      stageItems[i].classList.add("is-done");
      runStages(i + 1, done);
    }, STAGE_DURATIONS[i] || 900);
  }

  function showDashboard(result) {
    document.getElementById("doc-title").textContent = result.title;
    document.getElementById("doc-timecode").textContent = result.timecode;
    document.getElementById("summary-text").textContent = result.summary;

    fillList("actions-list", result.action_items, "ACTION");
    fillList("decisions-list", result.key_decisions, "DECISION");
    fillList("questions-list", result.open_questions, "OPEN");
    fillTranscript(result.transcript);

    heroSection.hidden = true;
    dashboard.hidden = false;
    dashboard.scrollIntoView({ behavior: "smooth", block: "start" });
  }

  function fillList(id, items, tagLabel) {
    const el = document.getElementById(id);
    el.innerHTML = "";
    items.forEach(text => {
      const li = document.createElement("li");
      li.innerHTML = `<span class="tag">${tagLabel}</span><span>${text}</span>`;
      el.appendChild(li);
    });
  }

  function fillTranscript(lines) {
    const el = document.getElementById("transcript-log");
    el.innerHTML = "";
    lines.forEach(line => {
      const div = document.createElement("div");
      div.className = "t-line";
      div.innerHTML = `
        <span class="t-time">${line.time}</span>
        <span class="t-text"><span class="t-speaker">${line.speaker}</span>${line.text}</span>`;
      el.appendChild(div);
    });
  }

  /* ---------------- dashboard tab switching ---------------- */
  const docTabs = document.querySelectorAll(".doc-tab");
  const docPanels = document.querySelectorAll(".doc-panel");
  docTabs.forEach(tab => {
    tab.addEventListener("click", () => {
      docTabs.forEach(t => { t.classList.remove("is-active"); t.setAttribute("aria-selected", "false"); });
      docPanels.forEach(p => p.classList.remove("is-active"));
      tab.classList.add("is-active");
      tab.setAttribute("aria-selected", "true");
      document.querySelector(`[data-panel="${tab.dataset.tab}"]`).classList.add("is-active");
    });
  });

  /* ---------------- new session reset ---------------- */
  function resetSession() {
    dashboard.hidden = true;
    heroSection.hidden = false;
    form.hidden = false;
    processing.hidden = true;
    processBtn.disabled = false;
    stageItems.forEach(li => li.classList.remove("is-active", "is-done"));
    document.getElementById("source-url").value = "";
    fileInput.value = "";
    fileLabel.textContent = "Choose a file or drop it here";
    heroSection.scrollIntoView({ behavior: "smooth", block: "start" });
  }
  document.getElementById("new-session-btn").addEventListener("click", resetSession);
  document.getElementById("nav-cta").addEventListener("click", () => {
    if (!dashboard.hidden) resetSession();
    else heroSection.scrollIntoView({ behavior: "smooth", block: "start" });
  });

  /* ---------------- mock chat (RAG stand-in) ---------------- */
  const chatForm = document.getElementById("chat-form");
  const chatInput = document.getElementById("chat-input");
  const chatLog = document.getElementById("chat-log");

  chatForm.addEventListener("submit", (e) => {
    e.preventDefault();
    const question = chatInput.value.trim();
    if (!question) return;

    appendChat("user", question);
    chatInput.value = "";

    // WIRE BACKEND: replace with
    //   const res = await fetch("/api/chat", { method: "POST", body: JSON.stringify({ question }) });
    //   const { answer } = await res.json();
    setTimeout(() => {
      appendChat("bot", mockAnswer(question));
    }, 500);
  });

  function appendChat(who, text) {
    const div = document.createElement("div");
    div.className = `chat-msg chat-msg-${who}`;
    const p = document.createElement("p");
    p.textContent = text;
    div.appendChild(p);
    chatLog.appendChild(div);
    chatLog.scrollTop = chatLog.scrollHeight;
  }

  function mockAnswer(q) {
    const lower = q.toLowerCase();
    if (lower.includes("date") || lower.includes("launch")) {
      return "The transcript points to the second week of next month as the target — flagged as tentative pending QA sign-off.";
    }
    if (lower.includes("who") || lower.includes("owner")) {
      return "Ownership wasn't stated explicitly for that point in the transcript — worth confirming with the team.";
    }
    return "Based on the transcript, that wasn't discussed directly — try asking about the summary, decisions, or action items instead.";
  }

  /* ---------------- mock pipeline output ---------------- */
  function mockResult(sourceName, language) {
    const isHinglish = language === "hinglish";
    return {
      title: "Q3 Roadmap Sync — Product & Eng",
      timecode: "00:00:00 — 00:41:12",
      summary: isHinglish
        ? "Team ne Q3 roadmap discuss kiya, priorities align ki, aur launch timeline pe tentative agreement bana — lekin QA sign-off abhi pending hai."
        : "The team walked through the Q3 roadmap, aligned on priorities between product and engineering, and reached a tentative agreement on the launch window pending QA sign-off.",
      action_items: [
        "Confirm QA sign-off timeline with the testing lead by Friday.",
        "Share the updated roadmap doc with design for review.",
        "Follow up on the open API rate-limit question with infra.",
      ],
      key_decisions: [
        "Launch window set for the second week of next month, tentative.",
        "Feature scope trimmed to the three P0 items discussed.",
        "Weekly sync moved to Tuesdays going forward.",
      ],
      open_questions: [
        "Who owns the migration rollback plan if launch slips?",
        "Is the rate-limit increase confirmed with the infra team?",
        "Do we need a design review before the next sync?",
      ],
      transcript: [
        { time: "00:00:12", speaker: "Speaker 1:", text: `Source processed: ${sourceName}. Let's start with where we left off on the roadmap.` },
        { time: "00:02:41", speaker: "Speaker 2:", text: "Sure — priorities look mostly settled, but I want to flag the QA dependency before we lock the date." },
        { time: "00:07:03", speaker: "Speaker 1:", text: "Agreed. Let's treat the launch date as tentative until QA confirms." },
        { time: "00:14:52", speaker: "Speaker 3:", text: "On scope — I think we should trim it to the three P0 items and push the rest to next quarter." },
        { time: "00:22:18", speaker: "Speaker 2:", text: "That works. I'll also need someone to own the rollback plan in case the migration slips." },
        { time: "00:31:07", speaker: "Speaker 1:", text: "Let's move the weekly sync to Tuesdays so it doesn't clash with design review." },
      ],
    };
  }

});
