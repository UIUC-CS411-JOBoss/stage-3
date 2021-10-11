DROP TABLE IF EXISTS `USER`;
DROP TABLE IF EXISTS `USER_PROFILE`;
DROP TABLE IF EXISTS `TAG`;
DROP TABLE IF EXISTS `USER_PREFERRED_TAG`;
DROP TABLE IF EXISTS `INTEREST`;
DROP TABLE IF EXISTS `COMPANY`;
DROP TABLE IF EXISTS `JOB`;
DROP TABLE IF EXISTS `JOB_STATUS`;
DROP TABLE IF EXISTS `JOB_TAG`;


CREATE TABLE `USER` (
  `id` INT PRIMARY KEY AUTO_INCREMENT,
  `email` VARCHAR(250) NOT NULL,
  `token` VARCHAR(250) NOT NULL ,
  `create_at` Datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `update_at` Datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);
 
CREATE TABLE `USER_PROFILE` (
  `user_id` INT PRIMARY KEY,
  `first_name` VARCHAR(250) NOT NULL,
  `last_name` VARCHAR(250) NOT NULL,
  `prefered_first_name` VARCHAR(250),
  `introduction` VARCHAR(2000),
  `email` VARCHAR(250),
  `phone` VARCHAR(20),
  `address` VARCHAR(250),
  `social_website` VARCHAR(250),
  `work_experiences` JSON,
  `resume` VARCHAR(2083),
  `cover_letter` VARCHAR(2083),
  `visa_required` bool,
  `create_at` Datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `update_at` Datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  FOREIGN KEY (`user_id`) REFERENCES `USER` (`id`)
);

CREATE TABLE `TAG` (
  `id` INT PRIMARY KEY AUTO_INCREMENT,
  `tag` VARCHAR(250) NOT NULL,
  `tag_type` ENUM ('skills', 'interview', 'others') NOT NULL,
  `create_at` Datetime NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE `USER_PREFERRED_TAG` (
  `user_id` INT NOT NULL,
  `tag_id` INT NOT NULL,
  `create_at` Datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `update_at` Datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`user_id`, `tag_id`),
  FOREIGN KEY (`user_id`) REFERENCES `USER` (`id`),
  FOREIGN KEY (`tag_id`) REFERENCES `TAG` (`id`)
);
 
CREATE TABLE `INTEREST` (
  `id` INT PRIMARY KEY AUTO_INCREMENT,
  `user_id` INT NOT NULL,
  `interest` ENUM ('front-end', 'back-end', 'full-stack', 'machine-learning', 'data-science', 'mobile-app') NOT NULL,
  `create_at` Datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `update_at` Datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  FOREIGN KEY (`user_id`) REFERENCES `USER` (`id`)
);
 
CREATE TABLE `COMPANY` (
  `id` INT PRIMARY KEY AUTO_INCREMENT,
  `name` VARCHAR(250) NOT NULL,
  `website` VARCHAR(2048) NOT NULL,
  `email` VARCHAR(2048),
  `phone` VARCHAR(20),
  `create_at` Datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `update_at` Datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);
 
CREATE TABLE `JOB` (
  `id` INT PRIMARY KEY AUTO_INCREMENT,
  `company_id` INT NOT NULL,
  `url` VARCHAR(2048) NOT NULL,
  `archived_url` VARCHAR(2048) NOT NULL,
  `active` Boolean NOT NULL,
  `location` VARCHAR(250),
  `type` ENUM ('internship', 'coop', 'full-time') NOT NULL,
  `title` VARCHAR(2048) NOT NULL,
  `description` TEXT NOT NULL,
  `accept_opt_cpt` ENUM ('yes', 'no', 'unknown') NOT NULL,
  `visa_sponsorship` ENUM ('yes', 'no', 'unknown') NOT NULL,
  `create_at` Datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `update_at` Datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  FOREIGN KEY (`company_id`) REFERENCES `COMPANY` (`id`)
);
 
CREATE TABLE `JOB_STATUS` (
  `id` int PRIMARY KEY AUTO_INCREMENT,
  `job_id` int NOT NULL,
  `user_id` int NOT NULL,
  `create_at` Datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `application_status` ENUM ('applied', 'OA', 'behavior interview', 'technical interview', 'rejected', 'offered') NOT NULL,
  FOREIGN KEY (`job_id`) REFERENCES `JOB` (`id`),
  FOREIGN KEY (`user_id`) REFERENCES `USER` (`id`)
);
 
CREATE TABLE `JOB_TAG` (
  `job_id` INT NOT NULL,
  `tag_id` INT NOT NULL,
  `create_at` Datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `update_at` Datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`job_id`, `tag_id`),
  FOREIGN KEY (`job_id`) REFERENCES `JOB` (`id`),
  FOREIGN KEY (`tag_id`) REFERENCES `TAG` (`id`)
);
