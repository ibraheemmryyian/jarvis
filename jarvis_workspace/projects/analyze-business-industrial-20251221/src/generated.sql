CREATE TABLE sustainability_initiatives (
    id UUID PRIMARY KEY,
    company_id UUID REFERENCES companies(id),
    initiative_name VARCHAR(255) NOT NULL,
    description TEXT,
    status VARCHAR(50),
    start_date DATE,
    end_date DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);