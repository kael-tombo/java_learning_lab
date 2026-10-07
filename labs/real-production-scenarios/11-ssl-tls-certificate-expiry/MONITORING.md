# Monitoring: SSL/TLS Certificate Expiry

## Monitoring Architecture Overview

The monitoring stack is designed to provide multiple independent detection mechanisms for certificate expiry, ensuring defense in depth. Detection should occur at minimum 30 days before expiry, with automated escalation at 14 days and 7 days.

## 1. Prometheus blackbox_exporter

### Deployment Configuration

```yaml
# prometheus.yml scrape config
scrape_configs:
  - job_name: 'blackbox-ssl'
    metrics_path: /probe
    params:
      module: [ssl_certificate_expiry]
    static_configs:
      - targets:
          - 'https://acmecorp.com'
          - 'https://api.acmecorp.com'
          - 'https://www.acmecorp.com'
          - 'https://app.acmecorp.com'
    relabel_configs:
      - source_labels: [__address__]
        target_label: __param_target
      - source_labels: [__param_target]
        target_label: instance
      - target_label: __address__
        replacement: blackbox-exporter:9115
```

### Key Metrics

| Metric | Type | Description | Threshold |
|--------|------|-------------|-----------|
| `probe_ssl_earliest_cert_expiry` | Gauge | Unix timestamp of earliest cert expiry | 30 days > now |
| `probe_ssl_last_chain_expiry_timestamp_seconds` | Gauge | Expiry of full chain | 30 days > now |
| `probe_success` | Gauge | Probe success (1=up, 0=down) | 1 |
| `probe_duration_seconds` | Gauge | Time to complete probe | < 5s |
| `probe_http_ssl` | Gauge | SSL present (1=yes, 0=no) | 1 |

### Alert Rules

```yaml
groups:
  - name: ssl_certificates
    interval: 5m
    rules:
      - alert: SSLCertExpiringSoon
        expr: probe_ssl_earliest_cert_expiry{job="blackbox-ssl"} - time() < 2592000
        for: 5m
        labels:
          severity: warning
          pagerduty: sre
        annotations:
          summary: "SSL cert for {{ $labels.instance }} expires in {{ $value | humanizeDuration }}"

      - alert: SSLCertExpiringCritical
        expr: probe_ssl_earliest_cert_expiry{job="blackbox-ssl"} - time() < 1209600
        for: 1m
        labels:
          severity: critical
          pagerduty: sre
        annotations:
          summary: "SSL cert for {{ $labels.instance }} expires in < 14 days"

      - alert: SSLCertExpired
        expr: probe_ssl_earliest_cert_expiry{job="blackbox-ssl"} - time() < 0
        for: 0m
        labels:
          severity: critical
          pagerduty: sre
        annotations:
          summary: "SSL cert for {{ $labels.instance }} has EXPIRED!"

      - alert: SSLProbeDown
        expr: probe_success{job="blackbox-ssl"} == 0
        for: 1m
        labels:
          severity: critical
          pagerduty: sre
        annotations:
          summary: "SSL probe failed for {{ $labels.instance }}"
```

## 2. Grafana Dashboard

### Dashboard Panels

1. **Certificate Expiry Countdown** (Singlestat)
   - Query: `probe_ssl_earliest_cert_expiry - time()`
   - Unit: days
   - Color thresholds: green > 30, yellow > 14, red < 14

2. **Certificate Expiry Gauge** (Gauge)
   - Query: `probe_ssl_earliest_cert_expiry{job="blackbox-ssl"}`
   - Min/Max: based on 90-day cert lifecycle
   - Display: time until expiry in days

3. **Domain Status Table** (Table)
   - Query: `probe_success{job="blackbox-ssl"}`
   - Columns: instance, status, expiry date, days remaining

4. **Certificate Chain Check** (Table)
   - Query: `probe_ssl_last_chain_expiry_timestamp_seconds`
   - Display: root, intermediate, leaf cert expiry dates

## 3. Synthetic Monitoring (External)

### Checkly / Pingdom Configuration

