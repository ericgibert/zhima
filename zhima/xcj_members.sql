-- phpMyAdmin SQL Dump
-- version 4.7.8
-- https://www.phpmyadmin.net/
--
-- Host: localhost
-- Generation Time: Mar 18, 2018 at 02:31 AM
-- Server version: 10.2.13-MariaDB
-- PHP Version: 7.1.15

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
SET AUTOCOMMIT = 0;
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `xcj_members`
--

-- --------------------------------------------------------

--
-- Table structure for table `tb_log`
--

CREATE TABLE `tb_log` (
  `id` int(11) NOT NULL,
  `type` varchar(20) NOT NULL,
  `code` int(11) NOT NULL,
  `message` text NOT NULL,
  `created_on` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

--
-- Dumping data for table `tb_log`
--

INSERT INTO `tb_log` (`id`, `type`, `code`, `message`, `created_on`) VALUES
(1, 'INFO', 1, 'Testing log INSERT', '2018-01-28 07:58:19'),
(2, 'INFO', 1, 'Testing log INSERT', '2018-01-28 07:59:24'),
(3, 'NOT_OK', 55555, 'Not OK, please fix your status: NOT OK - QR V2', '2018-01-28 08:12:58'),
(4, 'NOT_OK', 55555, 'Not OK, please fix your status: NOT OK - QR V1', '2018-01-28 08:13:14'),
(5, 'OPEN', 123456, 'Welcome Eric Gibert - QR V1', '2018-01-28 08:13:18'),
(6, 'OPEN', 123456, 'Welcome Eric Gibert - QR V2', '2018-01-28 08:13:32'),
(7, 'OPEN', 123456, 'Welcome Eric Gibert - QR V2', '2018-01-28 08:17:59'),
(8, 'OPEN', 123456, 'Welcome Eric Gibert - QR V2', '2018-01-28 08:21:49'),
(9, 'OPEN', 123456, 'Welcome Eric Gibert - QR V2', '2018-01-28 08:22:56'),
(10, 'OPEN', 123456, 'Welcome Eric Gibert - QR V2', '2018-01-28 08:24:14'),
(11, 'OPEN', 123456, 'Welcome Eric Gibert - QR V2', '2018-01-28 08:25:04'),
(12, 'OPEN', 123456, 'Welcome Eric Gibert - QR V2', '2018-01-28 08:32:34'),
(13, 'WARNING', 2000, 'BLE communiction takes too long: kill the com', '2018-01-28 08:32:37'),
(14, 'ERROR', 2002, 'Connection to 50:8C:B1:69:A2:F1 by \'hci0\' failed: Device does not exist, check adapter name and MAC address.', '2018-01-28 08:32:37'),
(15, 'OPEN', 123456, 'Welcome Eric Gibert - QR V2', '2018-01-28 08:33:42'),
(16, 'ERROR', 2002, 'Connection to 50:8C:B1:69:A2:F1 by \'hci0\' failed: Device does not exist, check adapter name and MAC address.', '2018-01-28 08:33:45'),
(17, 'OPEN', 123456, 'Welcome Eric Gibert - QR V2', '2018-01-28 08:58:26'),
(18, 'ERROR', 2002, 'Connection to 50:8C:B1:69:A2:F1 by \'hci0\' failed: Device does not exist, check adapter name and MAC address.', '2018-01-28 08:58:29'),
(19, 'OPEN', 123456, 'Welcome Eric Gibert - QR V2', '2018-01-28 09:00:59'),
(20, 'ERROR', 2002, 'Connection to 50:8C:B1:69:A2:F1 by \'hci0\' failed: Device does not exist, check adapter name and MAC address.', '2018-01-28 09:01:02'),
(21, 'OPEN', 123456, 'Welcome Eric Gibert - QR V2', '2018-01-28 10:41:03'),
(22, 'ERROR', 2002, 'Connection to 50:8C:B1:69:A2:F1 by \'hci0\' failed: Device does not exist, check adapter name and MAC address.', '2018-01-28 10:41:07'),
(23, 'NOT_OK', 55555, 'Not OK, please fix your status: NOT OK - QR V2', '2018-01-28 10:41:48'),
(24, 'NOT_OK', 55555, 'Not OK, please fix your status: NOT OK - QR V2', '2018-01-28 10:42:43'),
(25, 'OPEN', 123456, 'Welcome Eric Gibert - QR V2', '2018-01-28 10:49:32'),
(26, 'ERROR', 2002, 'Connection to 50:8C:B1:69:A2:F1 by \'hci0\' failed: Device does not exist, check adapter name and MAC address.', '2018-01-28 10:49:35'),
(27, 'OPEN', 123456, 'Welcome Eric Gibert - QR V2', '2018-01-28 10:49:57'),
(28, 'ERROR', 2002, 'Connection to 50:8C:B1:69:A2:F1 by \'hci0\' failed: Device does not exist, check adapter name and MAC address.', '2018-01-28 10:50:00'),
(29, 'OPEN', 123456, 'Welcome Eric Gibert - QR V2', '2018-01-28 10:50:11'),
(30, 'ERROR', 2002, 'Connection to 50:8C:B1:69:A2:F1 by \'hci0\' failed: Device does not exist, check adapter name and MAC address.', '2018-01-28 10:50:14'),
(31, 'OPEN', 123456, 'Welcome Eric Gibert - QR V2', '2018-01-28 10:51:05'),
(32, 'ERROR', 2002, 'Connection to 50:8C:B1:69:A2:F1 by \'hci0\' failed: Device does not exist, check adapter name and MAC address.', '2018-01-28 10:51:08'),
(33, 'OPEN', 123456, 'Welcome Eric Gibert - QR V2', '2018-01-28 10:51:23'),
(34, 'ERROR', 2002, 'Connection to 50:8C:B1:69:A2:F1 by \'hci0\' failed: Device does not exist, check adapter name and MAC address.', '2018-01-28 10:51:26'),
(35, 'OPEN', 123456, 'Welcome Eric Gibert - QR V2', '2018-01-28 10:51:45'),
(36, 'ERROR', 2002, 'Connection to 50:8C:B1:69:A2:F1 by \'hci0\' failed: Device does not exist, check adapter name and MAC address.', '2018-01-28 10:51:48'),
(37, 'OPEN', 123456, 'Welcome Eric Gibert - QR V2', '2018-01-28 10:52:00'),
(38, 'ERROR', 2002, 'Connection to 50:8C:B1:69:A2:F1 by \'hci0\' failed: Device does not exist, check adapter name and MAC address.', '2018-01-28 10:52:03'),
(39, 'NOT_OK', 55555, 'Not OK, please fix your status: NOT OK - QR V2', '2018-01-28 10:52:13'),
(40, 'NOT_OK', 55555, 'Not OK, please fix your status: NOT OK - QR V1', '2018-01-28 10:52:17'),
(41, 'OPEN', 123456, 'Welcome Eric Gibert - QR V1', '2018-01-28 10:52:24'),
(42, 'ERROR', 2002, 'Connection to 50:8C:B1:69:A2:F1 by \'hci0\' failed: Device does not exist, check adapter name and MAC address.', '2018-01-28 10:52:27'),
(43, 'NOT_OK', 55555, 'Not OK, please fix your status: NOT OK - QR V2', '2018-01-28 10:53:25'),
(44, 'OPEN', 123456, 'Welcome Eric Gibert - QR V2', '2018-01-28 10:53:31'),
(45, 'ERROR', 2002, 'Connection to 50:8C:B1:69:A2:F1 by \'hci0\' failed: Device does not exist, check adapter name and MAC address.', '2018-01-28 10:53:34'),
(46, 'NOT_OK', 55555, 'Not OK, please fix your status: NOT OK - QR V1', '2018-01-28 10:53:39'),
(47, 'INFO', 1, 'Testing log INSERT', '2018-01-28 23:49:12'),
(48, 'INFO', 1, 'Testing log INSERT', '2018-01-29 23:36:16'),
(49, 'INFO', 1, 'Testing log INSERT', '2018-01-29 23:37:44'),
(50, 'INFO', 1, 'Testing log INSERT', '2018-01-29 23:38:11'),
(51, 'INFO', 1, 'Testing log INSERT', '2018-01-29 23:38:31'),
(52, 'INFO', 1, 'Testing log INSERT', '2018-01-29 23:39:05'),
(53, 'INFO', 1, 'Testing log INSERT', '2018-01-29 23:39:37'),
(54, 'INFO', 1, 'Testing log INSERT', '2018-01-29 23:43:05'),
(55, 'INFO', 1, 'Testing log INSERT', '2018-01-29 23:44:03'),
(56, 'INFO', 2, 'Testing log INSERT', '2018-01-29 23:45:44'),
(57, 'INFO', 2, 'Testing log INSERT', '2018-01-29 23:52:06'),
(58, 'INFO', 2, 'Testing log INSERT', '2018-01-29 23:52:45'),
(59, 'INFO', 2, 'Testing log INSERT', '2018-01-29 23:52:57'),
(60, 'INFO', 2, 'Testing log INSERT', '2018-01-29 23:53:15'),
(61, 'INFO', 2, 'Testing log INSERT', '2018-01-29 23:53:42'),
(62, 'INFO', 2, 'Testing log INSERT', '2018-01-29 23:53:52'),
(63, 'INFO', 2, 'Testing log INSERT', '2018-01-30 00:01:51'),
(64, 'INFO', 2, 'Testing log INSERT', '2018-01-30 00:03:43'),
(65, 'INFO', 2, 'Testing log INSERT', '2018-01-30 00:06:28'),
(66, 'INFO', 2, 'Testing log INSERT', '2018-02-01 00:09:09'),
(67, 'OPEN', 123456, 'Welcome Eric Gibert - QR V2', '2018-02-01 00:14:05'),
(68, 'ERROR', 2002, 'Connection to 50:8C:B1:69:A2:F1 by \'hci0\' failed: Device does not exist, check adapter name and MAC address.', '2018-02-01 00:14:08'),
(69, 'OPEN', 123456, 'Welcome Eric Gibert - QR V2', '2018-02-01 00:14:23'),
(70, 'ERROR', 2002, 'Connection to 50:8C:B1:69:A2:F1 by \'hci0\' failed: Device does not exist, check adapter name and MAC address.', '2018-02-01 00:14:27'),
(71, 'OPEN', 123456, 'Welcome Eric Gibert - QR V2', '2018-02-01 00:14:31'),
(72, 'ERROR', 2002, 'Connection to 50:8C:B1:69:A2:F1 by \'hci0\' failed: Device does not exist, check adapter name and MAC address.', '2018-02-01 00:14:34'),
(73, 'OPEN', 123456, 'Welcome Eric Gibert - QR V2', '2018-02-01 00:17:00'),
(74, 'WARNING', 2000, 'BLE communiction takes too long: kill the com', '2018-02-01 00:17:04'),
(75, 'OPEN', 123456, 'Welcome Eric Gibert - QR V2', '2018-02-01 00:19:12'),
(76, 'WARNING', 2000, 'BLE communiction takes too long: kill the com', '2018-02-01 00:19:16'),
(77, 'OPEN', 123456, 'Welcome Eric Gibert - QR V2', '2018-02-01 00:19:40'),
(78, 'ERROR', 2001, 'Connection to 50:8C:B1:69:A2:F1 failed. Try using \'hciconfig\' and \'hcitool\'', '2018-02-01 00:19:40'),
(79, 'WARNING', 2000, 'BLE communiction takes too long: kill the com', '2018-02-01 00:19:44'),
(80, 'ERROR', 2001, 'Connection to 50:8C:B1:69:A2:F1 failed. Try using \'hciconfig\' and \'hcitool\'', '2018-02-01 00:20:09'),
(81, 'WARNING', 3001, 'Photo not taken properly: \'Controller\' object has no attribute \'stop\'', '2018-02-04 01:58:43'),
(82, 'OPEN', 123456, 'Welcome Eric Gibert - QR V2', '2018-02-04 09:16:36'),
(83, 'ERROR', 2002, 'Connection to 50:8C:B1:69:A2:F1 by \'hci0\' failed: Device does not exist, check adapter name and MAC address.', '2018-02-04 09:16:39'),
(84, 'OPEN', 55555, 'Welcome Not OK - QR V2', '2018-02-04 09:16:57'),
(85, 'ERROR', 2002, 'Connection to 50:8C:B1:69:A2:F1 by \'hci0\' failed: Device does not exist, check adapter name and MAC address.', '2018-02-04 09:17:00'),
(86, 'OPEN', 55555, 'Welcome Not OK - QR V2', '2018-02-04 09:17:04'),
(87, 'ERROR', 2002, 'Connection to 50:8C:B1:69:A2:F1 by \'hci0\' failed: Device does not exist, check adapter name and MAC address.', '2018-02-04 09:17:07'),
(88, 'OPEN', 55555, 'Welcome Not OK - QR V2', '2018-02-04 09:17:11'),
(89, 'ERROR', 2002, 'Connection to 50:8C:B1:69:A2:F1 by \'hci0\' failed: Device does not exist, check adapter name and MAC address.', '2018-02-04 09:17:14'),
(90, 'OPEN', 55555, 'Welcome Not OK - QR V2', '2018-02-04 09:17:18'),
(91, 'ERROR', 2002, 'Connection to 50:8C:B1:69:A2:F1 by \'hci0\' failed: Device does not exist, check adapter name and MAC address.', '2018-02-04 09:17:21'),
(92, 'NOT_OK', 55555, 'Not OK, please fix your status: Not OK - QR V2', '2018-02-04 09:17:31'),
(93, 'NOT_OK', 55555, 'Not OK, please fix your status: Not OK - QR V2', '2018-02-04 09:26:53'),
(94, 'NOT_OK', 55555, 'Not OK, please fix your status: Not OK - QR V2', '2018-02-04 09:27:32'),
(95, 'NOT_OK', 55555, 'Not OK, please fix your status: Not OK - QR V2', '2018-02-04 09:27:42'),
(96, 'NOT_OK', 55555, 'Not OK, please fix your status: Not OK - QR V2', '2018-02-04 09:28:10'),
(97, 'NOT_OK', 55555, 'Not OK, please fix your status: Not OK - QR V2', '2018-02-04 09:28:28'),
(98, 'NOT_OK', 55555, 'Not OK, please fix your status: Not OK - QR V1', '2018-02-04 09:28:40'),
(99, 'OPEN', 123456, 'Welcome Eric Gibert - QR V1', '2018-02-04 09:28:45'),
(100, 'WARNING', 2000, 'BLE communiction takes too long: kill the com', '2018-02-04 09:28:49'),
(101, 'NOT_OK', 55555, 'Not OK, please fix your status: Not OK - QR V2', '2018-02-04 09:28:56'),
(102, 'ERROR', 2001, 'Connection to 50:8C:B1:69:A2:F1 failed. Try using \'hciconfig\' and \'hcitool\'', '2018-02-04 09:29:13'),
(103, 'OPEN', 123456, 'Welcome Eric Gibert - QR V2', '2018-02-04 09:29:41'),
(104, 'WARNING', 2000, 'BLE communiction takes too long: kill the com', '2018-02-04 09:29:45'),
(105, 'ERROR', 2001, 'Connection to 50:8C:B1:69:A2:F1 failed. Try using \'hciconfig\' and \'hcitool\'', '2018-02-04 09:30:09'),
(106, 'OPEN', 123456, 'Welcome Eric Gibert - QR V2', '2018-02-04 10:02:30'),
(107, 'ERROR', 2002, 'Connection to 50:8C:B1:69:A2:F1 by \'hci0\' failed: Device does not exist, check adapter name and MAC address.', '2018-02-04 10:02:33'),
(108, 'WARNING', 2000, 'BLE communiction takes too long: kill the com', '2018-02-04 10:02:34'),
(109, 'OPEN', 123456, 'Welcome Eric Gibert - QR V1', '2018-02-04 10:12:08'),
(110, 'WARNING', 2000, 'BLE communiction takes too long: kill the com', '2018-02-04 10:12:12'),
(111, 'ERROR', 2001, 'Connection to 50:8C:B1:69:A2:F1 failed. Try using \'hciconfig\' and \'hcitool\'', '2018-02-04 10:12:36'),
(112, 'OPEN', 123456, 'Welcome Eric Gibert - QR V2', '2018-02-04 10:15:46'),
(113, 'WARNING', 2000, 'BLE communiction takes too long: kill the com', '2018-02-04 10:15:51'),
(114, 'ERROR', 2001, 'Connection to 50:8C:B1:69:A2:F1 failed. Try using \'hciconfig\' and \'hcitool\'', '2018-02-04 10:16:15'),
(115, 'OPEN', 123456, 'Welcome Eric Gibert - QR V2', '2018-02-04 10:16:15'),
(116, 'WARNING', 2000, 'BLE communiction takes too long: kill the com', '2018-02-04 10:16:19'),
(117, 'ERROR', 2001, 'Connection to 50:8C:B1:69:A2:F1 failed. Try using \'hciconfig\' and \'hcitool\'', '2018-02-04 10:16:43'),
(118, 'NOT_OK', 55555, 'Not OK, please fix your status: Not OK - QR V2', '2018-02-04 10:18:03'),
(119, 'NOT_OK', 55555, 'Not OK, please fix your status: Not OK - QR V2', '2018-02-04 10:18:18'),
(120, 'OPEN', 123456, 'Welcome Eric Gibert - QR V2', '2018-02-04 10:18:31'),
(121, 'WARNING', 2000, 'BLE communiction takes too long: kill the com', '2018-02-04 10:18:35'),
(122, 'OPEN', 123456, 'Welcome Eric Gibert - QR V2', '2018-02-04 10:18:53'),
(123, 'ERROR', 2001, 'Connection to 50:8C:B1:69:A2:F1 failed. Try using \'hciconfig\' and \'hcitool\'', '2018-02-04 10:19:00'),
(124, 'WARNING', 2000, 'BLE communiction takes too long: kill the com', '2018-02-04 10:19:03'),
(125, 'ERROR', 2001, 'Connection to 50:8C:B1:69:A2:F1 failed. Try using \'hciconfig\' and \'hcitool\'', '2018-02-04 10:19:27'),
(126, 'OPEN', 123456, 'Welcome Eric Gibert - QR V2', '2018-02-04 10:20:54'),
(127, 'WARNING', 2000, 'BLE communiction takes too long: kill the com', '2018-02-04 10:21:24'),
(128, 'ERROR', 2001, 'Connection to 50:8C:B1:69:A2:F1 failed. Try using \'hciconfig\' and \'hcitool\'', '2018-02-04 10:21:48'),
(129, 'NOT_OK', 55555, 'Not OK, please fix your status: Not OK - QR V2', '2018-02-04 11:44:33'),
(130, 'NOT_OK', 55555, 'Not OK, please fix your status: Not OK - QR V1', '2018-02-04 11:44:43'),
(131, 'OPEN', 123456, 'Welcome Eric Gibert - QR V2', '2018-02-04 11:45:05'),
(132, 'WARNING', 2000, 'BLE communiction takes too long: kill the com', '2018-02-04 11:45:09'),
(133, 'ERROR', 2001, 'Connection to 50:8C:B1:69:A2:F1 failed. Try using \'hciconfig\' and \'hcitool\'', '2018-02-04 11:45:33'),
(134, 'OPEN', 1, 'Welcome admin - QR V2', '2018-03-04 11:32:17'),
(135, 'OPEN', 1, 'Welcome admin - QR V2', '2018-03-04 11:32:21'),
(136, 'OPEN', 1, 'Welcome admin - QR V2', '2018-03-04 11:32:24'),
(137, 'OPEN', 1, 'Welcome admin - QR V2', '2018-03-04 11:32:27'),
(138, 'OPEN', 1, 'Welcome admin - QR V2', '2018-03-04 11:32:35'),
(139, 'OPEN', 1, 'Welcome admin - QR V2', '2018-03-04 11:32:38'),
(140, 'OPEN', 123456, 'Welcome Eric Gibert - QR V2', '2018-03-04 11:32:46'),
(141, 'OPEN', 123456, 'Welcome Eric Gibert - QR V2', '2018-03-04 11:32:49'),
(142, 'OPEN', 123456, 'Welcome Eric Gibert - QR V2', '2018-03-04 11:32:52'),
(143, 'NOT_OK', 55555, 'Not OK, please fix your status: Not OK - QR V2', '2018-03-04 11:32:57'),
(144, 'NOT_OK', 55555, 'Not OK, please fix your status: Not OK - QR V2', '2018-03-04 11:33:14'),
(145, 'ERROR', 1000, 'Non XCJ QR Code or No member found for: None', '2018-03-08 13:00:31'),
(146, 'ERROR', 1000, 'Non XCJ QR Code or No member found for: None', '2018-03-08 13:00:34'),
(147, 'ERROR', 1000, 'Non XCJ QR Code or No member found for: None', '2018-03-08 13:00:38'),
(148, 'ERROR', 1000, 'Non XCJ QR Code or No member found for: None', '2018-03-08 13:00:41'),
(149, 'ERROR', 1000, 'Non XCJ QR Code or No member found for: None', '2018-03-08 13:00:44'),
(150, 'ERROR', 1000, 'Non XCJ QR Code or No member found for: None', '2018-03-08 13:00:47'),
(151, 'ERROR', 1000, 'Non XCJ QR Code or No member found for: None', '2018-03-08 13:00:51'),
(152, 'OPEN', 1, 'Welcome admin - QR V2', '2018-03-08 13:00:59'),
(153, 'OPEN', 123456, 'Welcome Eric Gibert - QR V1', '2018-03-08 13:01:06'),
(154, 'OPEN', 123456, 'Welcome Eric Gibert - QR V1', '2018-03-08 13:01:09'),
(155, 'OPEN', 123456, 'Welcome Eric Gibert - QR V2', '2018-03-08 13:01:23'),
(156, 'OPEN', 123456, 'Welcome Eric Gibert - QR V2', '2018-03-08 13:02:16'),
(157, 'OPEN', 123456, 'Welcome Eric Gibert - QR V2', '2018-03-08 13:02:19'),
(158, 'OPEN', 123456, 'Welcome Eric Gibert - QR V2', '2018-03-08 13:02:22'),
(159, 'OPEN', 123456, 'Welcome Eric Gibert - QR V2', '2018-03-08 13:03:11'),
(160, 'OPEN', 123456, 'Welcome Eric Gibert - QR V2', '2018-03-08 13:03:20'),
(161, 'OPEN', 123456, 'Welcome Eric Gibert - QR V2', '2018-03-08 13:03:23'),
(162, 'OPEN', 123456, 'Welcome Eric Gibert - QR V2', '2018-03-08 13:03:27'),
(163, 'INFO', 2, 'Testing log INSERT', '2018-03-10 02:42:51'),
(164, 'INFO', 2, 'Testing log INSERT', '2018-03-10 02:44:11'),
(165, 'INFO', 2, 'Testing log INSERT', '2018-03-10 02:44:15'),
(166, 'NOT_OK', 55555, 'Not OK, please fix your status: Not OK - QR V1', '2018-03-10 03:12:35'),
(167, 'NOT_OK', 55555, 'Not OK, please fix your status: Not OK - QR V1', '2018-03-10 03:13:32'),
(168, 'NOT_OK', 55555, 'Not OK, please fix your status: Not OK - QR V1', '2018-03-10 03:13:46'),
(169, 'NOT_OK', 55555, 'Not OK, please fix your status: Not OK - QR V1', '2018-03-10 03:14:08'),
(170, 'NOT_OK', 55555, 'Not OK, please fix your status: Not OK - QR V1', '2018-03-10 03:16:57'),
(171, 'NOT_OK', 55555, 'Not OK, please fix your status: Not OK - QR V1', '2018-03-10 03:17:23'),
(172, 'NOT_OK', 55555, 'Not OK, please fix your status: Not OK - QR V1', '2018-03-10 03:17:36'),
(173, 'NOT_OK', 55555, 'Not OK, please fix your status: Not OK - QR V1', '2018-03-10 03:17:55'),
(174, 'NOT_OK', 55555, 'Not OK, please fix your status: Not OK - QR V1', '2018-03-10 03:18:13'),
(175, 'NOT_OK', 55555, 'Not OK, please fix your status: Not OK - QR V1', '2018-03-10 03:18:32'),
(176, 'OPEN', 1, 'Welcome admin - QR V2', '2018-03-18 02:16:22'),
(177, 'OPEN', 1, 'Welcome admin - QR V2', '2018-03-18 02:16:26'),
(178, 'OPEN', 1, 'Welcome admin - QR V2', '2018-03-18 02:16:29');

-- --------------------------------------------------------

--
-- Table structure for table `transactions`
--

CREATE TABLE `transactions` (
  `id` int(11) NOT NULL,
  `member_id` int(11) NOT NULL,
  `type` varchar(20) NOT NULL,
  `description` text NOT NULL,
  `amount` float NOT NULL,
  `currency` varchar(4) NOT NULL,
  `valid_from` date NOT NULL,
  `valid_until` date NOT NULL,
  `created_on` datetime NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

--
-- Dumping data for table `transactions`
--

INSERT INTO `transactions` (`id`, `member_id`, `type`, `description`, `amount`, `currency`, `valid_from`, `valid_until`, `created_on`) VALUES
(1, 123456, '1M MEMBERSHIP', 'vvv', 10, 'CNY', '2018-02-03', '2018-03-06', '2018-02-03 18:38:53'),
(2, 123456, '1M MEMBERSHIP', 'vvv', 10, 'CNY', '2018-02-03', '2018-03-06', '2018-02-03 18:41:00'),
(3, 123456, '1M MEMBERSHIP', 'vvv', 10, 'CNY', '2018-02-03', '2018-03-06', '2018-02-03 18:42:23'),
(4, 123456, '1M MEMBERSHIP', 'vvv', 10, 'CNY', '2018-02-03', '2018-03-06', '2018-02-03 18:42:41'),
(5, 123456, '1M MEMBERSHIP', 'vvvxccc', 10, 'CNY', '2018-02-03', '2018-03-06', '2018-02-03 18:45:38'),
(6, 123456, '1M MEMBERSHIP', 'vvvxccc', 10, 'CNY', '2018-02-03', '2018-03-06', '2018-02-03 18:48:36'),
(7, 55555, '6M MEMBERSHIP', 'ccf', 0, 'CNY', '2018-02-03', '2018-03-06', '2018-02-03 18:49:07'),
(8, 55555, 'EVENT', 'ccf', 0, 'CNY', '2018-02-03', '2018-03-06', '2018-02-03 19:01:43'),
(9, 55555, 'TOOL', 'xxx', 0, 'CNY', '2018-02-03', '2018-03-06', '2018-02-03 19:04:39'),
(10, 55555, 'CROWD FUNDING', '', 0, 'CNY', '2018-02-04', '2018-03-07', '2018-02-04 16:49:36'),
(11, 55555, '6M MEMBERSHIP', '', 0, 'CNY', '2018-02-04', '2018-08-04', '2018-02-04 16:49:48'),
(12, 123456, '6M MEMBERSHIP', '', 830, 'CNY', '2018-02-04', '2018-08-04', '2018-02-04 17:08:23'),
(13, 123456, '1M MEMBERSHIP', '', 0, 'CNY', '2018-02-04', '2018-03-07', '2018-02-04 17:12:54'),
(14, 55555, '6M MEMBERSHIP', 'fffff', 0, 'CNY', '2018-02-04', '2018-08-04', '2018-02-04 17:13:29'),
(15, 123460, '6M MEMBERSHIP', '', 450, 'CNY', '2018-03-03', '2018-08-31', '2018-03-03 17:40:29'),
(17, 1, '1M MEMBERSHIP', '', 100, 'CNY', '2018-03-10', '2999-04-10', '2018-03-10 09:56:16');

-- --------------------------------------------------------

--
-- Table structure for table `users`
--

CREATE TABLE `users` (
  `id` int(11) NOT NULL,
  `openid` varchar(40) NOT NULL,
  `username` varchar(200) NOT NULL,
  `passwd` varchar(50) NOT NULL,
  `avatar_url` varchar(256) DEFAULT NULL,
  `email` varchar(128) DEFAULT NULL,
  `birthdate` date DEFAULT NULL,
  `status` varchar(20) DEFAULT NULL,
  `role` int(11) NOT NULL DEFAULT 0,
  `city` varchar(100) DEFAULT NULL,
  `province` varchar(100) DEFAULT NULL,
  `country` varchar(100) DEFAULT NULL,
  `gender` tinyint(4) NOT NULL DEFAULT 0 COMMENT '1: male, 2: female, 0:unknown',
  `language` varchar(5) DEFAULT NULL,
  `last_active_type` varchar(50) DEFAULT NULL,
  `last_active_time` datetime DEFAULT NULL,
  `create_time` datetime NOT NULL,
  `last_update` datetime NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

--
-- Dumping data for table `users`
--

INSERT INTO `users` (`id`, `openid`, `username`, `passwd`, `avatar_url`, `email`, `birthdate`, `status`, `role`, `city`, `province`, `country`, `gender`, `language`, `last_active_type`, `last_active_time`, `create_time`, `last_update`) VALUES
(1, '1', 'admin', '*AB127787E83A4553B0C08C2E06B6F046646AA6A9', '', '', '1967-12-01', 'OK', 5, '', '', '', 0, '', '[OPEN] Welcome admin - QR V2', '2018-03-18 10:16:29', '2018-03-14 22:24:37', '2018-03-14 22:24:37'),
(55555, '55555', 'not ok', '*ADCA6C445D26C70EE14C728DCCE437F09C54062D', '', '', '1967-12-01', 'Not OK', 0, '', '', '', 0, '', '', '2018-03-14 22:24:37', '2018-03-14 22:24:37', '2018-03-14 22:24:37'),
(123456, '123456', 'Eric Gibert', '*ADCA6C445D26C70EE14C728DCCE437F09C54062D', '', '', '1967-12-01', 'OK', 1, '', '', '', 0, '', '', '2018-03-14 22:24:37', '2018-03-14 22:24:37', '2018-03-14 22:24:37'),
(123457, '123457', 'Normal One', '*ADCA6C445D26C70EE14C728DCCE437F09C54062D', '', '', '2018-02-06', 'OK', 0, '', '', '', 0, '', '', '2018-03-14 22:24:37', '2018-03-14 22:24:37', '2018-03-14 22:24:37'),
(123458, '123458', 'eric2', '*ADCA6C445D26C70EE14C728DCCE437F09C54062D', '', '', '1967-12-01', 'OK', 0, '', '', '', 0, '', '', '2018-03-14 22:24:37', '2018-03-14 22:24:37', '2018-03-14 22:24:37'),
(123459, '123459', 'eric', '*ADCA6C445D26C70EE14C728DCCE437F09C54062D', '', '', '1967-12-01', 'OK', 0, '', '', '', 0, '', '', '2018-03-14 22:24:37', '2018-03-14 22:24:37', '2018-03-14 22:24:37'),
(123460, '123460', 'krapo', '*BB1962AFE30332EB0010129C20FA41019155ADAF', '', '', '1967-12-01', 'OK', 0, '', '', '', 0, '', '', '2018-03-14 22:24:37', '2018-03-14 22:24:37', '2018-03-14 22:24:37'),
(123461, '123461', 'www', '*19A4904A05D0ECDE0903BCF4B5072C531715E2E5', '', '', '1234-12-12', 'OK', 0, '', '', '', 0, '', '', '2018-03-14 22:24:37', '2018-03-14 22:24:37', '2018-03-14 22:24:37'),
(123462, '123462', 'ee', '*33E0B212CC71ADACB7017A3790B8D662986E504B', NULL, NULL, '1234-12-12', 'OK', 0, NULL, NULL, NULL, 0, NULL, NULL, NULL, '2018-03-17 16:33:55', '2018-03-17 16:33:55'),
(123464, '123464', 'eeee', '*7B844B41A3799185EBF33B603FA8C632E65CA3EF', NULL, '', '1234-12-12', 'OK', 1, NULL, NULL, NULL, 0, NULL, NULL, NULL, '2018-03-17 23:36:35', '2018-03-17 23:36:35');

--
-- Indexes for dumped tables
--

--
-- Indexes for table `tb_log`
--
ALTER TABLE `tb_log`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `transactions`
--
ALTER TABLE `transactions`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `users`
--
ALTER TABLE `users`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `openid` (`openid`),
  ADD UNIQUE KEY `username` (`username`);

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `tb_log`
--
ALTER TABLE `tb_log`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=179;

--
-- AUTO_INCREMENT for table `transactions`
--
ALTER TABLE `transactions`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=18;

--
-- AUTO_INCREMENT for table `users`
--
ALTER TABLE `users`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=123465;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
