CREATE TYPE user_role AS ENUM ('admin', 'reception', 'comptable', 'manager');
CREATE TYPE employee_status AS ENUM ('active', 'on_leave', 'sick', 'absent');
CREATE TYPE intervention_status AS ENUM ('planned', 'in_progress', 'done', 'cancelled');
CREATE TYPE expense_status AS ENUM ('draft', 'validated', 'exported');

CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    full_name VARCHAR(120) NOT NULL,
    email VARCHAR(160) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    role user_role NOT NULL DEFAULT 'reception',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS employees (
    id SERIAL PRIMARY KEY,
    full_name VARCHAR(120) NOT NULL,
    function VARCHAR(120) NOT NULL,
    phone VARCHAR(40),
    status employee_status NOT NULL DEFAULT 'active',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS interventions (
    id SERIAL PRIMARY KEY,
    intervention_date DATE NOT NULL,
    client VARCHAR(160) NOT NULL,
    site VARCHAR(180) NOT NULL,
    mission TEXT NOT NULL,
    employee_id INTEGER NOT NULL REFERENCES employees(id),
    status intervention_status NOT NULL DEFAULT 'planned',
    notes TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS travel_expenses (
    id SERIAL PRIMARY KEY,
    intervention_id INTEGER NOT NULL REFERENCES interventions(id),
    distance_km NUMERIC(8, 2) NOT NULL DEFAULT 0,
    transport_amount NUMERIC(10, 2) NOT NULL DEFAULT 0,
    meal_amount NUMERIC(10, 2) NOT NULL DEFAULT 0,
    other_amount NUMERIC(10, 2) NOT NULL DEFAULT 0,
    status expense_status NOT NULL DEFAULT 'draft',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_interventions_date ON interventions(intervention_date);
CREATE INDEX IF NOT EXISTS idx_interventions_employee ON interventions(employee_id);
CREATE INDEX IF NOT EXISTS idx_expenses_intervention ON travel_expenses(intervention_id);
