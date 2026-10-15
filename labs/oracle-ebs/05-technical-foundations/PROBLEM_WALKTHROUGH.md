# Problem Walkthrough: Custom PL/SQL Concurrent Program with EBS APIs

## Problem Statement

**Design and build a production-grade custom PL/SQL concurrent program for Oracle EBS R12.2 that reads external supplier data from an interface table, validates it against EBS standards, processes it through standard EBS APIs (PO, AP, INV), and generates detailed execution reports with error handling, rollback capabilities, and audit logging.**

The client is a manufacturing company that receives supplier price lists via EDI. The EDI files are loaded into a staging table but need a custom concurrent program to: (1) validate supplier data against EBS supplier master, (2) create/update supplier sites and contacts, (3) update purchasing item prices, and (4) generate a comprehensive execution report. The current manual process takes 3 days per price list update; they need it in under 1 hour.

### Business Requirements
- Process 10,000+ price list lines per run
- Multi-mode execution: VALIDATE_ONLY, PROCESS, ROLLBACK
- Comprehensive error handling with detailed error log
- XML concurrent program output with summary and detail sections
- Parameter-driven: supplier range, category, effective date
- Audit trail for all DML operations (who, when, what)
- Rollback capability in case of post-processing issues

### Technical Constraints
- Oracle EBS R12.2 with standard PO, AP, INV modules
- Concurrent Manager execution with FND_REQUEST
- Must use standard EBS APIs (not direct INSERT/UPDATE on base tables)
- Must honor Multi-Org Access Control (MOAC)
- Output must be XML format for BI Publisher integration
- Must pass Oracle CEMLI standards for customizations

---

## Architecture Overview

```
+---------------------------+
|   Concurrent Manager      |
|   (FND_REQUEST)           |
+-----------+---------------+
            |
+-----------v---------------+
| XX_SUPPLIER_PRICE_UPDATE  |
| (Main Entry Point)        |
+-----------+---------------+
            |
    +-------+-------+-------+
    |       |       |       |
    v       v       v       |
+--------+ +-----+ +------+ |
|VALIDATE| |PROC. | |ROLLBK| |
| ONLY   | |ESS   | |ACK   | |
+--------+ +-----+ +------+ |
            |       |       |
            +-------+-------+
                    |
         +----------v--------+
         | Output Generation  |
         | (XML via FND_FILE) |
         +-------------------+
```

### Step 1: Interface Table Design

```sql
CREATE TABLE xx_supplier_price_staging (
  batch_id              NUMBER NOT NULL,
  line_id               NUMBER NOT NULL,
  source_line_number    VARCHAR2(50),
  supplier_number       VARCHAR2(30) NOT NULL,
  supplier_site_code    VARCHAR2(15),
  supplier_contact_name VARCHAR2(240),
  item_number           VARCHAR2(50) NOT NULL,
  item_description      VARCHAR2(250),
  uom_code              VARCHAR2(3),
  list_price            NUMBER,
  effective_date        DATE,
  expiration_date       DATE,
  currency_code         VARCHAR2(15) DEFAULT 'USD',
  process_flag          VARCHAR2(1) DEFAULT 'N',
  validation_status     VARCHAR2(20),
  error_message         VARCHAR2(4000),
  request_id            NUMBER,
  processed_date        DATE,
  created_by            NUMBER,
  creation_date         DATE DEFAULT SYSDATE,
  CONSTRAINT xx_spp_stg_pk PRIMARY KEY (batch_id, line_id)
);

CREATE TABLE xx_supplier_price_batches (
  batch_id              NUMBER PRIMARY KEY,
  batch_name            VARCHAR2(100),
  total_lines           NUMBER,
  validated_lines       NUMBER,
  processed_lines       NUMBER,
  error_lines           NUMBER,
  batch_status          VARCHAR2(20),
  request_id            NUMBER,
  execution_mode        VARCHAR2(20),
  created_by            NUMBER,
  creation_date         DATE DEFAULT SYSDATE,
  last_updated_by       NUMBER,
  last_update_date      DATE
);

CREATE TABLE xx_supplier_price_audit (
  audit_id              NUMBER PRIMARY KEY,
  batch_id              NUMBER,
  line_id               NUMBER,
  audit_timestamp       DATE DEFAULT SYSDATE,
  audit_action          VARCHAR2(50),
  audit_status          VARCHAR2(20),
  table_name            VARCHAR2(100),
  record_id             NUMBER,
  old_value             VARCHAR2(4000),
  new_value             VARCHAR2(4000),
  error_message         VARCHAR2(4000),
  created_by            NUMBER
);

CREATE SEQUENCE xx_supplier_price_batches_s;
CREATE SEQUENCE xx_supplier_price_audit_s;
```

