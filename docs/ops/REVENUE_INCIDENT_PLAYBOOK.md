# Revenue Incident Playbook

## Severity

- Sev-1: Any issue that blocks money or breaks paid fulfillment.
- Sev-2: Degraded but recoverable within normal support window.

## Sev-1 triggers

- Payment succeeds but no project/brief is created.
- Payment fails due to misconfiguration in production mode.
- Brief link is missing, invalid, or expired immediately.
- Handoff email is not delivered for paid customer.
- Ops dashboard status disagrees with Stripe event status.

## First 15 minutes

1. Open incident channel and pin customer IDs/order IDs.
2. Freeze new release and disable risky deploys.
3. Verify `/health` and stripe mode on production.
4. Reproduce using production-safe smoke flow.
5. Decide immediate mitigation: rollback, feature flag, or hotfix.

## Customer communication rule

- Send first acknowledgment within 15 minutes.
- Include current status, expected next update time, and fallback path.

## Kill switch options

- Disable checkout entry points if paid flow is unsafe.
- Route customers to contact flow with manual intake backup.
- Temporarily switch to manual handoff if email provider is degraded.

## Root cause checklist

- Stripe keys, webhook secret, and price IDs are correct.
- Render environment variables and app startup logs are clean.
- Resend key/domain and sender config are valid.
- Database write path for purchase -> project -> intake token is healthy.
- Any recent copy or route changes did not break status polling.

## Exit criteria for incident closure

- At least 3 successful prod-safe smoke loops in a row.
- No outstanding failed paid customers without recovery plan.
- Post-incident note published with timeline and prevention actions.

## Postmortem template

- Trigger:
- Impact window:
- Affected customers:
- Root cause:
- Detection gap:
- Corrective action:
- Preventive action:
- Owner + due date:
