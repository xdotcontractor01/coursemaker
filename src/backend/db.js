const Database = require('better-sqlite3');
const path = require('path');
const fs = require('fs');
require('dotenv').config();

const dbPath = process.env.DB_PATH || './data/jobs.db';
const dbDir = path.dirname(dbPath);

if (!fs.existsSync(dbDir)) {
  fs.mkdirSync(dbDir, { recursive: true });
}

const db = new Database(dbPath, { verbose: console.log });

// Initialize tables
db.exec(`
  CREATE TABLE IF NOT EXISTS jobs (
    id TEXT PRIMARY KEY,
    md_content TEXT,
    status TEXT CHECK(status IN ('pending','processing','done','error','degraded')) DEFAULT 'pending',
    current_step INTEGER DEFAULT 0,
    output_path TEXT,
    tokens JSON DEFAULT '{}',
    errors JSON DEFAULT '[]',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
  );

  CREATE TABLE IF NOT EXISTS job_errors (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    job_id TEXT,
    step_no INTEGER,
    error_type TEXT,
    details TEXT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    retry_count INTEGER DEFAULT 0,
    fallback_used BOOLEAN DEFAULT 0,
    FOREIGN KEY(job_id) REFERENCES jobs(id)
  );
`);

module.exports = db;