### Step 2: Validation Engine

```sql
CREATE OR REPLACE PACKAGE xx_supplier_validation_pkg AS
  FUNCTION validate_supplier_exists(p_supplier_number VARCHAR2) RETURN VARCHAR2;
  FUNCTION validate_item_exists(p_item_number VARCHAR2, p_org_id NUMBER) RETURN VARCHAR2;
  FUNCTION validate_price(p_list_price NUMBER) RETURN VARCHAR2;
  PROCEDURE validate_batch(p_batch_id NUMBER, p_org_id NUMBER);
END xx_supplier_validation_pkg;
/

CREATE OR REPLACE PACKAGE BODY xx_supplier_validation_pkg AS

  FUNCTION validate_supplier_exists(p_supplier_number VARCHAR2) RETURN VARCHAR2 IS
    l_vendor_id NUMBER;
  BEGIN
    SELECT vendor_id INTO l_vendor_id
    FROM po_vendors
    WHERE segment1 = p_supplier_number AND enabled_flag = 'Y';
    RETURN 'Y';
  EXCEPTION
    WHEN NO_DATA_FOUND THEN RETURN 'N';
  END validate_supplier_exists;

  FUNCTION validate_item_exists(p_item_number VARCHAR2, p_org_id NUMBER) RETURN VARCHAR2 IS
    l_item_id NUMBER;
  BEGIN
    SELECT inventory_item_id INTO l_item_id
    FROM mtl_system_items_b
    WHERE segment1 = p_item_number
    AND organization_id = p_org_id
    AND inventory_item_flag = 'Y';
    RETURN 'Y';
  EXCEPTION
    WHEN NO_DATA_FOUND THEN RETURN 'N';
  END validate_item_exists;

  FUNCTION validate_price(p_list_price NUMBER) RETURN VARCHAR2 IS
  BEGIN
    IF p_list_price IS NULL THEN RETURN 'NULL_PRICE';
    ELSIF p_list_price <= 0 THEN RETURN 'NEGATIVE';
    ELSIF p_list_price > 999999999 THEN RETURN 'TOO_HIGH';
    ELSE RETURN 'VALID';
    END IF;
  END validate_price;

  PROCEDURE validate_batch(p_batch_id NUMBER, p_org_id NUMBER) IS
    CURSOR lines_cur IS
      SELECT * FROM xx_supplier_price_staging
      WHERE batch_id = p_batch_id AND process_flag = 'N';
    l_supplier_ok VARCHAR2(1);
    l_item_ok     VARCHAR2(1);
    l_price_valid VARCHAR2(30);
    l_errors      NUMBER := 0;
    l_validated   NUMBER := 0;
  BEGIN
    FOR rec IN lines_cur LOOP
      l_supplier_ok := validate_supplier_exists(rec.supplier_number);
      l_item_ok := validate_item_exists(rec.item_number, p_org_id);
      l_price_valid := validate_price(rec.list_price);

      IF l_supplier_ok = 'N' THEN
        UPDATE xx_supplier_price_staging
        SET validation_status = 'ERROR',
            error_message = 'Supplier ' || rec.supplier_number || ' not found'
        WHERE batch_id = p_batch_id AND line_id = rec.line_id;
        l_errors := l_errors + 1;
      ELSIF l_item_ok = 'N' THEN
        UPDATE xx_supplier_price_staging
        SET validation_status = 'ERROR',
            error_message = 'Item ' || rec.item_number || ' not found'
        WHERE batch_id = p_batch_id AND line_id = rec.line_id;
        l_errors := l_errors + 1;
      ELSIF l_price_valid != 'VALID' THEN
        UPDATE xx_supplier_price_staging
        SET validation_status = 'ERROR',
            error_message = 'Price validation: ' || l_price_valid
        WHERE batch_id = p_batch_id AND line_id = rec.line_id;
        l_errors := l_errors + 1;
      ELSE
        UPDATE xx_supplier_price_staging
        SET validation_status = 'VALIDATED'
        WHERE batch_id = p_batch_id AND line_id = rec.line_id;
        l_validated := l_validated + 1;
      END IF;
    END LOOP;

    UPDATE xx_supplier_price_batches
    SET validated_lines = l_validated,
        error_lines = l_errors,
        batch_status = CASE WHEN l_errors = 0 THEN 'VALIDATED' ELSE 'VALIDATED_WITH_ERRORS' END
    WHERE batch_id = p_batch_id;

    COMMIT;
  END validate_batch;

END xx_supplier_validation_pkg;
/
```

