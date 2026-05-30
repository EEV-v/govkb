import * as vscode from "vscode";
import { buildHomeModel, HomeAction, HomeModel } from "./homeState";

export type HomeActionHandler = (action: HomeAction) => void | Thenable<void>;

export class GovkbHomeWebviewProvider implements vscode.WebviewViewProvider {
  private view?: vscode.WebviewView;
  private model: HomeModel = buildHomeModel();

  constructor(private readonly onAction: HomeActionHandler) {}

  resolveWebviewView(webviewView: vscode.WebviewView): void {
    this.view = webviewView;
    webviewView.webview.options = {
      enableScripts: true
    };
    webviewView.webview.onDidReceiveMessage(async (message: { type?: string; index?: number }) => {
      if (message?.type !== "action" || typeof message.index !== "number") {
        return;
      }
      const action = allHomeActions(this.model)[message.index];
      if (action) {
        await this.onAction(action);
      }
    });
    this.render();
  }

  update(model: HomeModel): void {
    this.model = model;
    this.render();
  }

  private render(): void {
    if (!this.view) {
      return;
    }
    this.view.webview.html = renderHomeHtml(
      this.model,
      getNonce(),
      this.view.webview.cspSource
    );
  }
}

export function allHomeActions(model: HomeModel): HomeAction[] {
  return [
    model.primaryAction,
    ...model.sections.flatMap((section) => section.actions)
  ];
}

