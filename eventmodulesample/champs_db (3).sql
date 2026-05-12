-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1
-- Generation Time: May 12, 2026 at 08:48 AM
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
-- Database: `champs_db`
--

-- --------------------------------------------------------

--
-- Table structure for table `attendance`
--

CREATE TABLE `attendance` (
  `attendance_id` int(11) NOT NULL,
  `event_id` int(11) DEFAULT NULL,
  `attendance_status` varchar(50) NOT NULL DEFAULT 'Present',
  `check_in_time` datetime NOT NULL DEFAULT current_timestamp(),
  `member_id` int(11) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `attendance`
--

INSERT INTO `attendance` (`attendance_id`, `event_id`, `attendance_status`, `check_in_time`, `member_id`) VALUES
(1, 5, 'Present', '2026-05-12 05:10:40', 1),
(2, 5, 'Late', '2026-05-12 05:13:33', 6),
(3, 4, 'Present', '2026-05-12 05:18:51', 12),
(4, 4, 'Late', '2026-05-12 05:18:54', 9),
(5, 4, 'Absent', '2026-05-12 05:19:01', 8),
(6, 4, 'Present', '2026-05-12 05:19:06', 2),
(7, 4, 'Present', '2026-05-12 05:20:23', 1),
(8, 5, 'Present', '2026-05-12 06:00:07', 13),
(9, 5, 'Present', '2026-05-12 06:00:08', 4),
(10, 5, 'Present', '2026-05-12 06:00:10', 12),
(11, 5, 'Present', '2026-05-12 06:00:11', 8),
(12, 5, 'Present', '2026-05-12 06:00:13', 17),
(13, 5, 'Present', '2026-05-12 06:00:14', 9),
(14, 5, 'Present', '2026-05-12 06:00:16', 14),
(15, 5, 'Present', '2026-05-12 06:00:17', 11),
(16, 5, 'Present', '2026-05-12 06:00:19', 3),
(17, 5, 'Present', '2026-05-12 06:00:22', 15),
(18, 5, 'Present', '2026-05-12 06:00:23', 7),
(19, 5, 'Present', '2026-05-12 06:00:26', 2),
(20, 7, 'Present', '2026-05-12 06:05:24', 13),
(21, 7, 'Present', '2026-05-12 06:05:26', 8),
(22, 7, 'Present', '2026-05-12 06:05:27', 11),
(23, 7, 'Present', '2026-05-12 06:05:29', 14),
(24, 4, 'Absent', '2026-05-12 06:05:50', 14),
(25, 4, 'Absent', '2026-05-12 06:05:53', 3),
(26, 4, 'Absent', '2026-05-12 06:05:55', 15),
(27, 4, 'Absent', '2026-05-12 06:05:59', 7),
(28, 4, 'Absent', '2026-05-12 06:06:01', 11),
(29, 4, 'Absent', '2026-05-12 06:06:04', 13),
(30, 4, 'Absent', '2026-05-12 06:06:06', 6),
(31, 8, 'Absent', '2026-05-12 06:07:09', 2),
(32, 8, 'Absent', '2026-05-12 06:07:11', 7),
(33, 8, 'Late', '2026-05-12 06:07:14', 1),
(34, 8, 'Absent', '2026-05-12 06:07:16', 11),
(35, 8, 'Absent', '2026-05-12 06:07:19', 3),
(36, 8, 'Absent', '2026-05-12 06:07:21', 14),
(37, 8, 'Absent', '2026-05-12 06:07:23', 9),
(38, 8, 'Absent', '2026-05-12 06:07:25', 6),
(39, 8, 'Absent', '2026-05-12 06:07:27', 8),
(40, 8, 'Absent', '2026-05-12 06:07:29', 15),
(41, 8, 'Absent', '2026-05-12 06:07:32', 4),
(42, 8, 'Absent', '2026-05-12 06:07:35', 13),
(43, 9, 'Absent', '2026-05-12 06:11:02', 1),
(44, 9, 'Absent', '2026-05-12 06:11:05', 11),
(45, 9, 'Absent', '2026-05-12 06:11:08', 2),
(46, 9, 'Absent', '2026-05-12 06:11:11', 15),
(47, 9, 'Absent', '2026-05-12 06:11:13', 9),
(48, 9, 'Present', '2026-05-12 06:11:15', 8);

-- --------------------------------------------------------

--
-- Table structure for table `events`
--

CREATE TABLE `events` (
  `event_id` int(11) NOT NULL,
  `event_name` varchar(255) DEFAULT NULL,
  `event_type` varchar(100) DEFAULT NULL,
  `description` text DEFAULT NULL,
  `location` varchar(255) DEFAULT NULL,
  `event_date` date DEFAULT NULL,
  `start_time` time DEFAULT NULL,
  `end_time` time DEFAULT NULL,
  `expected_attendance` int(11) DEFAULT NULL,
  `status` varchar(50) DEFAULT NULL,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `events`
--

INSERT INTO `events` (`event_id`, `event_name`, `event_type`, `description`, `location`, `event_date`, `start_time`, `end_time`, `expected_attendance`, `status`, `created_at`) VALUES
(4, 'Saturday Breakfast for the Professionals', 'Saturday Breakfast', 'for the professionals of BCBO', 'BCBP LIPA CHAPTER', '2026-05-15', '08:00:00', '09:00:00', 80, 'Finished', '2026-05-11 19:12:32'),
(5, 'test after update', 'Saturday Breakfast', 'test', 'lipa batangas', '2026-05-30', '06:40:00', '07:40:00', 80, 'Finished', '2026-05-11 20:41:02'),
(6, 'EASTER EGG HUNT', 'Friday Action Group Leader', 'egg', 'lipa batangas', '2026-05-01', '09:10:00', '17:00:00', 100, 'Finished', '2026-05-11 22:04:09'),
(7, 'FISHING FRIDAY', 'Friday Action Group Leader', 'fish', 'lipa batangas', '2026-05-30', '09:00:00', '17:00:00', 50, 'Finished', '2026-05-11 22:05:11'),
(8, 'test 2', 'Saturday Breakfast', 'test', 'lipa batangas', '2026-05-12', '02:06:00', '14:06:00', 50, 'Finished', '2026-05-11 22:06:51'),
(9, 'test 3', 'Friday Action Group Leader', 'test', 'lipa batangas', '2026-05-12', '02:10:00', '14:10:00', 50, 'Finished', '2026-05-11 22:10:51');

-- --------------------------------------------------------

--
-- Table structure for table `members`
--

CREATE TABLE `members` (
  `member_id` int(11) NOT NULL,
  `first_name` varchar(100) NOT NULL,
  `last_name` varchar(100) NOT NULL,
  `email` varchar(255) DEFAULT NULL,
  `phone` varchar(30) DEFAULT NULL,
  `role` varchar(100) DEFAULT NULL,
  `position` varchar(100) DEFAULT NULL,
  `status` varchar(50) NOT NULL DEFAULT 'Active',
  `created_at` datetime NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `members`
--

INSERT INTO `members` (`member_id`, `first_name`, `last_name`, `email`, `phone`, `role`, `position`, `status`, `created_at`) VALUES
(1, 'Josh', 'Sianquita', 'siankeets@gmail.com', '09151045628', 'Member', 'N/A', 'Active', '2026-05-12 05:09:58'),
(2, 'Allister', 'Villanueva', 'allister@gmail.com', '09123456789', 'Staff', 'Director', 'Active', '2026-05-12 05:11:31'),
(3, 'Mark', 'Reyes', 'mark.reyes@gmail.com', '09171234561', 'Member', 'N/A', 'Active', '2026-05-12 13:12:49'),
(4, 'Angela', 'Cruz', 'angela.cruz@gmail.com', '09171234562', 'Member', 'N/A', 'Active', '2026-05-12 13:12:49'),
(5, 'Daniel', 'Santos', 'daniel.santos@gmail.com', '09171234563', 'Member', 'N/A', 'Inactive', '2026-05-12 13:12:49'),
(6, 'Patricia', 'Garcia', 'patricia.garcia@gmail.com', '09171234564', 'Staff', 'Coordinator', 'Active', '2026-05-12 13:12:49'),
(7, 'Kevin', 'Torres', 'kevin.torres@gmail.com', '09171234565', 'Member', 'N/A', 'Active', '2026-05-12 13:12:49'),
(8, 'Samantha', 'Flores', 'samantha.flores@gmail.com', '09171234566', 'Staff', 'Secretary', 'Active', '2026-05-12 13:12:49'),
(9, 'Joshua', 'Mendoza', 'joshua.mendoza@gmail.com', '09171234567', 'Member', 'N/A', 'Active', '2026-05-12 13:12:49'),
(10, 'Nicole', 'Aquino', 'nicole.aquino@gmail.com', '09171234568', 'Member', 'N/A', 'Inactive', '2026-05-12 13:12:49'),
(11, 'Carlo', 'Navarro', 'carlo.navarro@gmail.com', '09171234569', 'Staff', 'Treasurer', 'Active', '2026-05-12 13:12:49'),
(12, 'Bianca', 'Fernandez', 'bianca.fernandez@gmail.com', '09171234570', 'Member', 'N/A', 'Active', '2026-05-12 13:12:49'),
(13, 'Ethan', 'Castillo', 'ethan.castillo@gmail.com', '09171234571', 'Member', 'N/A', 'Active', '2026-05-12 13:12:49'),
(14, 'Rica', 'Morales', 'rica.morales@gmail.com', '09171234572', 'Staff', 'Assistant Director', 'Active', '2026-05-12 13:12:49'),
(15, 'Nathan', 'Perez', 'nathan.perez@gmail.com', '09171234573', 'Member', 'N/A', 'Active', '2026-05-12 13:12:49'),
(16, 'Claire', 'Ramos', 'claire.ramos@gmail.com', '09171234574', 'Member', 'N/A', 'Inactive', '2026-05-12 13:12:49'),
(17, 'Vincent', 'Lopez', 'vincent.lopez@gmail.com', '09171234575', 'Staff', 'Facilitator', 'Active', '2026-05-12 13:12:49'),
(18, 'Ramon', 'Dela Cruz', 'ramon.delacruz@gmail.com', '09171000018', 'Member', 'N/A', 'Active', '2026-01-05 08:00:00'),
(19, 'Lourdes', 'Bautista', 'lourdes.bautista@gmail.com', '09171000019', 'Staff', 'Program Coordinator', 'Active', '2026-01-05 08:01:00'),
(20, 'Reynaldo', 'Santiago', 'reynaldo.santiago@gmail.com', '09171000020', 'Member', 'N/A', 'Active', '2026-01-05 08:02:00'),
(21, 'Maricel', 'Reyes', 'maricel.reyes@gmail.com', '09171000021', 'Core Team', 'Prayer Leader', 'Active', '2026-01-05 08:03:00'),
(22, 'Alfredo', 'Ocampo', 'alfredo.ocampo@gmail.com', '09171000022', 'Member', 'N/A', 'Inactive', '2026-01-05 08:04:00'),
(23, 'Teresita', 'Villanueva', 'tess.villanueva@gmail.com', '09171000023', 'Staff', 'Logistics Head', 'Active', '2026-01-05 08:05:00'),
(24, 'Ernesto', 'Gutierrez', 'ernesto.gutierrez@gmail.com', '09171000024', 'Member', 'N/A', 'Active', '2026-01-05 08:06:00'),
(25, 'Carmela', 'Hernandez', 'carmela.hernandez@gmail.com', '09171000025', 'Volunteer', 'N/A', 'Active', '2026-01-05 08:07:00'),
(26, 'Danilo', 'Pascual', 'danilo.pascual@gmail.com', '09171000026', 'Member', 'N/A', 'Active', '2026-01-05 08:08:00'),
(27, 'Florencia', 'Aguilar', 'flo.aguilar@gmail.com', '09171000027', 'Core Team', 'Communications', 'Active', '2026-01-05 08:09:00'),
(28, 'Roberto', 'Macaraeg', 'roberto.macaraeg@gmail.com', '09171000028', 'Member', 'N/A', 'Active', '2026-01-10 08:00:00'),
(29, 'Susana', 'Dela Torre', 'susana.delatorre@gmail.com', '09171000029', 'Staff', 'Finance Assistant', 'Active', '2026-01-10 08:01:00'),
(30, 'Eduardo', 'Tolentino', 'eduardo.tolentino@gmail.com', '09171000030', 'Member', 'N/A', 'Inactive', '2026-01-10 08:02:00'),
(31, 'Rosario', 'Manalo', 'rosario.manalo@gmail.com', '09171000031', 'Core Team', 'Music Ministry', 'Active', '2026-01-10 08:03:00'),
(32, 'Gregorio', 'Soriano', 'greg.soriano@gmail.com', '09171000032', 'Member', 'N/A', 'Active', '2026-01-10 08:04:00'),
(33, 'Milagros', 'Cabrera', 'milagros.cabrera@gmail.com', '09171000033', 'Volunteer', 'N/A', 'Active', '2026-01-10 08:05:00'),
(34, 'Rogelio', 'Dimaculangan', 'rogelio.dima@gmail.com', '09171000034', 'Member', 'N/A', 'Active', '2026-01-10 08:06:00'),
(35, 'Norma', 'Espiritu', 'norma.espiritu@gmail.com', '09171000035', 'Staff', 'Secretary', 'Active', '2026-01-10 08:07:00'),
(36, 'Wilfredo', 'Alcantara', 'wil.alcantara@gmail.com', '09171000036', 'Member', 'N/A', 'Inactive', '2026-01-10 08:08:00'),
(37, 'Consuelo', 'Buenaventura', 'consuelo.bv@gmail.com', '09171000037', 'Core Team', 'Hospitality', 'Active', '2026-01-10 08:09:00'),
(38, 'Arsenio', 'Pineda', 'arsenio.pineda@gmail.com', '09171000038', 'Member', 'N/A', 'Active', '2026-01-15 08:00:00'),
(39, 'Remedios', 'Valdez', 'rem.valdez@gmail.com', '09171000039', 'Volunteer', 'N/A', 'Active', '2026-01-15 08:01:00'),
(40, 'Benedicto', 'Pangilinan', 'ben.pangilinan@gmail.com', '09171000040', 'Member', 'N/A', 'Active', '2026-01-15 08:02:00'),
(41, 'Adoracion', 'Medina', 'adora.medina@gmail.com', '09171000041', 'Staff', 'Outreach Lead', 'Active', '2026-01-15 08:03:00'),
(42, 'Marcelino', 'Tabios', 'marcelino.tabios@gmail.com', '09171000042', 'Member', 'N/A', 'Inactive', '2026-01-15 08:04:00'),
(43, 'Perpetua', 'Corpus', 'perp.corpus@gmail.com', '09171000043', 'Core Team', 'Discipleship', 'Active', '2026-01-15 08:05:00'),
(44, 'Teodoro', 'Constantino', 'teo.constantino@gmail.com', '09171000044', 'Member', 'N/A', 'Active', '2026-01-15 08:06:00'),
(45, 'Felicitas', 'Umali', 'feli.umali@gmail.com', '09171000045', 'Volunteer', 'N/A', 'Active', '2026-01-15 08:07:00'),
(46, 'Simplicio', 'Eugenio', 'sim.eugenio@gmail.com', '09171000046', 'Member', 'N/A', 'Active', '2026-01-15 08:08:00'),
(47, 'Ligaya', 'Crisostomo', 'ligaya.criso@gmail.com', '09171000047', 'Staff', 'Records Officer', 'Active', '2026-01-15 08:09:00'),
(48, 'Herminio', 'Ilagan', 'herminio.ilagan@gmail.com', '09171000048', 'Member', 'N/A', 'Active', '2026-01-20 08:00:00'),
(49, 'Visitacion', 'Tanedo', 'visita.tanedo@gmail.com', '09171000049', 'Core Team', 'Intercessory', 'Active', '2026-01-20 08:01:00'),
(50, 'Procopio', 'Abelardo', 'proc.abelardo@gmail.com', '09171000050', 'Member', 'N/A', 'Inactive', '2026-01-20 08:02:00'),
(51, 'Anunciacion', 'Manaloto', 'annun.manaloto@gmail.com', '09171000051', 'Volunteer', 'N/A', 'Active', '2026-01-20 08:03:00'),
(52, 'Crisanto', 'Evangelista', 'cris.evangelista@gmail.com', '09171000052', 'Member', 'N/A', 'Active', '2026-01-20 08:04:00'),
(53, 'Purificacion', 'Dizon', 'puri.dizon@gmail.com', '09171000053', 'Staff', 'Treasurer Assistant', 'Active', '2026-01-20 08:05:00'),
(54, 'Emiliano', 'Lacson', 'emil.lacson@gmail.com', '09171000054', 'Member', 'N/A', 'Active', '2026-01-20 08:06:00'),
(55, 'Resurreccion', 'Tuason', 'resu.tuason@gmail.com', '09171000055', 'Core Team', 'Youth Ministry', 'Active', '2026-01-20 08:07:00'),
(56, 'Macario', 'Natividad', 'macario.natividad@gmail.com', '09171000056', 'Member', 'N/A', 'Inactive', '2026-01-20 08:08:00'),
(57, 'Presentacion', 'Tiongson', 'pres.tiongson@gmail.com', '09171000057', 'Volunteer', 'N/A', 'Active', '2026-01-20 08:09:00'),
(58, 'Abundio', 'Sarmiento', 'abun.sarmiento@gmail.com', '09171000058', 'Member', 'N/A', 'Active', '2026-02-01 08:00:00'),
(59, 'Consolacion', 'Agcaoili', 'conso.agcaoili@gmail.com', '09171000059', 'Staff', 'Events Coordinator', 'Active', '2026-02-01 08:01:00'),
(60, 'Tranquilino', 'Mercado', 'tranq.mercado@gmail.com', '09171000060', 'Member', 'N/A', 'Active', '2026-02-01 08:02:00'),
(61, 'Felipa', 'Batungbakal', 'felipa.batung@gmail.com', '09171000061', 'Core Team', 'Social Action', 'Active', '2026-02-01 08:03:00'),
(62, 'Isidoro', 'Bacani', 'isidoro.bacani@gmail.com', '09171000062', 'Member', 'N/A', 'Inactive', '2026-02-01 08:04:00'),
(63, 'Esperanza', 'Bulatao', 'espe.bulatao@gmail.com', '09171000063', 'Volunteer', 'N/A', 'Active', '2026-02-01 08:05:00'),
(64, 'Dominador', 'Caguioa', 'dom.caguioa@gmail.com', '09171000064', 'Member', 'N/A', 'Active', '2026-02-01 08:06:00'),
(65, 'Serafina', 'Delos Reyes', 'sera.delosreyes@gmail.com', '09171000065', 'Staff', 'Facilitator', 'Active', '2026-02-01 08:07:00'),
(66, 'Eustaquio', 'Fonacier', 'eusta.fonacier@gmail.com', '09171000066', 'Member', 'N/A', 'Active', '2026-02-01 08:08:00'),
(67, 'Asuncion', 'Gatdula', 'asun.gatdula@gmail.com', '09171000067', 'Core Team', 'Worship', 'Active', '2026-02-01 08:09:00'),
(68, 'Fulgencio', 'Hilario', 'fulgen.hilario@gmail.com', '09171000068', 'Member', 'N/A', 'Active', '2026-02-10 08:00:00'),
(69, 'Salome', 'Ilustre', 'salome.ilustre@gmail.com', '09171000069', 'Volunteer', 'N/A', 'Active', '2026-02-10 08:01:00'),
(70, 'Custodio', 'Jacinto', 'custo.jacinto@gmail.com', '09171000070', 'Member', 'N/A', 'Inactive', '2026-02-10 08:02:00'),
(71, 'Brigida', 'Katigbak', 'brigida.katigbak@gmail.com', '09171000071', 'Staff', 'Membership Officer', 'Active', '2026-02-10 08:03:00'),
(72, 'Anastacio', 'Lacanlale', 'anas.lacanlale@gmail.com', '09171000072', 'Member', 'N/A', 'Active', '2026-02-10 08:04:00'),
(73, 'Francisca', 'Mabanta', 'fran.mabanta@gmail.com', '09171000073', 'Core Team', 'Family Ministry', 'Active', '2026-02-10 08:05:00'),
(74, 'Honorato', 'Narciso', 'honor.narciso@gmail.com', '09171000074', 'Member', 'N/A', 'Active', '2026-02-10 08:06:00'),
(75, 'Liberata', 'Obnamia', 'liber.obnamia@gmail.com', '09171000075', 'Volunteer', 'N/A', 'Active', '2026-02-10 08:07:00'),
(76, 'Saturnino', 'Paterno', 'satur.paterno@gmail.com', '09171000076', 'Member', 'N/A', 'Inactive', '2026-02-10 08:08:00'),
(77, 'Vicenta', 'Quiambao', 'vice.quiambao@gmail.com', '09171000077', 'Staff', 'Assistant Secretary', 'Active', '2026-02-10 08:09:00'),
(78, 'Leoncio', 'Recto', 'leon.recto@gmail.com', '09171000078', 'Member', 'N/A', 'Active', '2026-02-15 08:00:00'),
(79, 'Encarnacion', 'Salazar', 'encar.salazar@gmail.com', '09171000079', 'Core Team', 'Formation', 'Active', '2026-02-15 08:01:00'),
(80, 'Porfirio', 'Tanjuatco', 'porf.tanjuatco@gmail.com', '09171000080', 'Member', 'N/A', 'Active', '2026-02-15 08:02:00'),
(81, 'Felicidad', 'Umandal', 'felicidad.u@gmail.com', '09171000081', 'Volunteer', 'N/A', 'Active', '2026-02-15 08:03:00'),
(82, 'Celestino', 'Velez', 'celes.velez@gmail.com', '09171000082', 'Member', 'N/A', 'Inactive', '2026-02-15 08:04:00'),
(83, 'Catalina', 'Yaptinchay', 'cata.yapt@gmail.com', '09171000083', 'Staff', 'Protocol Officer', 'Active', '2026-02-15 08:05:00'),
(84, 'Apolinario', 'Zabala', 'apol.zabala@gmail.com', '09171000084', 'Member', 'N/A', 'Active', '2026-02-15 08:06:00'),
(85, 'Perpetuo', 'Adriano', 'perp.adriano@gmail.com', '09171000085', 'Core Team', 'Stewardship', 'Active', '2026-02-15 08:07:00'),
(86, 'Maximo', 'Bernardo', 'maximo.bernardo@gmail.com', '09171000086', 'Member', 'N/A', 'Active', '2026-02-15 08:08:00'),
(87, 'Presentacion', 'Castelo', 'pres.castelo@gmail.com', '09171000087', 'Volunteer', 'N/A', 'Inactive', '2026-02-15 08:09:00'),
(88, 'Exequiel', 'Dayrit', 'exe.dayrit@gmail.com', '09171000088', 'Member', 'N/A', 'Active', '2026-03-01 08:00:00'),
(89, 'Hilaria', 'Escueta', 'hilaria.escueta@gmail.com', '09171000089', 'Staff', 'Chaplaincy Support', 'Active', '2026-03-01 08:01:00'),
(90, 'Bonifacio', 'Flores', 'bonif.flores@gmail.com', '09171000090', 'Member', 'N/A', 'Active', '2026-03-01 08:02:00'),
(91, 'Dolores', 'Generoso', 'dolor.generoso@gmail.com', '09171000091', 'Core Team', 'Prayer Coordinator', 'Active', '2026-03-01 08:03:00'),
(92, 'Venancio', 'Hernando', 'venan.hernando@gmail.com', '09171000092', 'Member', 'N/A', 'Inactive', '2026-03-01 08:04:00'),
(93, 'Rosalinda', 'Iniguez', 'rosa.iniguez@gmail.com', '09171000093', 'Volunteer', 'N/A', 'Active', '2026-03-01 08:05:00'),
(94, 'Metodio', 'Javier', 'meto.javier@gmail.com', '09171000094', 'Member', 'N/A', 'Active', '2026-03-01 08:06:00'),
(95, 'Visitacion', 'Kanapi', 'visita.kanapi@gmail.com', '09171000095', 'Staff', 'Welcoming Ministry', 'Active', '2026-03-01 08:07:00'),
(96, 'Melchor', 'Luna', 'melchor.luna@gmail.com', '09171000096', 'Member', 'N/A', 'Active', '2026-03-01 08:08:00'),
(97, 'Caridad', 'Mallari', 'cari.mallari@gmail.com', '09171000097', 'Core Team', 'Evangelism', 'Active', '2026-03-01 08:09:00'),
(98, 'Rufino', 'Navarrete', 'rufino.navarrete@gmail.com', '09171000098', 'Member', 'N/A', 'Active', '2026-03-10 08:00:00'),
(99, 'Amparo', 'Oco', 'amparo.oco@gmail.com', '09171000099', 'Volunteer', 'N/A', 'Active', '2026-03-10 08:01:00'),
(100, 'Calixto', 'Penalosa', 'cali.penalosa@gmail.com', '09171000100', 'Member', 'N/A', 'Inactive', '2026-03-10 08:02:00'),
(101, 'Concepcion', 'Quinto', 'conce.quinto@gmail.com', '09171000101', 'Staff', 'Media Ministry', 'Active', '2026-03-10 08:03:00'),
(102, 'Gaudencio', 'Robosa', 'gauden.robosa@gmail.com', '09171000102', 'Member', 'N/A', 'Active', '2026-03-10 08:04:00'),
(103, 'Illuminada', 'Sison', 'illum.sison@gmail.com', '09171000103', 'Core Team', 'Documentation', 'Active', '2026-03-10 08:05:00'),
(104, 'Florencio', 'Tabamo', 'floren.tabamo@gmail.com', '09171000104', 'Member', 'N/A', 'Active', '2026-03-10 08:06:00'),
(105, 'Basilisa', 'Urquico', 'basil.urquico@gmail.com', '09171000105', 'Volunteer', 'N/A', 'Active', '2026-03-10 08:07:00'),
(106, 'Clemente', 'Virata', 'clem.virata@gmail.com', '09171000106', 'Member', 'N/A', 'Inactive', '2026-03-10 08:08:00'),
(107, 'Felomina', 'Wycoco', 'felo.wycoco@gmail.com', '09171000107', 'Staff', 'Liaison Officer', 'Active', '2026-03-10 08:09:00'),
(108, 'Hilarion', 'Ycasiano', 'hilarion.ycasiano@gmail.com', '09171000108', 'Member', 'N/A', 'Active', '2026-03-15 08:00:00'),
(109, 'Nazaria', 'Zulueta', 'naza.zulueta@gmail.com', '09171000109', 'Core Team', 'Small Groups', 'Active', '2026-03-15 08:01:00'),
(110, 'Eladio', 'Abreu', 'eladio.abreu@gmail.com', '09171000110', 'Member', 'N/A', 'Active', '2026-03-15 08:02:00'),
(111, 'Marciana', 'Blas', 'marci.blas@gmail.com', '09171000111', 'Volunteer', 'N/A', 'Active', '2026-03-15 08:03:00'),
(112, 'Deogracias', 'Coronel', 'deo.coronel@gmail.com', '09171000112', 'Member', 'N/A', 'Inactive', '2026-03-15 08:04:00'),
(113, 'Presentacion', 'Dacumos', 'pres2.dacumos@gmail.com', '09171000113', 'Staff', 'Pastoral Support', 'Active', '2026-03-15 08:05:00'),
(114, 'Fructuoso', 'Estoesta', 'fruc.estoesta@gmail.com', '09171000114', 'Member', 'N/A', 'Active', '2026-03-15 08:06:00'),
(115, 'Genoveva', 'Ferrer', 'geno.ferrer@gmail.com', '09171000115', 'Core Team', 'Women Ministry', 'Active', '2026-03-15 08:07:00'),
(116, 'Heraclio', 'Gamboa', 'hera.gamboa@gmail.com', '09171000116', 'Member', 'N/A', 'Active', '2026-03-15 08:08:00'),
(117, 'Imelda', 'Hechanova', 'imelda.hechanova@gmail.com', '09171000117', 'Volunteer', 'N/A', 'Active', '2026-03-15 08:09:00');

--
-- Indexes for dumped tables
--

--
-- Indexes for table `attendance`
--
ALTER TABLE `attendance`
  ADD PRIMARY KEY (`attendance_id`),
  ADD KEY `event_id` (`event_id`);

--
-- Indexes for table `events`
--
ALTER TABLE `events`
  ADD PRIMARY KEY (`event_id`);

--
-- Indexes for table `members`
--
ALTER TABLE `members`
  ADD PRIMARY KEY (`member_id`);

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `attendance`
--
ALTER TABLE `attendance`
  MODIFY `attendance_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=49;

--
-- AUTO_INCREMENT for table `events`
--
ALTER TABLE `events`
  MODIFY `event_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=10;

--
-- AUTO_INCREMENT for table `members`
--
ALTER TABLE `members`
  MODIFY `member_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=118;

--
-- Constraints for dumped tables
--

--
-- Constraints for table `attendance`
--
ALTER TABLE `attendance`
  ADD CONSTRAINT `attendance_ibfk_1` FOREIGN KEY (`event_id`) REFERENCES `events` (`event_id`);
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