### Step 3: Processing Engine Using EBS APIs

```sql
CREATE OR REPLACE PACKAGE xx_supplier_processing_pkg AS
  PROCEDURE create_supplier_site(p_batch_id NUMBER, p_line_id NUMBER, p_org_id NUMBER);
  PROCEDURE update_supplier_price(p_batch_id NUMBER, p_line_id NUMBER, p_org_id NUMBER);
  PROCEDURE process_batch(p_batch_id NUMBER, p_org_id NUMBER);
  PROCEDURE rollback_batch(p_batch_id NUMBER);
END xx_supplier_processing_pkg;
/

CREATE OR REPLACE PACKAGE BODY xx_supplier_processing_pkg AS

  PROCEDURE create_supplier_site(
    p_batch_id NUMBER, p_line_id NUMBER, p_org_id NUMBER
  ) IS
    l_vendor_id      NUMBER;
    l_vendor_site_id NUMBER;
    l_result         VARCHAR2(200);
  BEGIN
    SELECT vendor_id INTO l_vendor_id
    FROM po_vendors
    WHERE segment1 = (
      SELECT supplier_number FROM xx_supplier_price_staging
      WHERE batch_id = p_batch_id AND line_id = p_line_id
    );

    -- Use standard EBS API for supplier site
    l_vendor_site_id := po_vendor_site_api.create_vendor_site(
      p_vendor_id              => l_vendor_id,
      p_vendor_site_code       => 'PRICE_LIST_' || p_line_id,
      p_purchasing_site_flag   => 'Y',
      p_rfq_site_flag          => 'N',
      p_pay_site_flag          => 'Y',
      p_primary_pay_site_flag  => 'Y',
      p_org_id                 => p_org_id,
      p_inactive_date          => NULL
    );

    INSERT INTO xx_supplier_price_audit (
      audit_id, batch_id, line_id, audit_action,
      audit_status, table_name, record_id, new_value
    ) VALUES (
      xx_supplier_price_audit_s.NEXTVAL, p_batch_id, p_line_id,
      'CREATE_SITE', 'SUCCESS', 'PO_VENDOR_SITES',
      l_vendor_site_id, 'Site code: PRICE_LIST_' || p_line_id
    );

  EXCEPTION
    WHEN OTHERS THEN
      INSERT INTO xx_supplier_price_audit (
        audit_id, batch_id, line_id, audit_action,
        audit_status, error_message
      ) VALUES (
        xx_supplier_price_audit_s.NEXTVAL, p_batch_id, p_line_id,
        'CREATE_SITE', 'FAILURE', SQLERRM
      );
  END create_supplier_site;

  PROCEDURE update_supplier_price(
    p_batch_id NUMBER, p_line_id NUMBER, p_org_id NUMBER
  ) IS
    l_item_id     NUMBER;
    l_price_list_line_id NUMBER;
  BEGIN
    SELECT inventory_item_id INTO l_item_id
    FROM mtl_system_items_b
    WHERE segment1 = (
      SELECT item_number FROM xx_supplier_price_staging
      WHERE batch_id = p_batch_id AND line_id = p_line_id
    ) AND organization_id = p_org_id;

    -- Use standard Purchasing API for price update
    po_price_list_api.update_line(
      p_price_list_line_id   => l_price_list_line_id,
      p_item_id              => l_item_id,
      p_list_price           => (
        SELECT list_price FROM xx_supplier_price_staging
        WHERE batch_id = p_batch_id AND line_id = p_line_id
      ),
      p_effective_date       => (
        SELECT effective_date FROM xx_supplier_price_staging
        WHERE batch_id = p_batch_id AND line_id = p_line_id
      ),
      p_expiration_date      => (
        SELECT expiration_date FROM xx_supplier_price_staging
        WHERE batch_id = p_batch_id AND line_id = p_line_id
      ),
      p_org_id               => p_org_id
    );

    INSERT INTO xx_supplier_price_audit (
      audit_id, batch_id, line_id, audit_action,
      audit_status, table_name, record_id, new_value
    ) VALUES (
      xx_supplier_price_audit_s.NEXTVAL, p_batch_id, p_line_id,
      'UPDATE_PRICE', 'SUCCESS', 'PO_PRICE_LIST_LINES',
      l_price_list_line_id, 'Price: $' || (
        SELECT list_price FROM xx_supplier_price_staging
        WHERE batch_id = p_batch_id AND line_id = p_line_id
      )
    );

  EXCEPTION
    WHEN OTHERS THEN
      INSERT INTO xx_supplier_price_audit (
        audit_id, batch_id, line_id, audit_action,
        audit_status, error_message
      ) VALUES (
        xx_supplier_price_audit_s.NEXTVAL, p_batch_id, p_line_id,
        'UPDATE_PRICE', 'FAILURE', SQLERRM
      );
  END update_supplier_price;

  PROCEDURE process_batch(p_batch_id NUMBER, p_org_id NUMBER) IS
    CURSOR valid_lines_cur IS
      SELECT line_id FROM xx_supplier_price_staging
      WHERE batch_id = p_batch_id AND validation_status = 'VALIDATED';
    l_processed NUMBER := 0;
    l_errors    NUMBER := 0;
  BEGIN
    FOR rec IN valid_lines_cur LOOP
      BEGIN
        create_supplier_site(p_batch_id, rec.line_id, p_org_id);
        update_supplier_price(p_batch_id, rec.line_id, p_org_id);

        UPDATE xx_supplier_price_staging
        SET process_flag = 'Y',
            processed_date = SYSDATE,
            request_id = FND_GLOBAL.CONC_REQUEST_ID
        WHERE batch_id = p_batch_id AND line_id = rec.line_id;

        l_processed := l_processed + 1;
      EXCEPTION
        WHEN OTHERS THEN
          l_errors := l_errors + 1;
      END;
    END LOOP;

    UPDATE xx_supplier_price_batches
    SET processed_lines = l_processed,
        error_lines = l_errors,
        batch_status = CASE WHEN l_errors = 0 THEN 'PROCESSED' ELSE 'PROCESSED_WITH_ERRORS' END
    WHERE batch_id = p_batch_id;

    COMMIT;
  END process_batch;

  PROCEDURE rollback_batch(p_batch_id NUMBER) IS
    CURSOR audit_cur IS
      SELECT * FROM xx_supplier_price_audit
      WHERE batch_id = p_batch_id
      AND audit_status = 'SUCCESS'
      ORDER BY audit_id DESC;
  BEGIN
    FOR rec IN audit_cur LOOP
      IF rec.audit_action = 'CREATE_SITE' THEN
        po_vendor_site_api.disable_vendor_site(
          p_vendor_site_id => rec.record_id
        );
      ELSIF rec.audit_action = 'UPDATE_PRICE' THEN
        po_price_list_api.restore_previous_price(
          p_price_list_line_id => rec.record_id
        );
      END IF;
    END LOOP;

    UPDATE xx_supplier_price_batches
    SET batch_status = 'ROLLED_BACK'
    WHERE batch_id = p_batch_id;

    DELETE FROM xx_supplier_price_audit
    WHERE batch_id = p_batch_id;

    COMMIT;
  END rollback_batch;

END xx_supplier_processing_pkg;
/
```

