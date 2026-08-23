# Docs

This folder holds submission-related notes and references (Round 1 deck
content lives outside this repo as a PDF/PPT).

## References used for the problem statement

- RBI notification on increasing instances of payment frauds:
  https://www.rbi.org.in/commonman/english/scripts/Notification.aspx?Id=3221
- LexisNexis Risk Solutions — industry reports on account-takeover fraud trends:
  https://risk.lexisnexis.com/global/en/insights-resources/article/account-takeover-fraud
- Datos Insights — explainable AI vs. black-box models in fraud detection:
  https://datos-insights.com/blog/interpreting-the-black-box-why-explainable-ai-is-critical-for-fraud-detection/

## Design decision log

- **Rules + anomaly scoring over deep learning**: chosen for explainability
  and auditability, which matter more in a banking fraud context
  (regulatory transparency, analyst trust) than marginal accuracy gains.
- **Mock SIM-change feed**: live telecom SIM-swap APIs aren't publicly
  accessible for prototyping, so a simulated SIM-change event feed is
  used, designed to mirror real-world SIM-swap notification patterns.
