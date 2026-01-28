-- Database migration for clean system architecture
-- Adds JSONB columns for structured data storage

-- Add new columns to report_sections table
ALTER TABLE report_sections 
ADD COLUMN IF NOT EXISTS tables_data JSONB,
ADD COLUMN IF NOT EXISTS charts_data JSONB,
ADD COLUMN IF NOT EXISTS metrics_data JSONB;

-- Create chart_images table
CREATE TABLE IF NOT EXISTS chart_images (
    id SERIAL PRIMARY KEY,
    report_id INTEGER REFERENCES enhanced_reports(id) ON DELETE CASCADE,
    section_type VARCHAR(50) NOT NULL,
    chart_title VARCHAR(255) NOT NULL,
    image_data TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Create index for faster lookups
CREATE INDEX IF NOT EXISTS idx_chart_images_report 
ON chart_images(report_id, section_type);

-- Add unique constraint to prevent duplicate sections
ALTER TABLE report_sections 
DROP CONSTRAINT IF EXISTS unique_report_section;

ALTER TABLE report_sections 
ADD CONSTRAINT unique_report_section 
UNIQUE (report_id, section_type);

-- Verify schema
SELECT 
    column_name, 
    data_type 
FROM information_schema.columns 
WHERE table_name = 'report_sections' 
ORDER BY ordinal_position;
