-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1
-- Generation Time: May 23, 2025 at 12:01 AM
-- Server version: 10.4.32-MariaDB
-- PHP Version: 8.2.12

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `railway`
--

-- --------------------------------------------------------

--
-- Table structure for table `bookings`
--

CREATE TABLE `bookings` (
  `Train_No` int(11) NOT NULL,
  `Passenger_Name` varchar(30) NOT NULL,
  `Mobile_No` varchar(10) NOT NULL,
  `Passenger_Adhaar` varchar(12) NOT NULL,
  `Date_Of_Booking` varchar(20) NOT NULL,
  `Booking_ID` int(11) NOT NULL,
  `Class` varchar(20) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `bookings`
--

INSERT INTO `bookings` (`Train_No`, `Passenger_Name`, `Mobile_No`, `Passenger_Adhaar`, `Date_Of_Booking`, `Booking_ID`, `Class`) VALUES
(1, '1', '1111111111', '111111111111', '23-05-25', 2733, 'AC-1'),
(332, 'abhiraj', '9905174565', '123456789123', '23-05-25', 6967, 'AC-1');

-- --------------------------------------------------------

--
-- Table structure for table `train_info`
--

CREATE TABLE `train_info` (
  `Train_No` varchar(10) NOT NULL,
  `Station_Code` varchar(20) NOT NULL,
  `Station_Name` varchar(30) NOT NULL,
  `Arrival_Time` varchar(20) NOT NULL,
  `Departure_Time` varchar(20) NOT NULL,
  `Distance` varchar(10) NOT NULL,
  `Source_Station_Code` varchar(20) NOT NULL,
  `Source_Station_Name` varchar(70) NOT NULL,
  `Destination_Station_Code` varchar(20) NOT NULL,
  `Destination_Station_Name` varchar(60) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
