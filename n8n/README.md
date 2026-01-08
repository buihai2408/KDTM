# n8n Automation Workflows

This folder contains pre-built n8n workflows for the Personal Finance BI System.

## Workflows

### 1. Monthly Bill Reminder (`workflows/monthly_bill_reminder.json`)

Sends monthly email reminders for upcoming bills.

**Trigger:** 
- Cron: 1st of each month at 8:00 AM (Asia/Ho_Chi_Minh)
- Manual: For testing

**Flow:**
1. Get current month (YYYY-MM format)
2. Fetch upcoming bills from Backend API
3. Group bills by user
4. Build HTML email with bill details
5. Send email via MailHog SMTP

**Email includes:**
- List of all bills for the month
- Bill name, category, due date
- Wallet and amount
- Total amount due

### 2. Budget Overrun Alert (`workflows/budget_overrun_alert.json`)

Sends daily alerts when spending exceeds budget.

**Trigger:**
- Cron: Daily at 9:00 AM (Asia/Ho_Chi_Minh)
- Manual: For testing

**Flow:**
1. Query PostgreSQL for budget overruns
2. Check if any overruns exist
3. Group overruns by user
4. Build HTML alert email
5. Send email via MailHog SMTP

**Email includes:**
- Categories where budget exceeded
- Budget amount vs actual spent
- Overrun amount and percentage
- Recommendations

## Required Credentials

Before using these workflows, create these credentials in n8n:

### MailHog SMTP
- Name: `MailHog SMTP`
- Host: `mailhog`
- Port: `1025`
- SSL: OFF

### Finance PostgreSQL
- Name: `Finance PostgreSQL`
- Host: `postgres`
- Port: `5432`
- Database: `finance_db`
- User: `n8n_readonly`
- Password: `n8n_pass`
- SSL: OFF

## Environment Variables

The workflows use these environment variables (set in docker-compose.yml):

| Variable | Description |
|----------|-------------|
| `N8N_SERVICE_KEY` | API authentication key for backend |
| `DB_POSTGRESDB_HOST` | PostgreSQL host |
| `DB_POSTGRESDB_DATABASE` | Database name |
| `N8N_SMTP_HOST` | SMTP host for emails |

## Testing

1. Import workflow in n8n UI
2. Connect credentials to nodes
3. Click "Execute Workflow" or use Manual Trigger
4. Check MailHog UI at http://localhost:8025 for emails

## Security Notes

- Workflows authenticate with backend using `N8N_SERVICE_KEY`
- PostgreSQL access uses read-only user `n8n_readonly`
- Credentials are stored securely in n8n, not in workflow JSON
