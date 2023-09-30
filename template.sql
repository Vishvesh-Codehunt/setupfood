-- phpMyAdmin SQL Dump
-- version 5.0.3
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1:3307
-- Generation Time: May 30, 2022 at 08:15 PM
-- Server version: 10.4.14-MariaDB
-- PHP Version: 7.4.27

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `template`
--

-- --------------------------------------------------------

--
-- Table structure for table `contacts`
--

CREATE TABLE `contacts` (
  `id` int(11) NOT NULL,
  `resta_id` int(11) DEFAULT NULL,
  `name` varchar(100) DEFAULT NULL,
  `mobile_number` varchar(12) DEFAULT NULL,
  `message` varchar(600) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- --------------------------------------------------------

--
-- Table structure for table `dishtype`
--

CREATE TABLE `dishtype` (
  `id` int(11) NOT NULL,
  `resta_id` int(11) DEFAULT NULL,
  `dish` varchar(50) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- --------------------------------------------------------

--
-- Table structure for table `feedbacks`
--

CREATE TABLE `feedbacks` (
  `id` int(11) NOT NULL,
  `resta_id` int(11) DEFAULT NULL,
  `name` varchar(100) DEFAULT NULL,
  `mobile_number` varchar(12) DEFAULT NULL,
  `experience` varchar(100) DEFAULT NULL,
  `message` varchar(400) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- --------------------------------------------------------

--
-- Table structure for table `final_orders`
--

CREATE TABLE `final_orders` (
  `id` int(11) NOT NULL,
  `resta_id` int(11) DEFAULT NULL,
  `customer_name` varchar(100) DEFAULT NULL,
  `mobile_number` varchar(12) DEFAULT NULL,
  `table_no` varchar(10) DEFAULT NULL,
  `type` varchar(30) DEFAULT NULL,
  `order_items` longtext DEFAULT NULL,
  `quantity` longtext DEFAULT NULL,
  `price` longtext DEFAULT NULL,
  `total_price` longtext DEFAULT NULL,
  `order_time` timestamp NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- --------------------------------------------------------

--
-- Table structure for table `menuitems`
--

CREATE TABLE `menuitems` (
  `id` int(11) NOT NULL,
  `dish_id` int(11) DEFAULT NULL,
  `items` longtext NOT NULL,
  `price` longtext DEFAULT NULL,
  `description` longtext DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- --------------------------------------------------------

--
-- Table structure for table `orders`
--

CREATE TABLE `orders` (
  `id` int(11) NOT NULL,
  `resta_id` int(11) DEFAULT NULL,
  `customer_name` varchar(100) DEFAULT NULL,
  `mobile_number` varchar(12) DEFAULT NULL,
  `table_no` varchar(10) DEFAULT NULL,
  `order_items` longtext DEFAULT NULL,
  `quantity` longtext DEFAULT NULL,
  `price` longtext DEFAULT NULL,
  `total_price` longtext DEFAULT NULL,
  `order_date` varchar(30) NOT NULL,
  `order_time` varchar(30) NOT NULL,
  `status` varchar(10) NOT NULL DEFAULT 'Accepted',
  `type` varchar(30) DEFAULT NULL,
  `takeaway_time` varchar(30) DEFAULT '-',
  `price_sum` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- --------------------------------------------------------

--
-- Table structure for table `tempcontact`
--

CREATE TABLE `tempcontact` (
  `contact_id` int(11) NOT NULL,
  `contact_user_id` int(11) DEFAULT NULL,
  `address` varchar(100) DEFAULT NULL,
  `mobile` varchar(12) DEFAULT NULL,
  `email` varchar(50) DEFAULT NULL,
  `map_link` varchar(600) DEFAULT NULL,
  `instagram_link` varchar(300) DEFAULT NULL,
  `facebook_link` varchar(300) DEFAULT NULL,
  `twitter_link` varchar(300) DEFAULT 'none',
  `wp_link` varchar(300) DEFAULT 'none'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- --------------------------------------------------------

--
-- Table structure for table `tempdetails`
--

CREATE TABLE `tempdetails` (
  `temp_id` int(11) NOT NULL,
  `userid` int(11) DEFAULT NULL,
  `resta_name` varchar(40) DEFAULT NULL,
  `tagline` varchar(80) DEFAULT NULL,
  `opening` varchar(10) DEFAULT NULL,
  `closing` varchar(10) DEFAULT NULL,
  `about` longtext DEFAULT NULL,
  `logo` varchar(100) DEFAULT NULL,
  `banner` varchar(100) DEFAULT NULL,
  `img1` varchar(100) DEFAULT NULL,
  `img2` varchar(100) DEFAULT NULL,
  `img3` varchar(100) DEFAULT NULL,
  `img4` varchar(100) DEFAULT NULL,
  `gst` varchar(10) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- --------------------------------------------------------

--
-- Table structure for table `users`
--

CREATE TABLE `users` (
  `user_id` int(11) NOT NULL,
  `email` varchar(50) DEFAULT NULL,
  `restaurant_name` varchar(60) DEFAULT NULL,
  `password` varchar(30) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

--
-- Indexes for dumped tables
--

--
-- Indexes for table `contacts`
--
ALTER TABLE `contacts`
  ADD PRIMARY KEY (`id`),
  ADD KEY `resta_id` (`resta_id`);

--
-- Indexes for table `dishtype`
--
ALTER TABLE `dishtype`
  ADD PRIMARY KEY (`id`),
  ADD KEY `resta_id` (`resta_id`);

--
-- Indexes for table `feedbacks`
--
ALTER TABLE `feedbacks`
  ADD PRIMARY KEY (`id`),
  ADD KEY `resta_id` (`resta_id`);

--
-- Indexes for table `final_orders`
--
ALTER TABLE `final_orders`
  ADD PRIMARY KEY (`id`),
  ADD KEY `resta_id` (`resta_id`);

--
-- Indexes for table `menuitems`
--
ALTER TABLE `menuitems`
  ADD PRIMARY KEY (`id`),
  ADD KEY `dish_id` (`dish_id`);

--
-- Indexes for table `orders`
--
ALTER TABLE `orders`
  ADD PRIMARY KEY (`id`),
  ADD KEY `resta_id` (`resta_id`);

--
-- Indexes for table `tempcontact`
--
ALTER TABLE `tempcontact`
  ADD PRIMARY KEY (`contact_id`),
  ADD KEY `contact_user_id` (`contact_user_id`);

--
-- Indexes for table `tempdetails`
--
ALTER TABLE `tempdetails`
  ADD PRIMARY KEY (`temp_id`),
  ADD KEY `userid` (`userid`);

--
-- Indexes for table `users`
--
ALTER TABLE `users`
  ADD PRIMARY KEY (`user_id`);

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `contacts`
--
ALTER TABLE `contacts`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `dishtype`
--
ALTER TABLE `dishtype`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `feedbacks`
--
ALTER TABLE `feedbacks`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `final_orders`
--
ALTER TABLE `final_orders`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `menuitems`
--
ALTER TABLE `menuitems`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `orders`
--
ALTER TABLE `orders`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `tempcontact`
--
ALTER TABLE `tempcontact`
  MODIFY `contact_id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `tempdetails`
--
ALTER TABLE `tempdetails`
  MODIFY `temp_id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `users`
--
ALTER TABLE `users`
  MODIFY `user_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=2;

--
-- Constraints for dumped tables
--

--
-- Constraints for table `contacts`
--
ALTER TABLE `contacts`
  ADD CONSTRAINT `contacts_ibfk_1` FOREIGN KEY (`resta_id`) REFERENCES `users` (`user_id`) ON DELETE CASCADE;

--
-- Constraints for table `dishtype`
--
ALTER TABLE `dishtype`
  ADD CONSTRAINT `dishtype_ibfk_1` FOREIGN KEY (`resta_id`) REFERENCES `tempcontact` (`contact_user_id`) ON DELETE CASCADE;

--
-- Constraints for table `feedbacks`
--
ALTER TABLE `feedbacks`
  ADD CONSTRAINT `feedbacks_ibfk_1` FOREIGN KEY (`resta_id`) REFERENCES `users` (`user_id`) ON DELETE CASCADE;

--
-- Constraints for table `final_orders`
--
ALTER TABLE `final_orders`
  ADD CONSTRAINT `final_orders_ibfk_1` FOREIGN KEY (`resta_id`) REFERENCES `users` (`user_id`) ON DELETE CASCADE;

--
-- Constraints for table `menuitems`
--
ALTER TABLE `menuitems`
  ADD CONSTRAINT `menuitems_ibfk_1` FOREIGN KEY (`dish_id`) REFERENCES `dishtype` (`id`) ON DELETE CASCADE;

--
-- Constraints for table `orders`
--
ALTER TABLE `orders`
  ADD CONSTRAINT `orders_ibfk_1` FOREIGN KEY (`resta_id`) REFERENCES `users` (`user_id`) ON DELETE CASCADE;

--
-- Constraints for table `tempcontact`
--
ALTER TABLE `tempcontact`
  ADD CONSTRAINT `tempcontact_ibfk_1` FOREIGN KEY (`contact_user_id`) REFERENCES `tempdetails` (`userid`) ON DELETE CASCADE;

--
-- Constraints for table `tempdetails`
--
ALTER TABLE `tempdetails`
  ADD CONSTRAINT `tempdetails_ibfk_1` FOREIGN KEY (`userid`) REFERENCES `users` (`user_id`) ON DELETE CASCADE;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