### Step 4: Main Concurrent Program Entry Point

This is the entry point registered with the EBS Concurrent Manager:

```sql
CREATE OR REPLACE PROCEDURE xx_supplier_price_update (
  errbuf          OUT VARCHAR2,
  retcode         OUT VARCHAR2,
  p_batch_id      IN  NUMBER,
  p_execution_mode IN VARCHAR2,  -- VALIDATE_ONLY, PROCESS, ROLLBACK
  p_org_id        IN  NUMBER DEFAULT NULL
) IS
  l_org_id        NUMBER;
  l_total_lines   NUMBER;
  l_valid_lines   NUMBER;
  l_error_lines   NUMBER;
  l_start_time    DATE := SYSDATE;
BEGIN
  -- Set organization context (MOAC)
  IF p_org_id IS NOT NULL THEN
    MO_GLOBAL.INIT(p_org_id);
    FND_GLOBAL.ORG_ID := p_org_id;
  END IF;

  -- Validate batch exists
  BEGIN
    SELECT total_lines INTO l_total_lines
    FROM xx_supplier_price_batches
    WHERE batch_id = p_batch_id;
  EXCEPTION
    WHEN NO_DATA_FOUND THEN
      retcode := 1;
      errbuf := 'Batch ' || p_batch_id || ' not found';
      FND_FILE.PUT_LINE(FND_FILE.OUTPUT, errbuf);
      RETURN;
  END;

  -- Write XML header for output
  FND_FILE.PUT_NAMES('SUPPLIER_PRICE_UPDATE', '1.0', '');
  FND_FILE.PUT_LINE(FND_FILE.OUTPUT,
    '<SupplierPriceUpdate batch_id="' || p_batch_id || '"
      execution_mode="' || p_execution_mode || '">');

  -- Mode dispatch
  IF p_execution_mode = 'VALIDATE_ONLY' THEN
    FND_FILE.PUT_LINE(FND_FILE.OUTPUT, '<Phase>VALIDATION</Phase>');
    xx_supplier_validation_pkg.validate_batch(p_batch_id, p_org_id);

  ELSIF p_execution_mode = 'PROCESS' THEN
    -- First validate
    FND_FILE.PUT_LINE(FND_FILE.OUTPUT, '<Phase>VALIDATION</Phase>');
    xx_supplier_validation_pkg.validate_batch(p_batch_id, p_org_id);

    -- Check for errors
    SELECT validated_lines, error_lines
    INTO l_valid_lines, l_error_lines
    FROM xx_supplier_price_batches
    WHERE batch_id = p_batch_id;

    IF l_error_lines > 0 THEN
      FND_FILE.PUT_LINE(FND_FILE.OUTPUT,
        '<ValidationResult valid_lines="' || l_valid_lines
        || '" error_lines="' || l_error_lines || '"/>');
      FND_FILE.PUT_LINE(FND_FILE.OUTPUT,
        '<Warning>Processing with errors. Continuing.</Warning>');
    END IF;

    -- Process
    FND_FILE.PUT_LINE(FND_FILE.OUTPUT, '<Phase>PROCESSING</Phase>');
    xx_supplier_processing_pkg.process_batch(p_batch_id, p_org_id);

  ELSIF p_execution_mode = 'ROLLBACK' THEN
    FND_FILE.PUT_LINE(FND_FILE.OUTPUT, '<Phase>ROLLBACK</Phase>');
    xx_supplier_processing_pkg.rollback_batch(p_batch_id);
  END IF;

  -- Summary
  SELECT total_lines, validated_lines, processed_lines, error_lines, batch_status
  INTO l_total_lines, l_valid_lines, l_error_lines, l_error_lines, l_total_lines
  FROM xx_supplier_price_batches
  WHERE batch_id = p_batch_id;

  FND_FILE.PUT_LINE(FND_FILE.OUTPUT,
    '<Summary>
      <BatchId>' || p_batch_id || '</BatchId>
      <ExecutionMode>' || p_execution_mode || '</ExecutionMode>
      <StartTime>' || TO_CHAR(l_start_time, 'YYYY-MM-DD HH24:MI:SS') || '</StartTime>
      <EndTime>' || TO_CHAR(SYSDATE, 'YYYY-MM-DD HH24:MI:SS') || '</EndTime>
      <DurationMinutes>' || ROUND((SYSDATE - l_start_time) * 24 * 60, 2) || '</DurationMinutes>
    </Summary>');

  FND_FILE.PUT_LINE(FND_FILE.OUTPUT, '</SupplierPriceUpdate>');

  -- Return code: 0=success, 1=warning, 2=error
  IF l_error_lines > 0 AND l_execution_mode = 'VALIDATE_ONLY' THEN
    retcode := 1;
  ELSIF l_error_lines > 0 THEN
    retcode := 0;
  ELSE
    retcode := 0;
  END IF;

  COMMIT;

EXCEPTION
  WHEN OTHERS THEN
    retcode := 2;
    errbuf := SQLERRM;
    FND_FILE.PUT_LINE(FND_FILE.OUTPUT,
      '<FatalError>' || SQLERRM || '</FatalError>');
    FND_FILE.PUT_LINE(FND_FILE.OUTPUT, '</SupplierPriceUpdate>');
    ROLLBACK;
END xx_supplier_price_update;
/
```

