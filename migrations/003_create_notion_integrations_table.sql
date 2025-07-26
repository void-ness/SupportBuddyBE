-- Create notion_integrations table
CREATE TABLE IF NOT EXISTS notion_integrations (
    id SERIAL PRIMARY KEY,
    user_id INTEGER UNIQUE NOT NULL,
    access_token VARCHAR(255) NOT NULL,
    page_id VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);
