-- Success-ratio dashboard query
-- Calculates the success ratio for each source

SELECT
    source,
    SUM(CASE WHEN status = 'success' THEN 1 ELSE 0 END) * 100.0 / COUNT(*) as success_ratio,
    COUNT(*) as total_jobs
FROM job_audits
GROUP BY source
ORDER BY success_ratio DESC;
