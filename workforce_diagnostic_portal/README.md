## Workforce Diagnostic Portal

This Django application provides a rule-based workforce readiness diagnostic workflow for evaluating job roles across multiple decision levels (Founders/Leadership, Execution, and HR).

### Audit & Decision Logging

The system now records key events in the `AuditLog` model:

- **User login activity**: Successful and failed login attempts (including role mismatches) with username, selected role, actual role, and IP address.
- **Diagnostic submissions**: Each new `DiagnosticSubmission` logs the decision, user level/role, computed risk level, and a derived readiness score.
- **Readiness / risk evaluation**: Risk is calculated per submission using the existing rule engine, and the resulting `risk_level` is captured in audit metadata.
- **Final decisions per job role**: When Level 1 users open the results page, an overall hiring recommendation is generated and logged, including overall risk and any conditions.

### Viewing Audit Logs

- **Django admin**: Go to the `Audit logs` section in the admin to search and filter events by user, event type, and date.
- **In-app page (admins only)**: Visit `/audit-logs/` (named URL `audit_logs`) to see the most recent audit events, with simple filters for event type and username.

