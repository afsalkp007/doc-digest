"""Curated enterprise document presets for Map-Reduce summarization demonstration."""

PRESET_DOCUMENTS = {
    "Cloud Infrastructure Outage Postmortem (SEV-1)": {
        "title": "Incident Retrospective: SEV-1 Database Failover and Checkout Latency Spike",
        "content": """# Incident Summary & Timeline
On October 28, 2026, at 14:02 UTC, automated health monitoring detected a critical latency spike across all production API gateways. Within 3 minutes, checkout failure rates spiked from 0.02% to 68.4%. The incident lasted for 18 minutes until full recovery at 14:20 UTC.
A total of 4,200 active checkout sessions were terminated prematurely, resulting in an estimated immediate revenue loss of $64,000. Customer support received 312 escalated support tickets during the window.

# Root Cause Analysis
The incident was triggered during a scheduled non-peak database migration script (PR #4912) executed by the payments squad.
The migration script attempted to add a foreign key constraint on the `orders_v2` table without the `NOT VALID` qualifier and concurrent index creation. Under active read/write load, PostgreSQL acquired an exclusive AccessExclusiveLock on the active partition.
This lock caused all incoming transaction threads to block, exhausting the database connection pool (max_connections=2000) within 45 seconds. The automated circuit breaker failed to trigger because the health check endpoint responded with 200 OK while existing idle connections remained open.

# Detection & Incident Response
- 14:02 UTC: Datadog alert `P99_API_Latency > 2500ms` fired in `#incident-prod`.
- 14:05 UTC: Incident Commander declared SEV-1 and initiated War Room bridge.
- 14:09 UTC: Database SRE identified the blocked table lock on `orders_v2` via `pg_stat_activity`.
- 14:14 UTC: SRE team terminated the blocking migration PID `18492` and initiated failover to hot read-replica `aurora-db-replica-02`.
- 14:18 UTC: Replica promoted to primary; connection pool drained and stabilized.
- 14:20 UTC: Checkout error rate dropped below 0.05%; Incident Commander declared mitigation.

# Architectural Vulnerabilities & Risks
1. Database Cluster Topology: The primary database instance represents a single point of failure under table-level lock contention. Active-active multi-region failover has not yet been implemented for the payments ledger.
2. Unenforced Migration Guardrails: CI/CD pull request pipelines lacked automated linting checks (e.g., `strong_migrations` or `squawk`) to prevent synchronous table locks on partitioned tables.
3. Health Check Fidelity: The database readiness probe was testing shallow socket availability rather than active transaction query execution latency.

# Remediation & Action Items
1. Deploy automated CI/CD migration linter blocking unindexed table alterations and non-concurrent indexes. Owner: DevOps Lead (P0, Due: Oct 31).
2. Reconfigure Aurora automated failover health probes and drop failover threshold from 15m to 45s. Owner: Database Lead (P0, Due: Nov 02).
3. Implement dynamic query circuit breakers with exponential backoff on payment gateways. Owner: Payments Squad (P1, Due: Nov 06).
4. Conduct full disaster recovery chaos engineering drill on read-replica promotion under synthetic load. Owner: SRE Team (P1, Due: Nov 15).
5. Issue customer communications postmortem and provide service credits to top 50 affected enterprise merchants. Owner: VP of Customer Success (P1, Due: Oct 30).
"""
    },
    "Q3 SaaS Financial & Operational Review": {
        "title": "Quarterly Business Review: Q3 FY2026 Financial & Operational Performance",
        "content": """# Executive Summary & Top-Line Performance
In Q3 FY2026, the company generated strong financial acceleration across all core enterprise segments.
Ending Annual Recurring Revenue (ARR) reached $52.4M, representing an annualized growth rate of 38% Year-over-Year (YoY), surpassing the board forecast of $49.8M. Net New ARR added during the quarter was $4.6M.
Enterprise customer count grew to 384 accounts (+24 accounts net addition), with Average Contract Value (ACV) expanding from $112,000 to $136,000. Net Dollar Retention (NDR) remained best-in-class at 124%, driven by strong cross-sell adoption of our AI automation add-on module.

# Gross Margin & Unit Economics
Non-GAAP Gross Margin closed at 74.2%, reflecting a 180 basis point contraction compared to 76.0% in Q2.
The margin compression was directly attributable to accelerated GPU token inference consumption associated with the newly launched AI Agent product line. Infrastructure compute expenditure on Google Cloud and frontier LLM APIs increased from $620K/month to $1.15M/month.
Customer Acquisition Cost (CAC) Payback period improved to 14.2 months, compared to 16.5 months in the prior quarter, driven by higher inbound sales velocity and enterprise reference accounts.

# Regional & Sales Pipeline Breakdown
- North America (NA): Delivered $34.8M ARR (66% of total), growing 42% YoY. Enterprise win rate against competitors stood at 58%.
- EMEA: Generated $12.6M ARR (24% of total), growing 28% YoY. Average sales cycle length lengthened from 42 days to 68 days due to heightened European data privacy (GDPR / AI Act) procurement reviews.
- APAC: Contributed $5.0M ARR (10% of total), expanding 46% YoY off a smaller base, led by Japan and Australia financial services adoption.

# Strategic Risks & Operational Headwinds
1. Compute Cost Runaway: If AI inference token usage continues to grow at the current 25% month-over-month rate without semantic caching or unit pricing tiers, gross margins will degrade below our 70% long-term target by Q1 FY2027.
2. Regulatory Friction in EMEA: Extended compliance evaluations are creating pipeline slippage for 7 seven-figure enterprise contracts scheduled for Q4 closure.
3. Senior Engineering Capacity: Specialized AI platform and distributed systems recruitment remains behind hiring targets by 6 open headcount.

# Strategic Priorities & Board Action Plan
1. Implement edge semantic caching gateway and prompt compression to reduce LLM token consumption by 35%. Owner: VP Engineering (P0, Target: Nov 20).
2. Restructure enterprise AI contracts to introduce consumption-based token metering overages above baseline quotas. Owner: VP Product (P0, Target: Nov 15).
3. Achieve ISO 42001 (AI Management System) and EU AI Act compliance certification to accelerate European enterprise procurement. Owner: Chief Legal & Compliance Officer (P1, Target: Dec 15).
4. Accelerate APAC field partner distribution model to capture inbound sovereign cloud opportunities. Owner: Chief Revenue Officer (P2, Target: Jan 2027).
"""
    },
    "SOC2 Type II Security Compliance Audit": {
        "title": "SOC2 Type II Security & Trust Services Compliance Assessment",
        "content": """# Scope of Audit & Compliance Overview
Between May 1, 2026, and October 15, 2026, independent third-party auditor Ernst & Young conducted a SOC2 Type II examination of the production cloud environment, data pipelines, and developer access controls against the AICPA Trust Services Criteria: Security, Availability, and Confidentiality.
The examination reviewed 148 security controls spanning infrastructure access, continuous integration pipelines, cryptographic key management, employee lifecycle management, and incident response procedures.

# Auditor Findings & Control Exceptions
The audit concluded with an Unqualified Opinion with two minor control exceptions:
1. Exception SEC-042 (Access Deprovisioning Latency): In 3 out of 45 employee terminations sampled during the audit period, Okta single sign-on access and GitHub repository permissions were revoked between 48 and 72 hours after termination, exceeding the required 24-hour SLA. No unauthorized data access occurred.
2. Exception ENC-018 (Key Rotation Evidence): Secondary backup database snapshots in AWS us-east-2 lacked automated audit logging proving that KMS envelope encryption keys were rotated within the mandatory 365-day cadence. The keys were active and valid, but rotation event logs were purged prematurely.

# Identity, Infrastructure & Zero-Trust Posture
- Multi-Factor Authentication (MFA): 100% of internal accounts enforce FIDO2 WebAuthn hardware security keys. SMS and email OTP have been entirely eliminated.
- Secrets Management: Hardcoded secrets scanning in CI/CD detected zero exposed API keys or private certificates across 82 active git repositories over the 6-month observation period.
- Vulnerability Remediation: Mean Time to Remediate (MTTR) for critical CVE vulnerabilities averaged 4.2 days, well within the compliance requirement of 14 days.

# Residual Security Risks
1. Deprovisioning Automation Gap: Manual notification handoffs between Workday HRIS and Identity IT teams introduce potential windows of stale account credentials.
2. Retention of Compliance Audit Logs: CloudTrail and KMS logging retention policies were set to 90 days rather than the required 365 days on secondary archival buckets.

# Remediation Commitments
1. Integrate Workday webhook with Okta API for automated, zero-touch account suspension within 15 minutes of employee offboarding. Owner: IT Security Director (P0, Target: Nov 10).
2. Extend CloudTrail and KMS log lifecycle retention rules in Terraform to 400 days with immutable S3 Object Lock. Owner: Cloud Security Lead (P0, Target: Oct 30).
3. Re-audit deprovisioning and key rotation controls with EY for clean SOC2 final report issuance. Owner: Chief Information Security Officer (P1, Target: Nov 25).
"""
    }
}
