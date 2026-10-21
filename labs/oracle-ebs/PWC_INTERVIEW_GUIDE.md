# PwC Interview Guide — Oracle EBS Academy

## Interview Process for EBS Roles

### Rounds
- **Round 1 – Partner/Senior Manager Screen (45 min)**: Client service orientation, deal experience, practice area fit. "What's your experience implementing EBS for a Fortune 500 company?" Expect thoughtful questions about risk management and compliance.
- **Round 2 – Technical & Functional (1 hr)**: Hands-on EBS exercise — configure a ledger, write a PL/SQL reconciliation script, analyze a security setup gap. Focus on controls, SOX, and compliance.
- **Round 3 – Case Study (1 hr)**: Present a solution to a client scenario. "A manufacturing client is migrating EBS to the cloud. Advise on risk, controls, and implementation approach." Time-constrained presentation.
- **Round 4 – Cultural Fit (45 min)**: PwC values — "Act with Integrity", "Make a Difference", "Care", "Collaborate", "Work with Purpose, Reimagine the Possible."
- **Timeline**: 2–4 weeks. PwC has a rigorous partner-review process.

### EBS-Specific Expectations
- PwC is a professional services firm — EBS roles sit at the intersection of technology, process, and risk/controls.
- SOX compliance is a major theme. Expect questions about Segregation of Duties (SoD), access controls, audit trails, and GRC (Governance, Risk, and Compliance).
- PwC values consulting experience with a controls mindset. "How do you design an EBS solution that is both efficient and SOX-compliant?"
- Certifications: CISA, CIA, CPA, PMP are valued alongside OCP.
- Industry specialization: Financial services, manufacturing, energy, public sector.

## Top Technical Problems by Lab

### Lab 02: System Administration and Security

#### Problem: Segregation of Duties (SoD) — Incompatible Responsibilities
- **Difficulty/Frequency**: High / Very Frequent
- **Problem statement**: A client's SOX audit found that 3 users have both AP Invoice Approval and PO Creation responsibilities. Write a PL/SQL routine to scan all users for SoD conflicts based on a rules matrix, generate a report of violations, and provide the remediation logic (auto-revoke or escalate to manager).
- **Interview walkthrough**: SoD is about preventing any user from having conflicting responsibilities (e.g., Create PO + Approve Invoice). The conflict rules are stored in a custom table or in FND_RESPONSIBILITY dependencies. Use FND_USER_RESP_GROUPS_DIRECT to find user-responsibility assignments. Create a conflict matrix table custom_sod_rules with resp_key_a, resp_key_b, severity. Join to find users assigned to both. For remediation, update end_date or notify via workflow.
- **SQL/PLSQL/Java solution**:
`sql
CREATE TABLE custom_sod_rules (
  rule_id          NUMBER PRIMARY KEY,
  rule_name        VARCHAR2(100),
  resp_key_a       VARCHAR2(50),
  resp_key_b       VARCHAR2(50),
  severity         VARCHAR2(10) CHECK (severity IN ('HIGH','MEDIUM','LOW')),
  description      VARCHAR2(500),
  created_date     DATE DEFAULT SYSDATE
);

INSERT INTO custom_sod_rules VALUES
(1, 'PO_CREATE_AP_APPROVE', 'PO_CREATE', 'AP_APPROVE',
 'HIGH', 'User should not both create POs and approve invoices');
INSERT INTO custom_sod_rules VALUES
(2, 'GL_POST_GL_ADJUST', 'GL_POST', 'GL_ADJUST',
 'HIGH', 'User should not both post and adjust journal entries');

CREATE OR REPLACE PROCEDURE sod_violation_report AS
  CURSOR c_violations IS
    SELECT fu.user_name,
           fu.description user_desc,
           sr.rule_name,
           sr.severity,
           ra.responsibility_name resp_a,
           rb.responsibility_name resp_b,
           fur1.start_date start_date_a,
           fur2.start_date start_date_b
      FROM fnd_user fu,
           fnd_user_resp_groups_direct fur1,
           fnd_user_resp_groups_direct fur2,
           custom_sod_rules sr,
           fnd_responsibility_vl ra,
           fnd_responsibility_vl rb
     WHERE fu.user_id = fur1.user_id
       AND fu.user_id = fur2.user_id
       AND fur1.responsibility_id = ra.responsibility_id
       AND fur2.responsibility_id = rb.responsibility_id
       AND ra.responsibility_key = sr.resp_key_a
       AND rb.responsibility_key = sr.resp_key_b
       AND fur1.end_date IS NULL
       AND fur2.end_date IS NULL
     ORDER BY sr.severity, fu.user_name;

  PROCEDURE revoke_responsibility (p_user_id NUMBER, p_resp_id NUMBER) IS
  BEGIN
    UPDATE fnd_user_resp_groups_direct
       SET end_date = SYSDATE
     WHERE user_id = p_user_id
       AND responsibility_id = p_resp_id
       AND end_date IS NULL;
  END revoke_responsibility;

BEGIN
  fnd_file.put_line(fnd_file.output,
    'User,Rule,Severity,ResponsibilityA,ResponsibilityB,Action');
  FOR rec IN c_violations LOOP
    IF rec.severity = 'HIGH' THEN
      revoke_responsibility(rec.user_id, rec.resp_id_b);
      fnd_file.put_line(fnd_file.output,
        rec.user_name || ',' || rec.rule_name || ',HIGH,' ||
        rec.resp_a || ',' || rec.resp_b || ',AUTO-REVOKED');
    ELSE
      fnd_file.put_line(fnd_file.output,
        rec.user_name || ',' || rec.rule_name || ',MEDIUM,' ||
        rec.resp_a || ',' || rec.resp_b || ',ESCALATED');
    END IF;
  END LOOP;
  COMMIT;
END sod_violation_report;
/
`
- **EBS-specific context**: FND_USER, FND_USER_RESP_GROUPS_DIRECT, FND_RESPONSIBILITY_VL, end_date based deactivation, WHO columns for audit trail.
- **What PwC evaluates**: Controls and compliance mindset, SoD knowledge, audit trail understanding, remediation strategy.
- **Follow-ups**: How do you handle SoD conflicts at the function level vs responsibility level? Explain Oracle GRC (Governance, Risk, and Compliance) integration. How do you audit SoD remediation?

