# VoteWise2 User & Administrator Manual 🗳️

Welcome to the comprehensive guide for **VoteWise2**. This document serves as a complete reference for all users, covering everything from initial registration to advanced election management and troubleshooting.

---

## 📚 Table of Contents

1.  [**Voter Guide**](#-voter-guide)
    *   [Getting Started (Registration)](#1-getting-started)
    *   [Biometric Setup (Face ID)](#2-biometric-setup)
    *   [Voting Process](#3-voting-process)
    *   [Post-Election (Results & History)](#4-post-election)
    *   [Using the AI Assistant](#5-using-the-ai-assistant)
2.  [**Administrator Guide**](#-administrator-guide)
    *   [Dashboard Overview](#6-admin-dashboard)
    *   [Election Lifecycle Management](#7-election-lifecycle)
    *   [Candidate & Position Setup](#8-candidate--position-setup)
    *   [Voter Management & Verification](#9-voter-management)
    *   [Security & Monitoring](#10-security--monitoring)
    *   [Reporting & Analytics](#11-reporting--analytics)
3.  [**Troubleshooting & FAQ**](#-troubleshooting--faq)
    *   [Common Voter Issues](#common-voter-issues)
    *   [Common Admin Issues](#common-admin-issues)
    *   [Error Message Reference](#error-message-reference)

---

## 👤 Voter Guide

### 1. Getting Started
To ensure the integrity of the election, every voter must have a verified account.

*   **Step 1: Registration**
    *   Navigate to the **Register** page.
    *   Enter your **University Email**, **Student ID**, and create a strong Password.
    *   Select your **Course**, **Year Level**, and **Section**. Accuracy is crucial as these details may determine which elections you can vote in.
*   **Step 2: Verification**
    *   After signing up, your status will be **"Pending Verification"**.
    *   You cannot log in until an administrator approves your account.
    *   *Check your email* for a welcome notification once approved.

### 2. Biometric Setup
VoteWise2 uses Face Recognition to prevent voter fraud.
*   **Enrolling Your Face**:
    1.  Log in with your username and password.
    2.  Go to **Profile** > **Enroll Face**.
    3.  Grant camera permissions to your browser.
    4.  Position your face in the center of the frame. Ensure good lighting and remove masks/glasses.
    5.  The system will verify your face quality and save your biometric signature.
    > **Note:** Your actual face image is converted into a secure mathematical "embedding" (a long string of numbers). The original photo is not used for matching, ensuring privacy.

### 3. Voting Process
When an election is **Active**, follow these steps:

1.  **Dashboard Access**: Your dashboard will show an "Active Election" card. Click **Vote Now**.
2.  **Select Candidates**:
    *   Ballots are organized by **Position** (e.g., President, Senator).
    *   **Partylist Voting**: You can click a Partylist name to automatically select all candidates from that party.
    *   *Limitation Checks*: The system will prevent you from selecting more candidates than allowed (e.g., selecting 13 Senators when only 12 are allowed).
3.  **Submit Ballot**:
    *   Review your choices on the summary screen.
    *   Click **Submit Vote**.
    *   **Security Check**: You may be prompted to enter your Password or scan your Face to confirm it's really you.
4.  **Confirmation**:
    *   You will receive a **Digital Receipt** with a unique **Ballot ID**.
    *   **Save this ID!** You can use it later to verify your vote was counted.

### 4. Post-Election
*   **Results**: Once the election ends, visit the **Results** tab to view real-time graphs and winners.
*   **My History**: View a log of every election you participated in.

### 5. Using the AI Assistant
The built-in **Chatbot** (bottom-right corner) is powered by Google Gemini.
*   **Example Queries**:
    *   "Who is running for President?"
    *   "What is the platform of Candidate X?"
    *   "How do I change my password?"
    *   "When does the election end?"

---

## 🛡️ Administrator Guide

### 6. Admin Dashboard
The command center for election oversight.
*   **Live Metrics**: See `Total Voters`, `Votes Cast`, and `Turnout %` in real-time.
*   **Health Status**: Green checks indicate all systems (Database, Logging, Biometrics) are operational.
*   **Timeline**: See upcoming election events.

### 7. Election Lifecycle
Manage the flow of an election from creation to closure.
*   **Drafting**: Create a new election. Set `Start Date` and `End Date`.
*   **Activation**:
    *   Go to elections list and toggle status to **Active**.
    *   **CRITICAL**: Activating an election **LOCKS** all voter profiles. Students cannot change their Course/Year Level while an election is running to prevent constituency hopping.
*   **Closing**:
    *   The system automatically ends the election at the `End Date`.
    *   You can manually **Pause** or **End** an election early if necessary.

### 8. Candidate & Position Setup
*   **Positions**: Create positions with `Order` (appearance on ballot) and `Max Winners`.
    *   *Example*: "Senator", Max Winners: 12.
*   **Candidates**:
    *   Link a student profile to a Position.
    *   **Upload Photo**: Candidates without photos will appear with a placeholder.
    *   **Platform**: Add a rich-text bio for the "Know Your Candidate" feature.

### 9. Voter Management
*   **Verification Queue**:
    *   Go to **Voters** > **Pending**.
    *   Review details against school records.
    *   **Approve** or **Reject** with a reason.
*   **Bulk Actions**: You can upload a CSV of valid Student IDs to auto-approve matching registrations.

### 10. Security & Monitoring
*   **Audit Logs**: View the **Audit Log** page for a tamper-evident record of all actions.
    *   *Filter by*: `SECURITY`, `VOTE`, `ADMIN`, `AUTH`.
*   **Anomaly Detection**: The dashboard alerts you to:
    *   **Spikes**: >50 votes in 1 hour.
    *   **Ties**: Candidates with identical vote counts.
    *   **Low Turnout**: <10% participation.

### 11. Reporting & Analytics
*   **PDF Reports**: Generate official "Certificate of Canvass" style reports.
    *   *Includes*: Winner certification, vote breakdown, and AI-generated analysis of the results.
*   **Data Export**: Download raw CSV results for external auditing.

---

## 🔧 Troubleshooting & FAQ

### Common Voter Issues

#### 1. "You must have a student profile to vote."
*   **Cause**: You logged in with a generic user account that isn't linked to a student record.
*   **Fix**: Contact an admin to link your user account to a Student Profile.

#### 2. "Your account is not properly configured." / "Not verified"
*   **Cause**: You registered but an admin hasn't approved you yet.
*   **Fix**: Wait for the approval email. If it's been >24 hours, visit the Student Affairs office.

#### 3. Face Verification Failed ("Liveness Check Failed")
*   **Cause**: Poor lighting, wearing a mask, or holding the camera too close/far.
*   **Fix**:
    *   Find a well-lit room.
    *   Remove glasses/masks.
    *   Hold the device at eye level.
    *   **Workaround**: If biometric hardware is broken, ask an Admin to enable "Password-Only Mode" for your account temporarily.

#### 4. "You can only select N candidate(s)"
*   **Cause**: You tried to vote for 13 Senators when the limit is 12.
*   **Fix**: Deselect one candidate before selecting another.

### Common Admin Issues

#### 1. Cannot Edit Voter Details
*   **Error**: "Student information cannot be modified during an active election."
*   **Cause**: **Profile Locking** security feature is active.
*   **Fix**: You must wait until the election ends to update student courses/sections. This prevents gerrymandering during voting.

#### 2. "Low Turnout Alert"
*   **Cause**: Participation is under 10%.
*   **Fix**: Use the **"Send Global Reminder"** feature in the Email Center to notify all students who haven't voted yet.

#### 3. Reports are Empty or Missing Data
*   **Cause**: You might be generating a report for a "Draft" election or one with no votes.
*   **Fix**: Ensure the election ID is correct and that `VoterReceipt` records exist.

### Error Message Reference

| Error Code/Message | Likely Cause | Solution |
| :--- | :--- | :--- |
| `CSRF Verification Failed` | Browser cookies are blocked or session expired. | Refresh the page and try again. Enable cookies. |
| `IntegrityError` | Trying to create a duplicate record (e.g., same Student ID). | Check if the student is already registered. |
| `SMTPAuthenticationError` | System cannot send emails. | (Admin) Check `.env` email credentials. |
| `Face Not Found` | No face detected in the webcam frame. | Clean camera lens and improve lighting. |

---

*VoteWise2 Manual v2.1 - Updated Dec 8, 2025*
