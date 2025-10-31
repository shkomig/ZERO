# Zero Agent Monitoring

## Prometheus
- קובץ scrape: `monitoring/prometheus.yml`
- הגדר ב-Prometheus (prometheus.exe או Docker) את הקובץ הזה; הוא יגרד את `http://localhost:8080/metrics` כל 5 שניות.

## Grafana
- ייבא את `monitoring/grafana-dashboard-zero.json` כ-dashboard חדש.
- הדשבורד מציג:
  - Requests/min, Error rate
  - Latency p50/p95 ל-`/api/chat` ו-`/api/chat/auto`
  - טבלת בקשות לפי נתיב/סטטוס (1m)

## הפעלה מהירה (Windows)
1. התקן Prometheus ו-Grafana (או Docker Desktop).
2. הפעל Prometheus עם `--config.file monitoring/prometheus.yml`.
3. פתח Grafana (ברירת מחדל `http://localhost:3000`), הוסף Data Source מסוג Prometheus עם `http://localhost:9090`.
4. ייבא את ה-dashboard JSON.

## הרחבות מומלצות
- להוסיף מטריקות ייעודיות לזמן רוטינג ולשלבי smart/coder.
- התראות (Alerting) על error rate וזמן תגובה p95.




