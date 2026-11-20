-- Sample data for the marina model (fictional people and vessels)
INSERT INTO marina (MARINA_ID, NAME, CITY, COUNTRY, TOTAL_BERTHS, PHONE, EMAIL) VALUES
  (1, 'Puerto Deportivo Sotogrande', 'San Roque', 'Spain', 3, '+34 956 000 001', 'info@marina-sotogrande.example'),
  (2, 'Club de Yates Algarrobo', 'Algarrobo', 'Chile', 2, '+56 33 000 0002', 'contacto@yates-algarrobo.example');

INSERT INTO person (PERSON_ID, FIRST_NAME, LAST_NAME, DOCUMENT_ID, EMAIL, PHONE, NATIONALITY, BIRTH_DATE) VALUES
  (1, 'Lucia', 'Ferrer', 'X1000001', 'lucia.ferrer@example.com', NULL, 'Spanish', '1985-04-12'),
  (2, 'Tomas', 'Rojas', 'C2000002', 'tomas.rojas@example.com', '+56 9 0000 0002', 'Chilean', '1979-11-03'),
  (3, 'Anna', 'Keller', 'D3000003', 'anna.keller@example.com', NULL, 'German', NULL);

INSERT INTO berth (BERTH_ID, MARINA_ID, BERTH_CODE, MAX_LENGTH_M, MAX_BEAM_M, DEPTH_M, HAS_ELECTRICITY, MONTHLY_FEE, RENTER_PERSON_ID, RENTAL_START_DATE, RENTAL_END_DATE) VALUES
  (1, 1, 'A-01', 12.00, 4.20, 3.50, 1, 650.00, 1, '2026-01-01', '2026-12-31'),
  (2, 1, 'A-02', 15.00, 5.00, 4.00, 1, 820.00, NULL, NULL, NULL),
  (3, 2, 'P-01', 10.00, 3.80, 2.80, 0, 410.00, 2, '2026-03-01', NULL);

INSERT INTO vessel (VESSEL_ID, OWNER_PERSON_ID, BERTH_ID, NAME, REGISTRATION_NUMBER, VESSEL_TYPE, LENGTH_M, BEAM_M, BUILD_YEAR) VALUES
  (1, 1, 1,    'Brisa',     'ES-7-SG-1001', 'Sailboat',  11.40, 3.90, 2015),
  (2, 2, 3,    'Pelicano',  'CL-VAL-2002',  'Motorboat',  9.20, 3.10, 2019),
  (3, 3, NULL, 'Nordlicht', 'DE-HH-3003',   'Catamaran', 13.10, 7.20, 2021);