export function renderHomeHtml(model: HomeModel, nonce = "test-nonce", cspSource = ""): string {
  const actions = allHomeActions(model);
  const sectionHtml = model.sections
    .map(
      (section) => `
        <section class="section">
          <div class="section-heading">
            <h3>${escapeHtml(section.title)}</h3>
            <p>${escapeHtml(section.description)}</p>
          </div>
          <div class="action-row">
            ${section.actions.map((item) => renderButton(item, actions.indexOf(item), "secondary")).join("")}
          </div>
        </section>`
    )
    .join("");
  const csp = cspSource
    ? `<meta http-equiv="Content-Security-Policy" content="default-src 'none'; style-src ${cspSource} 'unsafe-inline'; script-src 'nonce-${nonce}';">`
    : "";

  return `<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  ${csp}
  <title>${escapeHtml(model.title)}</title>
  <style>
    :root {
      color-scheme: var(--vscode-color-scheme, light dark);
    }

    body {
      margin: 0;
      padding: 14px;
      color: var(--vscode-foreground);
      background: var(--vscode-sideBar-background);
      font: var(--vscode-font-size) var(--vscode-font-family);
    }

    .shell {
      display: flex;
      flex-direction: column;
      gap: 12px;
      min-width: 0;
    }

    .hero,
    .section {
      border: 1px solid var(--vscode-sideBarSectionHeader-border, var(--vscode-panel-border));
      border-radius: 6px;
      background: var(--vscode-editor-background);
    }

    .hero {
      padding: 14px;
    }

    h2,
    h3,
    p {
      margin: 0;
    }

    h2 {
      font-size: 16px;
      font-weight: 600;
      line-height: 1.35;
    }

    h3 {
      font-size: 13px;
      font-weight: 600;
      line-height: 1.35;
    }

    p,
    .badge-value,
    .button-note {
      color: var(--vscode-descriptionForeground);
      line-height: 1.35;
    }

    .subtitle {
      margin-top: 4px;
    }

    .primary-action {
      margin-top: 10px;
    }

    .badge-grid {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(112px, 1fr));
      gap: 6px;
      margin: 12px 0;
    }

    .badge {
      min-width: 0;
      padding: 7px 8px;
      border: 1px solid var(--vscode-panel-border);
      border-left: 3px solid var(--vscode-descriptionForeground);
      border-radius: 5px;
      background: var(--vscode-sideBar-background);
    }

    .badge[data-tone="success"] {
      border-left-color: var(--vscode-testing-iconPassed);
    }

    .badge[data-tone="warning"] {
      border-left-color: var(--vscode-testing-iconQueued);
    }

    .badge[data-tone="error"] {
      border-left-color: var(--vscode-testing-iconFailed);
    }

    .badge-label,
    .button-label {
      overflow-wrap: anywhere;
      font-weight: 600;
    }

    .badge-value {
      margin-top: 2px;
      overflow-wrap: anywhere;
      font-size: 12px;
    }

    .section {
      padding: 10px;
    }

    .section-heading {
      display: flex;
      flex-direction: column;
      gap: 3px;
      margin-bottom: 8px;
    }

    .action-row {
      display: flex;
      flex-wrap: wrap;
      gap: 7px;
    }

    button {
      display: inline-flex;
      align-items: center;
      gap: 6px;
      min-height: 30px;
      max-width: 100%;
      padding: 5px 9px;
      border: 1px solid var(--vscode-button-border, transparent);
      border-radius: 5px;
      color: var(--vscode-button-foreground);
      background: var(--vscode-button-background);
      font: inherit;
      text-align: left;
      cursor: pointer;
    }

    button:hover {
      background: var(--vscode-button-hoverBackground);
    }

    button.secondary {
      color: var(--vscode-button-secondaryForeground);
      background: var(--vscode-button-secondaryBackground);
    }

    button.secondary:hover {
      background: var(--vscode-button-secondaryHoverBackground);
    }

    .icon {
      flex: 0 0 16px;
      width: 16px;
      height: 16px;
      opacity: 0.9;
    }

    .icon svg {
      display: block;
      width: 16px;
      height: 16px;
      stroke: currentColor;
      fill: none;
      stroke-width: 1.8;
      stroke-linecap: round;
      stroke-linejoin: round;
    }

    .button-text {
      min-width: 0;
    }

    .button-note {
      display: block;
      margin-top: 1px;
      font-size: 11px;
      font-weight: 400;
    }

    .action-explanation {
      display: grid;
      grid-template-columns: 1fr;
      gap: 6px;
      margin-top: 10px;
    }

    .explanation-item {
      padding: 7px 8px;
      border-left: 3px solid var(--vscode-button-background);
      background: var(--vscode-sideBar-background);
    }

    .explanation-label {
      display: block;
      margin-bottom: 2px;
      color: var(--vscode-descriptionForeground);
      font-size: 11px;
      font-weight: 600;
      text-transform: uppercase;
    }
  </style>
</head>
<body>
  <main class="shell">
    <section class="hero">
      <h2>${escapeHtml(model.title)}</h2>
      <p class="subtitle">${escapeHtml(model.subtitle)}</p>
      <div class="primary-action">
        ${renderButton(model.primaryAction, 0, "primary")}
      </div>
      ${renderPrimaryExplanation(model.primaryAction)}
      <div class="badge-grid">
        ${model.badges
          .map(
            (badge) => `
              <div class="badge" data-tone="${escapeHtml(badge.tone)}">
                <div class="badge-label">${escapeHtml(badge.label)}</div>
                <div class="badge-value">${escapeHtml(badge.value)}</div>
              </div>`
          )
          .join("")}
      </div>
    </section>
    ${sectionHtml}
  </main>
  <script nonce="${nonce}">
    const vscode = acquireVsCodeApi();
    for (const button of document.querySelectorAll("button[data-action-index]")) {
      button.addEventListener("click", () => {
        vscode.postMessage({ type: "action", index: Number(button.dataset.actionIndex) });
      });
    }
  </script>
</body>
</html>`;
}

function renderPrimaryExplanation(action: HomeAction): string {
  if (!action.reason && !action.consequence) {
    return "";
  }
  return `
    <div class="action-explanation" aria-label="Primary action explanation">
      ${action.reason ? renderExplanationItem("Why", action.reason) : ""}
      ${action.consequence ? renderExplanationItem("Clicking it will", action.consequence) : ""}
    </div>`;
}

function renderExplanationItem(label: string, value: string): string {
  return `
    <div class="explanation-item">
      <span class="explanation-label">${escapeHtml(label)}</span>
      <p>${escapeHtml(value)}</p>
    </div>`;
}

function renderButton(action: HomeAction, index: number, tone: "primary" | "secondary"): string {
  const title = `${action.label}: ${action.description}`;
  return `
    <button class="${tone === "secondary" ? "secondary" : ""}" title="${escapeHtml(title)}" data-action-index="${index}" data-command="${escapeHtml(action.command)}">
      <span class="icon" aria-hidden="true">${inlineIcon(action.icon)}</span>
      <span class="button-text">
        <span class="button-label">${escapeHtml(action.label)}</span>
        <span class="button-note">${escapeHtml(action.description)}</span>
      </span>
    </button>`;
}

