CREATE USER usuario_etl WITH PASSWORD 'senha_super_secreta'; 
GRANT ALL PRIVILEGES ON DATABASE data_delivery TO usuario_etl; 
GRANT ALL PRIVILEGES ON SCHEMA public TO usuario_etl; 
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO usuario_etl; 
