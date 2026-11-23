# Submission Guidelines & Checklist for Task 5
**FOSSEE eSim Winter Internship - 2026 / Semester Long Internship (Autumn 2026)**  
**Screening Task 5: Tool Manager (CSE and related fields)**  

Follow these exact steps to complete and submit your screening task.

---

## Step 1: Initialize Git and Commit All Files

Run the following commands in your project terminal:

```bash
# 1. Initialize git repository (if not already done)
git init

# 2. Add all project files
git add .

# 3. Create initial commit
git commit -m "feat: complete eSim Automated Tool Manager for Task 5 screening submission"
```

---

## Step 2: Create a Private GitHub Repository

1. Go to [GitHub](https://github.com) and create a **new repository**.
2. **Repository Name:** e.g., `esim-automated-tool-manager` or `esim-task-5-tool-manager`
3. **Visibility:** Select **Private** *(Mandatory Requirement)*.
4. Do NOT initialize with a README, .gitignore, or license (these already exist in your local workspace).
5. Push your local repository to GitHub:
   ```bash
   git branch -M main
   git remote add origin https://github.com/<YOUR_GITHUB_USERNAME>/<YOUR_REPOSITORY_NAME>.git
   git push -u origin main
   ```

---

## Step 3: Grant Access to the Evaluator

Per the screening task instructions, you **MUST** grant read/collaborator access to the official FOSSEE evaluator:

1. In your GitHub repository, click on **Settings** (top navigation tab).
2. On the left sidebar under "Access", click **Collaborators**.
3. Click the green button **Add people**.
4. Search for: `Eyantra698Sumanto` (or URL: `https://github.com/Eyantra698Sumanto`).
5. Click **Add Eyantra698Sumanto to this repository**.

---

## Step 4: Send the Submission Email

Send an email to the FOSSEE eSim team with the exact details below:

* **To:** `contact-esim@fossee.in`
* **Subject:** `eSim Semester Long Internship - Autumn 2026 Submission Task 5`
* **Email Body Template:**

```text
Dear eSim Internship Evaluation Team / FOSSEE Team,

I am submitting my solution for Task 5: Tool Manager (CSE and related fields) for the eSim Semester Long Internship - Autumn 2026 / Winter Internship 2026.

Submission Details:
- Candidate Name: [Your Full Name]
- Email: [Your Email Address]
- Selected Task: Task 5 - Tool Manager (CSE and related fields)
- Private GitHub Repository Link: https://github.com/[YOUR_GITHUB_USERNAME]/[YOUR_REPOSITORY_NAME]
- Collaborator Access: Granted to https://github.com/Eyantra698Sumanto

Deliverables Included in Repository:
1. Detailed Architectural Design Document: DESIGN_DOCUMENT.md
2. Full Modular Code Implementation:
   - Tool Installation Engine (Package managers + Direct portable downloads)
   - Update & Upgrade System (Upstream version checking, pre-update backup, automated rollback)
   - Configuration Handling (Environment variables, PATH resolution, .esimrc, config.ini, .bat and .sh profile generation)
   - Dependency Checker / "eSim Doctor" (System health check, version parsing, Python scientific stack verification)
   - Dual User Interface (Rich formatted CLI + Modern dark-themed GUI using Tkinter/TTK)
   - Structured Action Logging (esim_tool_manager.log and esim_actions.jsonl)
3. Step-by-Step Execution Instructions & Quickstart: README.md
4. Complete Automated Test Suite: tests/ (17 tests, 100% passing)
5. Presentation & Video Demo Script: PRESENTATION_OUTLINE.md

Please let me know if any additional details are required.

Thank you and best regards,
[Your Full Name]
[Your Contact Number]
[Your College / Institute Name]
```

---

## Step 5: Fill Out the Google Form

Fill out the official Google Form provided in the instructions:
* **Form Link:** [Google Form Link](https://docs.google.com/forms/d/e/1FAIpQLSdFJCq7eOZjMSvq8kJN9ZtwNuQ0kM5D3gXOplQRYsduss5WMQ/viewform?usp=publish-editor)
* Paste your private GitHub repository URL and submission details in the relevant fields.
