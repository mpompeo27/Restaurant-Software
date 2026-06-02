-- Learning sandbox for designing the database for the Restaurant Software web app project

-- Add a 'server' column to the 'tables' table
ALTER TABLE tables ADD COLUMN server_id INTEGER REFERENCES staff(id);