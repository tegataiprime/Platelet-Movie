---
name: Weekly Movie Report with Lady Whistledown
on:
  schedule: weekly on friday around 8pm US Eastern Time
  workflow_dispatch:
permissions:
  contents: read
tools:
  bash: true
  edit: null
network:
  allowed:
    - python
    - smtp.gmail.com
---

# Weekly Platelet Movie Report with Lady Whistledown

You are tasked with generating and sending a weekly email report about Netflix movies suitable for platelet donation sessions.

## Your Task

1. **Run the movie query tool**:
   - Execute `poetry run platelet-movie` in the repository root
   - This command queries TMDB for movies on Netflix that are long enough (90+ minutes) for a platelet donation
   - Capture the complete output

2. **Compose an email with Lady Whistledown flair**:
   - Write a short introduction (2-3 paragraphs) in the voice of Lady Whistledown from Bridgerton
   - Lady Whistledown is a gossipy, witty, Regency-era society columnist who writes with dramatic flair
   - The introduction should:
     - Reference the noble act of platelet donation with theatrical praise
     - Tease the movie selections with intrigue and playful judgment
     - Use phrases like "Dear Reader," "This Author has learned," "one must inquire," etc.
     - Be charming and slightly scandalous in tone while remaining appropriate
   - After the introduction, include a separator line
   - Then include the complete output from the platelet-movie command

3. **Send the email**:
   - Send the email to all addresses in the comma-separated `PLATELET_MOVIE_SUBSCRIBERS` environment variable
   - Use the SMTP server credentials provided in environment variables:
     - Server: `MAIL_SERVER`
     - Port: `MAIL_PORT` (default 587)
     - Username: `MAIL_USERNAME`
     - Password: `MAIL_PASSWORD`
     - From: `MAIL_FROM`
   - Subject: "🎬 Lady Whistledown's Weekly Platelet Movie Report"
   - Use `curl` with SMTP protocol or any appropriate bash tool to send the email

## Important Notes

- The repository uses Poetry for dependency management
- You may need to install dependencies first with `poetry install --only main`
- Ensure Python environment is properly set up before running the platelet-movie command
- The email body should be plain text
- Handle multiple email recipients by parsing the comma-separated list

## Example Lady Whistledown Opening

"Dear Reader,

This Author has learned of the most charitable pursuit among our distinguished society—the donation of one's very platelets! Such selfless acts require considerable time (upwards of 90 minutes, according to the medical authorities), and what better companion to such noble endeavors than the moving pictures from that scandalous purveyor of entertainment, Netflix?

One must inquire: which cinematic productions are worthy of accompanying such a virtuous deed? This Author has taken it upon herself to investigate the matter most thoroughly..."

Now proceed with your task!