```javascript
// Checkly browser check for certificate validation
const { BrowserCheck } = require('checkly');

const check = new BrowserCheck('ssl-cert-check', {
  name: 'SSL Certificate Expiry Check',
  activated: true,
  locations: ['us-east-1', 'eu-west-1', 'ap-southeast-1'],
  frequency: 60, // every 60 minutes
  code: `
    const assert = require('assert');
    const https = require('https');
    
    const domains = ['acmecorp.com', 'api.acmecorp.com', 'www.acmecorp.com'];
    
    domains.forEach(domain => {
      const req = https.get('https://' + domain, (res) => {
        const cert = res.connection.getPeerCertificate();
        const expiryDate = new Date(cert.valid_to);
        const daysRemaining = Math.floor((expiryDate - new Date()) / (1000 * 60 * 60 * 24));
        
        console.log(\`\${domain}: \${daysRemaining} days remaining\`);
        
        if (daysRemaining < 30) {
          throw new Error(\`\${domain} certificate expires in \${daysRemaining} days\`);
        }
        
        assert.ok(daysRemaining > 0, \`\${domain} certificate has expired!\`);
      });
      req.end();
    });
  `,
});
```

## 4. Certificate Transparency Log Monitoring

### Automated CT Log Scanner

```bash
#!/bin/bash
# ct_monitor.sh — Monitor Certificate Transparency logs for upcoming expiries

DOMAINS=("acmecorp.com" "api.acmecorp.com" "www.acmecorp.com" "app.acmecorp.com")
ALERT_WEBHOOK="(link removed)"

for domain in "${DOMAINS[@]}"; do
  echo "Checking CT logs for $domain..."
  
  # Query crt.sh for certificate information
  response=$(curl -s "https://crt.sh/?q=%25.$domain&output=json" 2>/dev/null)
  
  if [ $? -eq 0 ] && [ -n "$response" ] && [ "$response" != "[]" ]; then
    # Extract earliest expiry date
    earliest=$(echo "$response" | jq -r '.[].not_after' | sort | head -1)
    
    if [ -n "$earliest" ] && [ "$earliest" != "null" ]; then
      earliest_epoch=$(date -d "$earliest" +%s 2>/dev/null)
      now_epoch=$(date +%s)
      days_remaining=$(( (earliest_epoch - now_epoch) / 86400 ))
      
      echo "  $domain: earliest cert expires $earliest ($days_remaining days)"
      
      # Alert if less than 30 days
      if [ "$days_remaining" -lt 30 ]; then
        curl -X POST -H "Content-type: application/json" \
          --data "{\"text\":\":warning: *CT Log Alert*: Certificate for $domain expires in $days_remaining days (earliest: $earliest)\"}" \
          "$ALERT_WEBHOOK"
      fi
    fi
  else
    echo "  $domain: no CT log entries found"
  fi
done
```

### Grafana Alert for CT Monitoring

```yaml
- alert: CTLogCertificateExpiry
  expr: ct_certificate_days_remaining{domain=~".*\\.acmecorp\\.com"} < 30
  for: 1h
  labels:
    severity: warning
  annotations:
    summary: "CT log shows certificate for {{ $labels.domain }} expires in {{ $value }} days"
```

## 5. Internal Certificate Inventory (CMDB)

### SQL-Based Expiry Tracking

```sql
-- Certificate inventory table
CREATE TABLE certificate_inventory (
    id SERIAL PRIMARY KEY,
    common_name VARCHAR(255) NOT NULL,
    serial_number VARCHAR(64),
    issuer_ca VARCHAR(128),
    valid_from TIMESTAMP,
    valid_to TIMESTAMP,
    days_to_expiry AS (valid_to - CURRENT_TIMESTAMP),
    owner_email VARCHAR(255),
    auto_renew BOOLEAN DEFAULT true,
    monitoring_enabled BOOLEAN DEFAULT true,
    last_checked TIMESTAMP,
    alert_sent_30d BOOLEAN DEFAULT false,
    alert_sent_14d BOOLEAN DEFAULT false,
    alert_sent_7d BOOLEAN DEFAULT false
);

-- Query for expiring certificates
SELECT common_name, valid_to,
    EXTRACT(DAY FROM valid_to - CURRENT_TIMESTAMP) as days_remaining
FROM certificate_inventory
WHERE valid_to < CURRENT_TIMESTAMP + INTERVAL '30 days'
  AND auto_renew = false;
```

## 6. Alert Escalation Matrix

| Days Remaining | Severity | Notification | Response Time |
|---------------|----------|-------------|--------------|
| 30 | Warning | Slack #ops-alerts | 24 hours |
| 14 | Warning | Slack + Email + PagerDuty | 4 hours |
| 7 | Critical | PagerDuty + Phone | 1 hour |
| 1 | Critical | PagerDuty + VP Engineering | 15 minutes |
| 0 | SEV1 | Full incident response | Immediate |

## 7. Runbook Integration

```yaml
# alertmanager.yml — Route for SSL alerts
routes:
  - match:
      alertname: SSLCertExpiringSoon
    receiver: slack-ops
    repeat_interval: 24h

  - match:
      alertname: SSLCertExpiringCritical
    receiver: pagerduty-sre
    repeat_interval: 4h

  - match:
      alertname: SSLCertExpired
    receiver: pagerduty-sre-critical
    repeat_interval: 15m

receivers:
  - name: slack-ops
    slack_configs:
      - channel: '#ops-alerts'
        send_resolved: true

  - name: pagerduty-sre
    pagerduty_configs:
      - routing_key: $PAGERDUTY_ROUTING_KEY
        severity: warning

  - name: pagerduty-sre-critical
    pagerduty_configs:
      - routing_key: $PAGERDUTY_ROUTING_KEY
        severity: critical
```

## 8. Monitoring Health Checks

```bash
#!/bin/bash
# Daily monitoring health check
echo "=== SSL Monitoring Health Check ==="
date

# Check blackbox_exporter is up
curl -sf http://localhost:9115/health > /dev/null && \
  echo "PASS: blackbox_exporter is running" || \
  echo "FAIL: blackbox_exporter is DOWN"

# Check SSL metrics are being scraped
curl -sf http://localhost:9115/metrics | grep -q probe_ssl_earliest_cert_expiry && \
  echo "PASS: SSL expiry metrics available" || \
  echo "FAIL: SSL expiry metrics missing"

# Verify alert rules are loaded
curl -sf http://localhost:9090/api/v1/rules | jq -e '.data.groups[].rules[] | select(.name=="SSLCertExpired")' > /dev/null && \
  echo "PASS: SSL alert rules active" || \
  echo "FAIL: SSL alert rules missing"

# Check certbot renewal timer
systemctl is-active certbot-renewal.timer > /dev/null && \
  echo "PASS: certbot renewal timer active" || \
  echo "FAIL: certbot renewal timer NOT active"

# Verify last renewal success
journalctl -u certbot-renewal.service --since "30 days ago" | grep -q "Skipped" && \
  echo "PASS: certbot renewals running (skipped = no renewal needed)" || \
  echo "INFO: checking if renewal occurred recently..."

echo "=== Health Check Complete ==="
```

## References

- Prometheus blackbox_exporter: https://github.com/prometheus/blackbox_exporter
- Google SRE Monitoring: https://sre.google/sre-book/monitoring-distributed-systems/
- Let's Encrypt Monitoring: (link removed)
- Cloudflare SSL Monitoring: (link removed)
