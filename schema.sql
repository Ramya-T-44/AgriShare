-- ==========================================
-- AgriShareDB - Database Schema
-- ==========================================
-- Run this script in SQL Server Management Studio (SSMS)
-- Requires: ODBC Driver 17 for SQL Server
-- ==========================================

IF DB_ID('AgriShareDB') IS NULL
BEGIN
    CREATE DATABASE AgriShareDB;
END
GO

USE AgriShareDB;
GO

-- ---------- Users Table ----------
IF OBJECT_ID('Users', 'U') IS NOT NULL DROP TABLE Users;
CREATE TABLE Users (
    UserID INT IDENTITY(1,1) PRIMARY KEY,
    FullName NVARCHAR(100) NOT NULL,
    Email NVARCHAR(150) NOT NULL UNIQUE,
    PasswordHash NVARCHAR(255) NOT NULL,
    PhoneNumber NVARCHAR(20),
    VillageName NVARCHAR(100),
    CreatedAt DATETIME DEFAULT GETDATE()
);

-- ---------- Equipment Table ----------
IF OBJECT_ID('Equipment', 'U') IS NOT NULL DROP TABLE Equipment;
CREATE TABLE Equipment (
    EquipmentID INT IDENTITY(1,1) PRIMARY KEY,
    Title NVARCHAR(150) NOT NULL,
    Category NVARCHAR(50) NOT NULL,
    HourlyRate DECIMAL(10,2) NOT NULL,
    DailyRate DECIMAL(10,2),
    OwnerID INT NOT NULL,
    IsAvailable BIT DEFAULT 1,
    CreatedAt DATETIME DEFAULT GETDATE(),
    CONSTRAINT FK_Equipment_Users FOREIGN KEY (OwnerID) REFERENCES Users(UserID)
);

-- ---------- Bookings Table ----------
IF OBJECT_ID('Bookings', 'U') IS NOT NULL DROP TABLE Bookings;
CREATE TABLE Bookings (
    BookingID INT IDENTITY(1,1) PRIMARY KEY,
    EquipmentID INT NOT NULL,
    RenterID INT NOT NULL,
    StartDate DATETIME NOT NULL,
    EndDate DATETIME NOT NULL,
    TotalCost DECIMAL(10,2) NOT NULL,
    BookingStatus NVARCHAR(20) DEFAULT 'Pending',
    CreatedAt DATETIME DEFAULT GETDATE(),
    CONSTRAINT FK_Bookings_Equipment FOREIGN KEY (EquipmentID) REFERENCES Equipment(EquipmentID),
    CONSTRAINT FK_Bookings_Renter FOREIGN KEY (RenterID) REFERENCES Users(UserID)
);

-- ---------- Indexes for faster lookups ----------
CREATE INDEX IX_Equipment_Owner ON Equipment(OwnerID);
CREATE INDEX IX_Equipment_Category ON Equipment(Category);
CREATE INDEX IX_Bookings_Renter ON Bookings(RenterID);
CREATE INDEX IX_Bookings_Equipment ON Bookings(EquipmentID);

PRINT '✅ AgriShareDB schema created successfully!';

