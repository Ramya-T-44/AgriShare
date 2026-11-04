-- ==========================================
-- AgriShareDB - DEMO DATA (SQL Server)
-- ==========================================
-- Run this AFTER schema.sql has created the tables.
-- All demo accounts share the password:  password123
-- ==========================================

USE AgriShareDB;
GO

-- Clear old demo data so this script is re-runnable
DELETE FROM Bookings;
DELETE FROM Equipment;
DELETE FROM Users;
GO

-- ==========================================
-- 1) INSERT USERS
--    UserID is IDENTITY(1,1) so it auto-starts at 1
-- ==========================================
INSERT INTO Users (FullName, Email, PasswordHash, PhoneNumber, VillageName, CreatedAt) VALUES
('Ramesh Kumar',   'ramesh@gmail.com',   'scrypt:32768:8:1$GraKF5AeIWdPXQXB$2a3f084a429a5a9094059ac780973e58fdf67d7533bfed4f6aa73692071224e594bdf757583721ca7515578044697967aa1c6d970c8d3019f683151dc5dab76e', '9876543210', 'Rampur',      GETDATE()),
('Sita Devi',      'sita@gmail.com',     'scrypt:32768:8:1$GraKF5AeIWdPXQXB$2a3f084a429a5a9094059ac780973e58fdf67d7533bfed4f6aa73692071224e594bdf757583721ca7515578044697967aa1c6d970c8d3019f683151dc5dab76e', '9876543211', 'Rampur',      GETDATE()),
('Gopal Singh',    'gopal@gmail.com',    'scrypt:32768:8:1$GraKF5AeIWdPXQXB$2a3f084a429a5a9094059ac780973e58fdf67d7533bfed4f6aa73692071224e594bdf757583721ca7515578044697967aa1c6d970c8d3019f683151dc5dab76e', '9876543212', 'Kisan Nagar', GETDATE()),
('Lakshmi Bai',    'lakshmi@gmail.com',  'scrypt:32768:8:1$GraKF5AeIWdPXQXB$2a3f084a429a5a9094059ac780973e58fdf67d7533bfed4f6aa73692071224e594bdf757583721ca7515578044697967aa1c6d970c8d3019f683151dc5dab76e', '9876543213', 'Kisan Nagar', GETDATE()),
('Hari Prasad',    'hari@gmail.com',     'scrypt:32768:8:1$GraKF5AeIWdPXQXB$2a3f084a429a5a9094059ac780973e58fdf67d7533bfed4f6aa73692071224e594bdf757583721ca7515578044697967aa1c6d970c8d3019f683151dc5dab76e', '9876543214', 'Green Valley', GETDATE());
GO

-- ==========================================
-- 2) INSERT EQUIPMENT
--    EquipmentID auto-starts at 1
-- ==========================================
INSERT INTO Equipment (Title, Category, HourlyRate, DailyRate, OwnerID, IsAvailable, CreatedAt) VALUES
('Mahindra Tractor 475',    'Tractor',        500,  3500, 1, 1, GETDATE()),
('John Deere Harvester',    'Harvester',      1200, 8000, 2, 1, GETDATE()),
('Kirloskar Irrigation Pump','Irrigation Pump',200,  1200, 3, 1, GETDATE()),
('Swaraj Tractor 744',      'Tractor',        550,  3800, 4, 1, GETDATE()),
('Mini Harvester Combo',    'Harvester',      1000, 6500, 5, 1, GETDATE()),
('Water Pump 5HP',          'Irrigation Pump',180,  1000, 1, 1, GETDATE()),
('Tractor Trolley',         'Tractor',        300,  1800, 2, 1, GETDATE());
GO

-- ==========================================
-- 3) INSERT BOOKINGS
--    BookingID auto-starts at 1
--    (EquipmentID, RenterID map to the IDs above)
-- ==========================================
INSERT INTO Bookings (EquipmentID, RenterID, StartDate, EndDate, TotalCost, BookingStatus, CreatedAt) VALUES
(1, 2, DATEADD(DAY, 1, GETDATE()), DATEADD(DAY, 2, GETDATE()), 4000, 'Pending',   GETDATE()),
(2, 3, DATEADD(DAY, 2, GETDATE()), DATEADD(DAY, 3, GETDATE()), 8000, 'Approved',  GETDATE()),
(3, 4, DATEADD(DAY, 3, GETDATE()), DATEADD(DAY, 4, GETDATE()), 1200, 'Pending',   GETDATE()),
(4, 5, DATEADD(DAY, 2, GETDATE()), DATEADD(DAY, 3, GETDATE()), 5500, 'Approved',  GETDATE()),
(5, 1, DATEADD(DAY, 4, GETDATE()), DATEADD(DAY, 5, GETDATE()), 6500, 'Pending',   GETDATE());
GO

-- ==========================================
-- VERIFY THE DATA
-- ==========================================
PRINT '================ USERS ================';
SELECT UserID, FullName, Email, PhoneNumber, VillageName FROM Users;

PRINT '================ EQUIPMENT ================';
SELECT EquipmentID, Title, Category, HourlyRate, DailyRate, OwnerID, IsAvailable FROM Equipment;

PRINT '================ BOOKINGS ================';
SELECT BookingID, EquipmentID, RenterID, StartDate, EndDate, TotalCost, BookingStatus FROM Bookings;
GO