#### Problem: Oracle Audit Vault — EBS Audit Trail Configuration
- **Difficulty/Frequency**: Medium / Frequent
- **Problem statement**: A client needs to enable fine-grained auditing (FGA) on AP_INVOICES_ALL for SOX compliance — track all SELECT, INSERT, UPDATE, DELETE by non-AP users. Write the FGA policy and an audit review query.
- **Interview walkthrough**: Use DBMS_FGA.ADD_POLICY to create Fine-Grained Audit policies on sensitive EBS tables. Logs go to DBA_FGA_AUDIT_TRAIL. For EBS-specific audit, add conditions like excluding AP responsibility users. The audit data can be consumed by Oracle Audit Vault for centralized monitoring.
- **SQL/PLSQL/Java solution**:
`sql
CREATE OR REPLACE PROCEDURE setup_ebs_fga AS
BEGIN
  DBMS_FGA.DROP_POLICY(
    object_schema => 'APPS',
    object_name   => 'AP_INVOICES_ALL',
    policy_name   => 'AP_INVOICE_SOX_AUDIT'
  );
EXCEPTION WHEN OTHERS THEN NULL;
END;
/

BEGIN
  DBMS_FGA.ADD_POLICY(
    object_schema   => 'APPS',
    object_name     => 'AP_INVOICES_ALL',
    policy_name     => 'AP_INVOICE_SOX_AUDIT',
    audit_condition => 'USER NOT IN (''APUSER'',''APMGR'')',
    audit_column    => 'INVOICE_AMOUNT,VENDOR_ID,INVOICE_NUM',
    handler_schema  => 'APPS',
    handler_module  => 'FGA_AP_NOTIFY',
    enable          => TRUE,
    statement_types => 'SELECT,INSERT,UPDATE,DELETE'
  );
  COMMIT;
END;
/

CREATE OR REPLACE PROCEDURE fga_ap_notify (
  p_schema    VARCHAR2,
  p_table     VARCHAR2,
  p_policy    VARCHAR2
) AS
  PRAGMA AUTONOMOUS_TRANSACTION;
BEGIN
  INSERT INTO custom_fga_alert_log
  (object_schema, object_name, policy_name,
   event_time, db_user, client_info)
  VALUES (p_schema, p_table, p_policy,
          SYSDATE, USER, SYS_CONTEXT('USERENV','CLIENT_INFO'));
  COMMIT;
END fga_ap_notify;
/

-- Audit review query
SELECT db_user, object_name, sql_text,
       timestamp, statement_type
  FROM dba_fga_audit_trail
 WHERE object_name = 'AP_INVOICES_ALL'
   AND timestamp >= SYSDATE - 7
 ORDER BY timestamp DESC;
`
- **EBS-specific context**: AP_INVOICES_ALL, DBMS_FGA, DBA_FGA_AUDIT_TRAIL, Oracle Audit Vault, FND_LOGIN_RESP_FORMS for user context.
- **What PwC evaluates**: Audit configuration expertise, SOX compliance understanding, detective controls in EBS.
- **Follow-ups**: Compare FGA vs standard auditing vs unified auditing in Oracle 19c. How do you monitor audit log integrity? What are the key SOX-relevant EBS tables?

