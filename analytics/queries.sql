-- 📊 Analytics Queries for Sea Around Us Dataset
-- These queries are designed to run on Amazon Athena against the Curated/Processed Parquet data.

-- 1. Total Catch Amount by Region and Species
-- Purpose: Identify which regions and species are most productive.
SELECT 
    region, 
    species, 
    SUM(catch_amount) AS total_catch,
    AVG(effort_hours) AS avg_effort
FROM 
    "sea_around_us_curated"."processed_data"
GROUP BY 
    region, 
    species
ORDER BY 
    total_catch DESC;

-- 2. Yearly Trend of Fishing Effort
-- Purpose: Analyze how fishing effort changes over time.
SELECT 
    year(date) AS fishing_year,
    SUM(effort_hours) AS annual_effort,
    SUM(catch_amount) AS annual_catch
FROM 
    "sea_around_us_curated"."processed_data"
GROUP BY 
    year(date)
ORDER BY 
    fishing_year DESC;

-- 3. High-Yielding Regions (Catch per unit of effort)
-- Purpose: Find the most efficient fishing regions.
SELECT 
    region,
    SUM(catch_amount) / NULLIF(SUM(effort_hours), 0) AS catch_per_effort_unit
FROM 
    "sea_around_us_curated"."processed_data"
GROUP BY 
    region
HAVING 
    SUM(effort_hours) > 0
ORDER BY 
    catch_per_effort_unit DESC;