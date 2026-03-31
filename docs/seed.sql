INSERT INTO users (username, password, role) VALUES
('admin1', '1234', 'admin'),
('operador1', 'abcd', 'operator');

INSERT INTO sensors (id, type, location, token, status) VALUES
('S001', 'vibration', 'puente_norte', 'token_vib_001', 'active'),
('S002', 'inclination', 'puente_norte', 'token_inc_002', 'active'),
('S003', 'humidity', 'edificio_bloque_a', 'token_hum_003', 'active'),
('S004', 'temperature', 'edificio_bloque_a', 'token_temp_004', 'active'),
('S005', 'stress', 'puente_norte', 'token_str_005', 'active');

INSERT INTO readings (sensor_id, value) VALUES
('S001', 8.4),
('S002', 4.2),
('S003', 72.5),
('S004', 33.1),
('S005', 65.0);

INSERT INTO alerts (sensor_id, level, message) VALUES
('S001', 'high', 'Vibracion anormal detectada en puente_norte');

INSERT INTO watchlist (user_id, sensor_id) VALUES
(2, 'S001'),
(2, 'S005');