### Lab 03: Financials (GL, AP, AR)

#### Problem: Subledger to GL Reconciliation — SOX Control
- **Difficulty/Frequency**: High / Very Frequent
- **Problem statement**: A client needs a SOX-control report that reconciles the AP subledger to the GL for each period. Write a PL/SQL procedure that compares AP_INVOICES_ALL totals against GL_BALANCES and reports discrepancies > ,000 as exceptions requiring management sign-off.
- **Interview walkthrough**: Use XLA_TRANSACTIONS_GT (Subledger Accounting) to get SLA distributions linked to AP invoices. Join with GL_JE_LINES via journal entry header. Compare period totals. For AP subledger, use AP_INVOICES_ALL and AP_INVOICE_DISTRIBUTIONS_ALL. For GL, use GL_BALANCES filtered by source = 'Payables'. Discrepancies indicate missing postings or data corruption.
- **SQL/PLSQL/Java solution**:
`sql
CREATE OR REPLACE PROCEDURE ap_gl_reconciliation (
  p_period_name  IN VARCHAR2,
  p_ledger_id    IN NUMBER,
  p_threshold    IN NUMBER DEFAULT 1000
) AS
  CURSOR c_recon IS
    WITH ap_totals AS (
      SELECT SUM(NVL(aid.amount, 0)) ap_amount,
             COUNT(DISTINCT ai.invoice_id) invoice_count
        FROM ap_invoices_all ai,
             ap_invoice_distributions_all aid
       WHERE ai.invoice_id = aid.invoice_id
         AND ai.approval_status = 'APPROVED'
         AND ai.invoice_date BETWEEN
             (SELECT period_start_date
                FROM gl_period_statuses
               WHERE period_name = p_period_name
                 AND application_id = 200  -- AP
                 AND ledger_id = p_ledger_id)
             AND (SELECT period_end_date
                   FROM gl_period_statuses
                  WHERE period_name = p_period_name
                    AND application_id = 200
                    AND ledger_id = p_ledger_id)
    ),
    gl_totals AS (
      SELECT SUM(NVL(gls.period_net_dr, 0) -
                 NVL(gls.period_net_cr, 0)) gl_amount
        FROM gl_balances gls,
             gl_code_combinations gcc
       WHERE gls.code_combination_id = gcc.code_combination_id
         AND gls.period_name = p_period_name
         AND gls.ledger_id = p_ledger_id
         AND gls.actual_flag = 'A'
         AND gls.source_code = 'Payables'
    )
    SELECT ap.ap_amount, gl.gl_amount,
           NVL(ap.ap_amount, 0) - NVL(gl.gl_amount, 0) difference,
           ap.invoice_count
      FROM ap_totals ap, gl_totals gl;

  l_status VARCHAR2(30);
BEGIN
  FOR rec IN c_recon LOOP
    IF ABS(rec.difference) > p_threshold THEN
      INSERT INTO recon_exceptions
      (period_name, ledger_id, source, subledger_amount,
       gl_amount, difference, created_date, status)
      VALUES (p_period_name, p_ledger_id, 'AP',
              rec.ap_amount, rec.gl_amount, rec.difference,
              SYSDATE, 'OPEN');
      l_status := 'EXCEPTION';
    ELSE
      l_status := 'MATCHED';
    END IF;

    fnd_file.put_line(fnd_file.output,
      'Period: ' || p_period_name ||
      ' | AP: ' || TO_CHAR(NVL(rec.ap_amount, 0)) ||
      ' | GL: ' || TO_CHAR(NVL(rec.gl_amount, 0)) ||
      ' | Diff: ' || TO_CHAR(rec.difference) ||
      ' | Status: ' || l_status);
  END LOOP;

  COMMIT;
END ap_gl_reconciliation;
/
`
- **EBS-specific context**: AP_INVOICES_ALL, AP_INVOICE_DISTRIBUTIONS_ALL, GL_BALANCES, XLA_TRANSACTIONS_GT, GL_PERIOD_STATUSES, subledger accounting (SLA).
- **What PwC evaluates**: SOX control design, reconciliation methodology, understanding of subledger accounting, exception handling.
- **Follow-ups**: How does SLA (Subledger Accounting) work? What are XLA_TRANSACTIONS_GT and XLA_AE_HEADERS? How do you automate this control with management sign-off workflow?