function inlineIcon(icon: string): string {
  const body = iconPaths[icon] ?? iconPaths.default;
  return `<svg viewBox="0 0 24 24" focusable="false">${body}</svg>`;
}

const iconPaths: Record<string, string> = {
  "cloud-upload": '<path d="M16 16l-4-4-4 4"/><path d="M12 12v8"/><path d="M20 17.5a4.5 4.5 0 0 0-2.4-8.3A6 6 0 0 0 6.4 8.1 5 5 0 0 0 5 18h2"/>',
  "debug-alt": '<path d="M8 7h8"/><path d="M9 3l1 4"/><path d="M15 3l-1 4"/><path d="M7 12h10"/><path d="M7 17h10"/><path d="M6 8v7a6 6 0 0 0 12 0V8"/>',
  diff: '<path d="M6 5h12"/><path d="M6 12h8"/><path d="M6 19h12"/><path d="M18 9v6"/><path d="M15 12h6"/>',
  edit: '<path d="M4 20h4l11-11-4-4L4 16v4z"/><path d="M13 7l4 4"/>',
  error: '<circle cx="12" cy="12" r="9"/><path d="M15 9l-6 6"/><path d="M9 9l6 6"/>',
  eye: '<path d="M2.5 12s3.5-6 9.5-6 9.5 6 9.5 6-3.5 6-9.5 6-9.5-6-9.5-6z"/><circle cx="12" cy="12" r="2.5"/>',
  "git-merge": '<path d="M7 4v10a4 4 0 0 0 4 4h6"/><circle cx="7" cy="4" r="2"/><circle cx="7" cy="20" r="2"/><circle cx="19" cy="18" r="2"/><path d="M7 14v4"/>',
  "git-pull-request-create": '<circle cx="6" cy="6" r="2"/><circle cx="6" cy="18" r="2"/><path d="M6 8v8"/><path d="M13 6h7"/><path d="M16.5 2.5V9.5"/>',
  "go-to-file": '<path d="M7 3h7l5 5v13H7z"/><path d="M14 3v5h5"/><path d="M10 15h7"/><path d="M14 11l3 4-3 4"/>',
  "list-tree": '<path d="M8 6h12"/><path d="M8 12h12"/><path d="M8 18h12"/><path d="M4 6h.01"/><path d="M4 12h.01"/><path d="M4 18h.01"/>',
  "new-folder": '<path d="M3 7h7l2 2h9v9a3 3 0 0 1-3 3H6a3 3 0 0 1-3-3z"/><path d="M12 15h6"/><path d="M15 12v6"/>',
  output: '<path d="M4 5h16v14H4z"/><path d="M7 9l3 3-3 3"/><path d="M12 16h5"/>',
  pass: '<circle cx="12" cy="12" r="9"/><path d="M8 12.5l2.5 2.5L16.5 9"/>',
  play: '<path d="M8 5v14l11-7z"/>',
  pulse: '<path d="M3 12h4l2-6 4 12 2-6h6"/>',
  "repo-commit": '<circle cx="12" cy="12" r="3"/><path d="M3 12h6"/><path d="M15 12h6"/>',
  refresh: '<path d="M20 12a8 8 0 0 1-13.7 5.7"/><path d="M4 12A8 8 0 0 1 17.7 6.3"/><path d="M17 3v4h-4"/><path d="M7 21v-4h4"/>',
  rocket: '<path d="M5 15c2-6 6-10 14-10 0 8-4 12-10 14l-4-4z"/><path d="M5 15l-2 6 6-2"/><circle cx="15" cy="9" r="1.5"/>',
  search: '<circle cx="10.5" cy="10.5" r="6.5"/><path d="M15.5 15.5L21 21"/>',
  trash: '<path d="M4 7h16"/><path d="M10 11v6"/><path d="M14 11v6"/><path d="M6 7l1 14h10l1-14"/><path d="M9 7V4h6v3"/>',
  default: '<circle cx="12" cy="12" r="8"/><path d="M12 8v5"/><path d="M12 16h.01"/>'
};

function escapeHtml(value: string): string {
  return value
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;");
}

function getNonce(): string {
  const chars = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789";
  let text = "";
  for (let index = 0; index < 32; index += 1) {
    text += chars.charAt(Math.floor(Math.random() * chars.length));
  }
  return text;
}