### Step 5: Concurrent Program Definition

Register the concurrent program in EBS:

```sql
-- Register executable
BEGIN
  FND_PROGRAM_REGISTRATION_PKG.REGISTER_EXECUTABLE(
    p_application    => 'SQLAP',
    p_exec_name      => 'XX_SUPPLIER_PRICE_UPDATE',
    p_exec_method    => 'PL/SQL Stored Procedure',
    p_exec_filename  => 'xx_supplier_price_update.xx_supplier_price_update',
    p_description    => 'Supplier Price List Update Program'
  );
END;
/

-- Register concurrent program with parameters
BEGIN
  FND_PROGRAM_REGISTRATION_PKG.REGISTER_PROGRAM(
    p_application       => 'SQLAP',
    p_program_name      => 'XX_SUPPLIER_PRICE_UPDATE',
    p_program_type      => 'C',
    p_enabled_flag      => 'Y',
    p_executable_name   => 'XX_SUPPLIER_PRICE_UPDATE',
    p_exec_method       => 'PL/SQL Stored Procedure',
    p_executable_file   => 'xx_supplier_price_update.xx_supplier_price_update',
    p_description       => 'Update supplier prices from staging interface'
  );

  -- Batch ID parameter
  FND_PROGRAM_REGISTRATION_PKG.REGISTER_PARAMETER(
    p_program_name      => 'XX_SUPPLIER_PRICE_UPDATE',
    p_parameter_seq     => 1,
    p_parameter_name    => 'p_batch_id',
    p_description       => 'Batch ID from staging table',
    p_required_flag     => 'Y',
    p_data_type         => 'N',
    p_display_flag      => 'Y'
  );

  -- Execution mode parameter
  FND_PROGRAM_REGISTRATION_PKG.REGISTER_PARAMETER(
    p_program_name      => 'XX_SUPPLIER_PRICE_UPDATE',
    p_parameter_seq     => 2,
    p_parameter_name    => 'p_execution_mode',
    p_description       => 'VALIDATE_ONLY, PROCESS, ROLLBACK',
    p_required_flag     => 'Y',
    p_data_type         => 'T',
    p_display_flag      => 'Y',
    p_validation_type   => 'CONSTANT',
    p_validation_value  => 'VALIDATE_ONLY/PROCESS/ROLLBACK'
  );

  -- Organization parameter
  FND_PROGRAM_REGISTRATION_PKG.REGISTER_PARAMETER(
    p_program_name      => 'XX_SUPPLIER_PRICE_UPDATE',
    p_parameter_seq     => 3,
    p_parameter_name    => 'p_org_id',
    p_description       => 'Operating Unit ID (MOAC)',
    p_required_flag     => 'N',
    p_data_type         => 'N',
    p_display_flag      => 'Y'
  );
END;
/
```

