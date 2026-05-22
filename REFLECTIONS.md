# Reflections

## 1. Multi-account

If `costctl` had to run across many AWS accounts, the main change would be authentication flow. Instead of using one local credential set, I would use STS assume-role and iterate through an account list. For my selected commands, `list` and `cost`, the output should include account IDs so the results can be aggregated later into one report. This would make the tool more useful for organization-wide visibility instead of only single-account inspection.

## 2. Cost visibility and tagging

The biggest limitation of the `cost` command is that it depends on tag quality. If resources are missing tags or if cost allocation tags are not activated in Billing, the command can return incomplete or zero results even when spending exists. Because of that, I see `list` and `cost` as connected: `list` helps inspect whether tagging is present, and `cost` turns that tagging into spending visibility. In practice, cost reporting is only as good as the tagging discipline behind it.

## 3. AI assistance

AI tools were useful for speeding up repetitive boto3 code and helping structure command logic, but they were not enough on their own. The reliable part of the work still came from reading the tests, checking the provided docstrings, and validating behavior against the CLI. I would trust AI for scaffolding and syntax patterns, but not for assumptions about AWS behavior without verification. For this lab, the value of AI was speed, not authority.

## 4. W7 carry-over

For W7, I would keep only `list` and `cost`. `list` is a strong base command because it gives a quick inventory view across EC2, RDS, S3, and EBS volumes. `cost` is also worth keeping because it supports reporting and can later be extended into multi-account summaries. I would not prioritize destructive commands in the next phase, because visibility and reporting are more important foundations before adding more automation.
