# Vibe-Coding for Medievalists

**How to use LLMs to safely and reliably accelerate your research workflows**

A two-hour hands-on workshop at *Ars Inquirendi 2026* (Oxford and online, November 2026).

Led by Dr Sebastian Dows-Miller (UCL).

This repository contains everything we need for the session. **Please complete the setup below before you arrive.** It is designed for medievalists with any level of coding experience, including complete beginners, so don't worry if some of it is unfamiliar. If you get stuck on any step, ask an LLM to talk you through it (good practice for our session!).

---

## About the session

"Vibe-coding" means directing a large language model to write, run, and improve code through natural-language instruction, rather than programming by hand. In this workshop we will cover:

- When vibe-coded tools can be trusted, especially where the output can be verified
- How to vibe-code effectively: prompt design, planning phases, iterative improvement, and choosing your tools and packages in advance
- How to vibe-code safely: version control, using GitHub, and staying aware of what the model is changing

We will put these principles into practice by building a simple Python-based TEI encoder that runs in your web browser.

---

## Before the session

Please complete the following steps in order.

### 1. Create a GitHub account

If you don't already have one, create a free account at [github.com/signup](https://github.com/signup). You will need it for GitHub Desktop and for GitHub Copilot.

### 2. Install the software

You will need a laptop on which you have permission to install software.

| Software | Notes |
|---|---|
| [Python](https://www.python.org/downloads/) | Version 3.11 or newer. **On Windows, tick "Add python.exe to PATH" on the first screen of the installer.** |
| [GitHub Desktop](https://desktop.github.com/download/) | After installing, sign in with your GitHub account. |
| [VS Code](https://code.visualstudio.com/download) | Please install the latest version. This is the code editor we will use. |

Once VS Code is installed, open it and install the **Python** extension (from the Extensions panel, the icon on the left-hand side that looks like four squares). You will also need the **GitHub Copilot** extension if it is not already built into your version of VS Code. Then sign in to GitHub from VS Code when prompted (or via the Accounts icon at the bottom of the left-hand sidebar).

### 3. Get access to GitHub Copilot

GitHub Copilot is the AI coding assistant we will use inside VS Code. It can write and edit code in your project on your instructions.

- **Participants with institutional affiliation** can apply for free Copilot Pro through [GitHub Education](https://github.com/education). Approval can take several days, so **please apply at least a week before the session**.
- **If you are not eligible, or your application is not approved in time,** the free Copilot tier is enough to follow along.

### 4. Clone the session repository

"Cloning" means making a copy of this repository on your own computer. In GitHub Desktop:

1. Choose **File > Clone repository**
2. Select the **URL** tab
3. Enter `https://github.com/dowsmiller/vibecoding` (or `dowsmiller/vibecoding` under the **GitHub.com** tab)
4. Choose a location on your computer that you will remember, then click **Clone**

### 5. Check your setup
 
Open the cloned repository in VS Code (in GitHub Desktop: **Repository > Open in Visual Studio Code**, or in VS Code: **File > Open Folder**). Then open the built-in terminal (**Terminal > New Terminal**) and run a quick check that Python is installed:
 
- Windows: `python --version`
- macOS / Linux: `python3 --version`
You should see `Python 3.11` or higher.
 
Finally, open the Copilot chat panel in VS Code and send it a short message (such as "hello") to confirm you are signed in and it responds.
 
If either check fails, paste the error message into an LLM and ask for help, or contact me before the session.
 
---

## Just before the session

I may add materials to this repository shortly before the session. On the day (or the evening before), open GitHub Desktop, select this repository, and click **Fetch origin**, then **Pull origin** if it is offered, to make sure you have the latest version.

---

## Troubleshooting

- **`python` is not recognised (Windows):** Python was probably installed without "Add python.exe to PATH". Re-run the installer, choose **Modify** or **Repair**, and make sure that option is ticked. Then close and reopen VS Code.
- **`python3` not found (macOS):** Install Python from the link above, then reopen the terminal.
- **Copilot application still pending:** Use the free Copilot tier for the session.
- **Anything else:** Ask an LLM, or contact me at `s.dows-miller@ucl.ac.uk`.

---

## Contact

Sebastian Dows-Miller, University College London: `s.dows-miller@ucl.ac.uk`