### Step 6: XML Report Template for BI Publisher

The concurrent program output can be styled with an XSL template:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet version="1.0"
  xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
  <xsl:template match="/">
    <html>
      <body style="font-family:Arial;font-size:10pt;">
        <h1>Supplier Price Update Report</h1>
        <xsl:apply-templates select="SupplierPriceUpdate/Summary"/>
        <xsl:apply-templates select="SupplierPriceUpdate/Phase"/>
      </body>
    </html>
  </xsl:template>

  <xsl:template match="Summary">
    <h2>Execution Summary</h2>
    <table border="1" width="100%">
      <tr style="background-color:#4CAF50;color:white;">
        <th>Metric</th><th>Value</th>
      </tr>
      <tr><td>Batch ID</td><td><xsl:value-of select="BatchId"/></td></tr>
      <tr><td>Mode</td><td><xsl:value-of select="ExecutionMode"/></td></tr>
      <tr><td>Start</td><td><xsl:value-of select="StartTime"/></td></tr>
      <tr><td>End</td><td><xsl:value-of select="EndTime"/></td></tr>
      <tr><td>Duration</td><td><xsl:value-of select="DurationMinutes"/> min</td></tr>
    </table>
  </xsl:template>
</xsl:stylesheet>
```

---

## Best Practices

### CEMLI Standards Compliance
1. **Naming conventions**: All custom objects must start with XX_ prefix; packages use _pkg suffix; tables use descriptive names
2. **API-only DML**: Never write INSERT/UPDATE/DELETE against Oracle-owned base tables (PO_*, AP_*, MTL_*) — always use public APIs
3. **Savepoint strategy**: Use named savepoints for multi-step processing; rollback to savepoint on line-level failure without losing batch context
4. **FND_FILE output**: Write both summary and detail sections; use FND_FILE.PUT_NAMES for XML format; include execution timestamps

### Error Handling
1. **Three-level error handling**: (a) Line-level validation errors (continue processing), (b) Batch-level errors (stop processing), (c) Fatal errors (rollback everything)
2. **Error categorization**: Categorize errors as DATA (fixable in staging), PROCESS (system issue), or VALIDATION (configuration issue) for faster resolution
3. **Maximum error threshold**: Implement a configurable max_error_count parameter — stop processing when exceeded to prevent cascading failures

### Performance Optimization
1. **Bulk processing**: For >10,000 lines, use BULK COLLECT with LIMIT clause (500-1000 rows per fetch) instead of row-by-row processing
2. **Array processing APIs**: Use EBS-standard array processing APIs (e.g., PO_PRICE_LIST_ARRAY_API) when available for large data volumes
3. **Commit frequency**: Commit every 500 lines to avoid UNDO segment contention; use SAVEPOINT for rollback granularity
4. **Parallel execution**: For truly large batches, partition by supplier category and submit multiple concurrent requests

### Concurrent Program Design Patterns
1. **Idempotency**: Design for re-runnability — skip already-processed lines on re-execution; never create duplicate records
2. **Multi-mode execution**: Always implement VALIDATE_ONLY mode for user preview; PROCESS for actual execution; ROLLBACK for recovery
3. **Parameter validation**: Validate all parameters at entry (batch exists, mode is valid, org is accessible) before processing starts
4. **Output structure**: Follow standard Oracle XML output structure: header, validation results, processing results, summary, footer

### Common Pitfalls
1. **Direct table DML**: Updating AP/PO/INV base tables directly bypasses triggers, validation, and audit — always results in data corruption
2. **Missing MOAC context**: Without MO_GLOBAL.INIT, multi-org queries return wrong data or no data — always set org context first
3. **No commit strategy**: Row-by-row commit causes ORA-01555 (snapshot too old) for long-running programs; batch commit with savepoints is essential
4. **Insufficient error detail**: "Error processing line X" is useless for troubleshooting — include column values, API return messages, and call stack

## Validation Checklist

| Check | Criteria | Method |
|-------|----------|--------|
| Naming convention | XX_ prefix on all objects | Code review |
| API compliance | No direct DML on base tables | Code review |
| Multi-mode | VALIDATE_ONLY, PROCESS, ROLLBACK | Functional test |
| Error handling | Line-level + batch-level + fatal | Negative testing |
| XML output | Well-formed XML with summary | XSD validation |
| MOAC | Correct org data per user | Multi-org test |
| Performance | 10K lines in < 1 hour | Benchmark test |
| Re-runnability | Idempotent re-execution | Regression test |
| Audit trail | All DML captured in audit table | Data validation |
