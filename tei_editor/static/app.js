"use strict";

const lineInputs = Array.from(document.querySelectorAll(".line input"));
const saveStatus = document.querySelector("#save-status");

let editVersion = 0;
let saveInProgress = false;
let saveAgain = false;
let saveTimer = null;
let hasUnsavedChanges = false;

function showStatus(message, state) {
  saveStatus.textContent = message;
  saveStatus.dataset.state = state;
}

function scheduleSave() {
  editVersion += 1;
  hasUnsavedChanges = true;
  showStatus("Unsaved changes. Saving in about one second...", "pending");
  window.clearTimeout(saveTimer);
  saveTimer = window.setTimeout(() => {
    void saveChanges();
  }, 1000);
}

async function saveChanges() {
  if (saveInProgress) {
    saveAgain = true;
    return;
  }

  saveInProgress = true;
  const versionBeingSaved = editVersion;
  const lines = lineInputs.map((input) => input.value);
  showStatus("Saving...", "saving");

  try {
    const response = await fetch("/save", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ lines }),
    });

    let result;
    try {
      result = await response.json();
    } catch {
      throw new Error("The server returned an unreadable response.");
    }

    if (!response.ok) {
      throw new Error(result.error || "The save did not complete.");
    }

    if (editVersion === versionBeingSaved) {
      hasUnsavedChanges = false;
      showStatus(`Saved at ${result.saved_at}`, "saved");
    } else {
      saveAgain = true;
      showStatus("Newer edits are waiting to be saved.", "pending");
    }
  } catch (error) {
    showStatus(
      `Save failed: ${error.message} Your text remains in the boxes. Try typing again to retry.`,
      "error",
    );
  } finally {
    saveInProgress = false;
    if (saveAgain || editVersion !== versionBeingSaved) {
      saveAgain = false;
      window.clearTimeout(saveTimer);
      saveTimer = window.setTimeout(() => {
        void saveChanges();
      }, 0);
    }
  }
}

for (const input of lineInputs) {
  input.addEventListener("input", scheduleSave);
}

window.addEventListener("beforeunload", (event) => {
  if (!hasUnsavedChanges) {
    return;
  }

  event.preventDefault();
  event.returnValue = "";
});
