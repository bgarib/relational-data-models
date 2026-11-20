-- 1. Occupancy by marina: berths rented vs total
SELECT m.NAME, COUNT(b.BERTH_ID) AS berths_modelled,
       SUM(CASE WHEN b.RENTER_PERSON_ID IS NOT NULL THEN 1 ELSE 0 END) AS berths_rented
  FROM marina m LEFT JOIN berth b ON b.MARINA_ID = m.MARINA_ID
 GROUP BY m.NAME ORDER BY m.NAME;

-- 2. Monthly rental income by marina
SELECT m.NAME, SUM(b.MONTHLY_FEE) AS monthly_income
  FROM berth b JOIN marina m ON m.MARINA_ID = b.MARINA_ID
 WHERE b.RENTER_PERSON_ID IS NOT NULL
 GROUP BY m.NAME ORDER BY monthly_income DESC;

-- 3. Vessels with no berth (waiting list)
SELECT v.NAME, v.VESSEL_TYPE, v.LENGTH_M, CONCAT(p.FIRST_NAME, ' ', p.LAST_NAME) AS owner
  FROM vessel v JOIN person p ON p.PERSON_ID = v.OWNER_PERSON_ID
 WHERE v.BERTH_ID IS NULL;
