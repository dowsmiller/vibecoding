"use strict";

const columnGrid = document.querySelector("#column-grid");
const columnTemplate = document.querySelector("#column-template");
const lineTemplate = document.querySelector("#line-template");
const saveStatus = document.querySelector("#save-status");

let editVersion = 0;
let saveInProgress = false;
let saveAgain = false;
let saveTimer = null;
let hasUnsavedChanges = false;

function columnLabel(index) {
  let label = "";
  while (index >= 0) {
    label = String.fromCharCode(97 + (index % 26)) + label;
    index = Math.floor(index / 26) - 1;
  }
  return label;
}

function getColumns() {
  return Array.from(columnGrid.children).filter((element) =>
    element.classList.contains("column"),
  );
}

function readColumns() {
  return getColumns().map((column) =>
    Array.from(column.querySelectorAll(".line input"), (input) => input.value),
  );
}

function showStatus(message, state) {
  saveStatus.textContent = message;
  saveStatus.dataset.state = state;
}

function scheduleSave(delay = 1000) {
  editVersion += 1;
  hasUnsavedChanges = true;
  if (delay === 0) {
    showStatus("Structural change. Saving now...", "pending");
  } else {
    showStatus("Unsaved changes. Saving in about one second...", "pending");
  }
  window.clearTimeout(saveTimer);
  saveTimer = window.setTimeout(() => {
    void saveChanges();
  }, delay);
}

function updateColumnLabels() {
  const columns = getColumns();
  columns.forEach((column, columnIndex) => {
    const label = columnLabel(columnIndex);
    const heading = column.querySelector("h2");
    heading.id = `column-heading-${columnIndex + 1}`;
    heading.textContent = `Column ${label}`;
    column.setAttribute("aria-labelledby", heading.id);
    column.dataset.columnIndex = String(columnIndex);

    const removeColumnButton = column.querySelector('[data-action="remove-column"]');
    removeColumnButton.disabled = columns.length === 1;
    removeColumnButton.setAttribute(
      "aria-label",
      `Remove column ${label}`,
    );

    const lines = Array.from(column.querySelectorAll(".line"));
    lines.forEach((line, lineIndex) => {
      const number = lineIndex + 1;
      const input = line.querySelector("input");
      const lineLabel = line.querySelector("label");
      const removeLineButton = line.querySelector('[data-action="remove-line"]');
      const inputId = `line-${columnIndex}-${number}`;

      line.dataset.lineIndex = String(lineIndex);
      lineLabel.htmlFor = inputId;
      lineLabel.textContent = String(number);
      lineLabel.setAttribute("aria-label", `Line ${number} in column ${label}`);
      input.id = inputId;
      input.name = inputId;
      removeLineButton.disabled = lines.length === 1;
      removeLineButton.setAttribute(
        "aria-label",
        `Remove line ${number} from column ${label}`,
      );
    });
  });
}

function appendLine(column, value = "") {
  const line = lineTemplate.content.firstElementChild.cloneNode(true);
  line.querySelector("input").value = value;
  column.querySelector(".lines").append(line);
}

function addColumn() {
  const column = columnTemplate.content.firstElementChild.cloneNode(true);
  for (let number = 0; number < 30; number += 1) {
    appendLine(column);
  }
  columnGrid.append(column);
  updateColumnLabels();
  column.querySelector("input").focus();
  scheduleSave(0);
}

async function saveChanges() {
  if (saveInProgress) {
    saveAgain = true;
    return;
  }

  saveInProgress = true;
  const versionBeingSaved = editVersion;
  const columns = readColumns();
  showStatus("Saving...", "saving");

  try {
    const response = await fetch("/save", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ columns }),
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
      `Save failed: ${error.message} Your text remains in the boxes. Try again.`,
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

columnGrid.addEventListener("input", (event) => {
  if (event.target.matches(".line input")) {
    scheduleSave();
  }
});

columnGrid.addEventListener("click", (event) => {
  const button = event.target.closest("button[data-action]");
  if (!button || button.disabled) {
    return;
  }

  const column = button.closest(".column");
  if (button.dataset.action === "add-line") {
    appendLine(column);
    updateColumnLabels();
    column.querySelector(".lines").lastElementChild.querySelector("input").focus();
    scheduleSave(0);
    return;
  }

  if (button.dataset.action === "remove-line") {
    const line = button.closest(".line");
    const input = line.querySelector("input");
    const lineNumber = Number(line.dataset.lineIndex) + 1;
    const columnName = columnLabel(Number(column.dataset.columnIndex));
    if (
      input.value.trim() !== "" &&
      !window.confirm(
        `Remove line ${lineNumber} in column ${columnName}? It contains text.`,
      )
    ) {
      return;
    }

    line.remove();
    updateColumnLabels();
    scheduleSave(0);
    return;
  }

  if (button.dataset.action === "remove-column") {
    const columns = getColumns();
    if (columns.length === 1) {
      return;
    }

    const columnName = columnLabel(Number(column.dataset.columnIndex));
    const containsText = Array.from(
      column.querySelectorAll(".line input"),
      (input) => input.value.trim() !== "",
    ).some(Boolean);
    if (
      containsText &&
      !window.confirm(`Remove column ${columnName}? It contains text.`)
    ) {
      return;
    }

    column.remove();
    updateColumnLabels();
    scheduleSave(0);
  }
});

document.querySelector("#add-column").addEventListener("click", addColumn);

window.addEventListener("beforeunload", (event) => {
  if (!hasUnsavedChanges) {
    return;
  }

  event.preventDefault();
  event.returnValue = "";
});

updateColumnLabels();
