# ⚠️ Limitations

This demo version of {{ PROJECT_NAME_DISPLAY }} has several known limitations:

- Limited to **{{ MAX_DEMO_RUNS }}  runs/day** in demo mode due to Modal costs; technical users can self-host using the installation guide.
- No user accounts or per-user sessions — all users share the same app state, memory, and run quota.
- Shared memory resets automatically every  {{ MEM_EXP_DAYS }}  days.
- Only predefined categories can be selected.
- User can select up to {{MAX_CAT}} categories per run.
- Deal data comes exclusively from **DealNews RSS feeds**.
- No support for user history or notifications.
- Filtering thresholds are configurable in code but not adjustable via the UI.

These limitations will be addressed in future releases.
