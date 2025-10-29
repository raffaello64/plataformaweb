-- Permitir conectarse a la base
GRANT CONNECT ON DATABASE tfg_db TO tfg_user;

-- Permisos completos sobre la base
GRANT ALL PRIVILEGES ON DATABASE tfg_db TO tfg_user;

-- Permisos sobre el esquema 'public' para que Django cree tablas
GRANT ALL PRIVILEGES ON SCHEMA public TO tfg_user;