### Lab 07: Reporting (BI Publisher, XML)

#### Problem: Compliance Dashboard — BI Publisher
- **Difficulty/Frequency**: High / Frequent
- **Problem statement**: Build a BI Publisher report that serves as a compliance dashboard for the audit committee. Show: number of SoD violations, open audit findings, critical change requests pending approval, and password policy exceptions. Write the data model SQL and explain the dashboard layout.
- **Interview walkthrough**: Create a master data model with multiple queries (one per metric). Use BI Publisher bursting to distribute to audit committee members. For SoD violations, query custom_sod_rules joined with FND_USER_RESP_GROUPS_DIRECT. For password exceptions, query FND_USER where last_update_date > 90 days or no password change in 180 days.
- **SQL/PLSQL/Java solution**:
`sql
-- Data model queries for compliance dashboard
-- Query 1: SoD Violations Count
SELECT COUNT(*) sod_violations,
       sr.severity
  FROM custom_sod_rules sr,
       fnd_user_resp_groups_direct fur1,
       fnd_user_resp_groups_direct fur2
 WHERE fur1.responsibility_id IN (
           SELECT responsibility_id
             FROM fnd_responsibility_vl
            WHERE responsibility_key = sr.resp_key_a
       )
   AND fur2.responsibility_id IN (
           SELECT responsibility_id
             FROM fnd_responsibility_vl
            WHERE responsibility_key = sr.resp_key_b
       )
   AND fur1.user_id = fur2.user_id
   AND fur1.end_date IS NULL
   AND fur2.end_date IS NULL
 GROUP BY sr.severity;

-- Query 2: Password Policy Exceptions
SELECT fu.user_name,
       fu.last_logon_date,
       fu.last_update_date,
       CASE
         WHEN fu.last_logon_date < SYSDATE - 90 THEN 'OVERDUE'
         ELSE 'COMPLIANT'
       END password_status
  FROM fnd_user fu
 WHERE fu.end_date IS NULL
   AND fu.last_logon_date IS NOT NULL
 ORDER BY fu.last_logon_date;

-- Query 3: Open Audit Findings (custom table)
SELECT af.finding_id,
       af.finding_type,
       af.description,
       af.severity,
       af.reported_date,
       af.owner,
       af.target_resolution_date,
       CASE
         WHEN af.target_resolution_date < SYSDATE THEN 'OVERDUE'
         ELSE 'OPEN'
       END status
  FROM custom_audit_findings af
 WHERE af.resolution_date IS NULL
 ORDER BY af.severity, af.target_resolution_date;

-- BI Publisher Bursting control file
/*
<?xml version="1.0" encoding="UTF-8"?>
<xdo:burst xmlns:xdo="http://xmlns.oracle.com/oxp/xdo">
  <delivery>
    <email from="compliance@company.com"
           to="audit-committee@company.com"
           subject="Monthly Compliance Dashboard"
           body="Please find attached the compliance dashboard report."/>
  </delivery>
</xdo:burst>
*/
`
- **EBS-specific context**: FND_USER, FND_USER_RESP_GROUPS_DIRECT, FND_RESPONSIBILITY_VL, BI Publisher data models, bursting, XDO_META_TABLES.
- **What PwC evaluates**: Compliance and risk reporting, BI Publisher data modeling, understanding of what audit committees need.
- **Follow-ups**: How do you schedule BI Publisher reports in EBS? What is the role of FND_SRS_RUNS? Explain BI Publisher security by responsibility.

### Lab 09: Security

#### Problem: Data Encryption at Rest — EBS PII Tables
- **Difficulty/Frequency**: Medium / Frequent
- **Problem statement**: A client needs to encrypt PII (Personally Identifiable Information) in EBS — supplier bank accounts (AP_BANK_ACCOUNTS_ALL), employee SSN (PER_PEOPLE_F), customer credit cards. Design the encryption strategy using Oracle Transparent Data Encryption (TDE) and write the implementation SQL.
- **Interview walkthrough**: TDE (Transparent Data Encryption) encrypts data at rest. Configure Oracle Wallet, create encryption key, encrypt tablespace containing sensitive tables. For columns, use TDE column encryption (salt + encrypt). For EBS, use DBMS_CRYPTO for application-level encryption when TDE is not feasible. Key management via Oracle Wallet or HSM.
- **SQL/PLSQL/Java solution**:
`sql
-- 1. Configure Oracle Wallet
ADMINISTER KEY MANAGEMENT CREATE KEYSTORE
  'C:\oracle\wallet' IDENTIFIED BY "WalletPwd123";

ADMINISTER KEY MANAGEMENT SET KEYSTORE OPEN
  IDENTIFIED BY "WalletPwd123";

ADMINISTER KEY MANAGEMENT SET KEY
  IDENTIFIED BY "WalletPwd123"
  WITH BACKUP USING 'initial_key';

-- 2. Encrypt tablespace containing PII tables
ALTER TABLESPACE APPS_TS_TX_DATA ENCRYPTION ONLINE
  USING 'AES256'
  ENCRYPT FILE_NAME_CONVERT = ('ts_tx_data.dbf', 'ts_tx_data_enc.dbf');

-- 3. Column-level TDE for sensitive columns
ALTER TABLE apps.ap_bank_accounts_all
  MODIFY (bank_account_name ENCRYPT USING 'AES256');

ALTER TABLE apps.per_people_f
  MODIFY (national_identifier ENCRYPT USING 'AES256');

-- 4. Alternative: application-level encryption
CREATE OR REPLACE PACKAGE app_encrypt AS
  FUNCTION encrypt_data(p_data VARCHAR2) RETURN RAW;
  FUNCTION decrypt_data(p_encrypted RAW) RETURN VARCHAR2;
END app_encrypt;
/

CREATE OR REPLACE PACKAGE BODY app_encrypt AS
  l_key RAW(32) := HEXTORAW('ABCDEF0123456789ABCDEF0123456789');
  
  FUNCTION encrypt_data(p_data VARCHAR2) RETURN RAW IS
  BEGIN
    RETURN DBMS_CRYPTO.ENCRYPT(
      src => UTL_I18N.STRING_TO_RAW(p_data, 'AL32UTF8'),
      typ => DBMS_CRYPTO.ENCRYPT_AES256 + DBMS_CRYPTO.CHAIN_CBC,
      key => l_key
    );
  END encrypt_data;

  FUNCTION decrypt_data(p_encrypted RAW) RETURN VARCHAR2 IS
  BEGIN
    RETURN UTL_I18N.RAW_TO_CHAR(
      DBMS_CRYPTO.DECRYPT(
        src => p_encrypted,
        typ => DBMS_CRYPTO.ENCRYPT_AES256 + DBMS_CRYPTO.CHAIN_CBC,
        key => l_key
      ),
      'AL32UTF8'
    );
  END decrypt_data;
END app_encrypt;
/
`
- **EBS-specific context**: AP_BANK_ACCOUNTS_ALL, PER_PEOPLE_F, TDE, Oracle Wallet, DBMS_CRYPTO, FND_ENCRYPTION_KEY, data masking policies.
- **What PwC evaluates**: Data security and privacy expertise, PII classification, encryption strategy, key management, GDPR/PII compliance.
- **Follow-ups**: How does TDE impact performance in EBS? What is the difference between TDE and DBMS_CRYPTO? How do you handle key rotation without downtime?

## EBS-Specific Deep Dive Questions

- **SOX Compliance in EBS**: Walk through the SOX compliance framework for an EBS implementation — control objectives, control activities, monitoring. What are the key automated controls? How are segregation of duties enforced? How do you test control effectiveness?
- **IT General Controls (ITGC)**: Access to programs and data, program changes, computer operations. How do you implement ITGC for EBS? Change management via Oracle EBS patch management. Access reviews for FND_USER, FND_RESPONSIBILITY.
- **GRC (Governance, Risk, and Compliance)**: Oracle GRC integration with EBS — Oracle Advanced Access Controls (OAAC), Oracle Advanced Financial Controls (OAFC). How do you monitor for SoD violations in real-time?
- **Internal Audit Approach**: How would you audit an EBS implementation from a financial controls perspective? Key risk areas: period close, inventory valuation, revenue recognition.
- **Data Privacy (GDPR, CCPA)**: How do you handle Right to Erasure (Data Deletion) in EBS? Identify PII in tables, anonymization via DBMS_REDEFINITION, deletion cascading in AP/AR.
- **Regulatory Reporting**: EBS configuration for regulatory reports — tax reporting (1099, VAT), GAAP/IFRS reporting. Multi-GAAP ledgers in R12.

## Behavioral Questions (STAR)

- **Situation**: Client's SOX audit identified 45 critical SoD violations across 3 modules.
  - **Task**: Remediate within 2 weeks before audit deadline.
  - **Action**: Built PL/SQL script to scan all 1,200+ EBS users against a 50-rule conflict matrix. Used Oracle GRC Predefined Controls. Auto-remediated HIGH severity violations by end-dating conflicting responsibilities. Presented remediation report to internal audit committee.
  - **Result**: Passed SOX audit with zero findings. Remediation completed in 10 days.

- **Situation**: GDPR data subject access request received — need to locate all PII data for a former employee across 12 EBS modules.
  - **Task**: Locate and report all PII within 30 days.
  - **Action**: Created a data discovery procedure using FND_TABLES and FND_COLUMNS with patterns matching PII attributes. Joined PER_PEOPLE_F with FND_USER, AP_BANK_ACCOUNTS_ALL, PO_VENDORS. Generated comprehensive report in BI Publisher.
  - **Result**: Data subject report delivered in 7 days. Zero data missed.

- **Situation**: Client wanted to rush an EBS custom report without proper change management.
  - **Task**: Ensure SOX-compliant change management.
  - **Action**: Refused to bypass ITGC procedures. Documented change request in the ITSM tool, performed code review, tested in DEV/UAT, obtained CAB approval. Trained client on ITGC compliance importance.
  - **Result**: Change implemented in 3 days with full compliance. Client adopted improved change management process.

- **Situation**: Revenue recognition audit revealed inconsistent revenue GL accounts across 4 countries.
  - **Task**: Harmonize revenue recognition configuration.
  - **Action**: Mapped each country's revenue recognition rules in RA_CUSTOMER_TRX_ALL and AR_RECEIVABLE_APPLICATIONS_ALL. Configured AutoAccounting rules to standardize GL accounts. Implemented revenue recognition concurrent program (ARXRWRR) for monthly validation.
  - **Result**: Revenue account consistency achieved. Audit finding closed.

- **Situation**: Disaster recovery drill failed because EBS backups were not decrypting properly.
  - **Task**: Fix DR process for encrypted backups.
  - **Action**: Identified that TDE wallet was not being copied to DR site. Automated wallet synchronization using scripts and Oracle Data Guard configuration. Documented full DR runbook including keystore restoration steps.
  - **Result**: Next DR drill passed. Recovery time reduced from 8 hours to 2.5 hours.

## Study Plan

| Priority | Labs |
|----------|------|
| Must | Lab 02 (System Admin/Security), Lab 03 (Financials), Lab 07 (Reporting), Lab 09 (Security) |
| Recommended | Lab 01 (Architecture), Lab 08 (Integrations), Lab 10 (Upgrade/Migration) |
| Additional | Lab 04 (Supply Chain), Lab 06 (Customization/OAF) |
| Niche | Lab 05 (HRMS) |

## Tips

- **Controls mindset**: PwC interviews are heavily focused on risk and controls. Every technical answer should include "and here's how we ensure SOX compliance."
- **SoD expertise**: Be prepared to discuss Segregation of Duties in depth — not just what it is, but how to detect, prevent, and remediate violations in EBS.
- **Audit standards**: Know the key standards — COSO, COBIT, ISO 27001. How do they map to EBS controls?
- **GRC tools**: Familiarity with Oracle GRC (OAAC, OAFC) is a strong differentiator.
- **Professional certifications**: PwC values CISA, CIA, CPA. If you have or are pursuing these, highlight them.
- **Industry knowledge**: PwC serves financial services heavily. EBS experience with banks or insurance companies is especially valuable.
- **Communication skills**: PwC consultants must communicate with audit committees and CFOs. Practice explaining technical EBS issues in business terms.
- **Documentation**: PwC expects thorough documentation of all controls, configurations, and changes. "If it's not documented, it didn't happen."
