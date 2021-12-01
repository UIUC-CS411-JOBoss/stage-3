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
  `reverse_email` VARCHAR(250) NOT NULL,
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
  `employer_industry_id` VARCHAR(250),
  `employer_logo_url` TEXT,
  `website` VARCHAR(2048),
  `email` VARCHAR(2048),
  `phone` VARCHAR(20),
  `create_at` Datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `update_at` Datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

CREATE TABLE `JOB` (
  `id` INT PRIMARY KEY AUTO_INCREMENT,
  `company_id` INT NOT NULL,
  `duration` VARCHAR(255),
  `job_type_id` INT,
  `job_type_name` VARCHAR(255),
  `location_cities` TEXT,
  `location_countries` TEXT,
  `location_states` TEXT,
  `location_names` TEXT,
  `salary_type_id` INT,
  `salary_type_name` VARCHAR(255),
  `text_description` TEXT,
  `title` VARCHAR(255),
  `remote` BOOLEAN,
  `cumulative_gpa_required` BOOLEAN,
  `cumulative_gpa` FLOAT,
  `located_in_us` BOOLEAN,
  `accepts_opt_cpt_candidates` BOOLEAN,
  `willing_to_sponsor_candidate` BOOLEAN,
  `graduation_date_minimum` DATE,
  `graduation_date_maximum` DATE,
  `work_auth_required` BOOLEAN,
  `school_year_or_graduation_date_required` BOOLEAN,
  `us_authorization_optional` BOOLEAN,
  `work_authorization_requirements` TEXT,
  `apply_start` DATETIME,
  `updated_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `expiration_date` DATETIME
);

CREATE TABLE `JOB_STATUS` (
  `id` int PRIMARY KEY AUTO_INCREMENT,
  `job_id` int NOT NULL,
  `user_id` int NOT NULL,
  `status_date` Datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `create_at` Datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `update_at` Datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
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

GRANT ALL PRIVILEGES ON joboss.* TO 'joboss'@'%';

DELIMITER $$
CREATE DEFINER=`root`@`%` PROCEDURE `recommend`(IN `my_job_id` INT, IN `my_user_id` INT)
BEGIN

  DECLARE cur CURSOR FOR 
    SELECT Y.job_id as job_id
    FROM (
      SELECT job_id, similar_factor
      FROM (SELECT js2.user_id as user_id, COUNT(*) as similar_factor
            FROM JOB_STATUS as js JOIN JOB_STATUS as js2 ON (js.job_id = js2.job_id AND js.user_id <> js2.user_id)
            WHERE js.user_id = my_user_id
            GROUP BY js2.user_id
            ORDER BY COUNT(*) DESC) as X 
            JOIN 
            JOB_STATUS as js ON X.user_id = js.user_id
      GROUP BY job_id, similar_factor
      ORDER BY similar_factor
    ) as Y JOIN JOB as j ON (Y.job_id = j.id) JOIN COMPANY as c ON (j.company_id = c.id)
    WHERE Y.job_id NOT IN (
      SELECT DISTINCT myJs.job_id FROM JOB_STATUS as myJs WHERE user_id = my_user_id
    );


IF my_job_id > 0 THEN
  SELECT jt.job_id as job_id, c.name as company_name, j.title as job_title
  FROM JOB_TAG as jt, JOB as j, COMPANY as c
  WHERE jt.tag_id IN (
    SELECT tag_id
    FROM JOB_TAG
    WHERE job_id = my_job_id
  ) AND jt.job_id != my_job_id
  AND jt.job_id = j.id AND j.company_id = c.id
  GROUP BY jt.job_id
  HAVING COUNT(jt.tag_id) >= 1
  ORDER BY COUNT(jt.tag_id) DESC
  limit 10;
ELSEIF my_user_id <= 0 THEN
  (SELECT jt.job_id as job_id, c.name as company_name, j.title as job_title FROM `JOB_STATUS` as jt, `JOB` as j, `COMPANY` as c WHERE jt.job_id = j.id AND c.id = j.company_id GROUP BY jt.job_id ORDER BY count(1) DESC LIMIT 5)
  UNION
  (SELECT jt.job_id as job_id, c.name as company_name, j.title as job_title FROM `JOB_STATUS` as jt, `JOB` as j, `COMPANY` as c WHERE jt.job_id = j.id AND jt.job_id AND c.id = j.company_id GROUP BY jt.job_id ORDER BY count(jt.create_at) DESC LIMIT 5);
ELSE
  
  OPEN cur;
  BEGIN
      DECLARE curr_job_id INT;
      DECLARE exist_history BOOLEAN DEFAULT FALSE;
      DECLARE exit_flag BOOLEAN DEFAULT FALSE;
      DECLARE CONTINUE HANDLER FOR NOT FOUND SET exit_flag=True;

      cloop: LOOP    
      IF exit_flag THEN
          LEAVE cloop;
      END IF;
      FETCH cur INTO curr_job_id;

      SELECT COUNT(*) INTO exist_history FROM RECOMMEND_HISTORY as rh WHERE rh.job_id = curr_job_id;
    	IF exist_history <= 0 THEN
        INSERT IGNORE INTO RECOMMEND_HISTORY (job_id, recommend_count) VALUES (curr_job_id, 0);
      END IF;
      UPDATE RECOMMEND_HISTORY as rh SET recommend_count = recommend_count + 1 WHERE rh.job_id = curr_job_id;
      END LOOP cloop;
  END;
  CLOSE cur;

  SELECT Y.job_id as job_id, c.name as company_name, j.title as job_title
  FROM (
    SELECT job_id, similar_factor
    FROM (SELECT js2.user_id as user_id, COUNT(*) as similar_factor
          FROM JOB_STATUS as js JOIN JOB_STATUS as js2 ON (js.job_id = js2.job_id AND js.user_id <> js2.user_id)
          WHERE js.user_id = my_user_id
          GROUP BY js2.user_id
          ORDER BY COUNT(*) DESC) as X 
          JOIN 
          JOB_STATUS as js ON X.user_id = js.user_id
    GROUP BY job_id, similar_factor
    ORDER BY similar_factor
  ) as Y JOIN JOB as j ON (Y.job_id = j.id) JOIN COMPANY as c ON (j.company_id = c.id)
  WHERE Y.job_id NOT IN (
    SELECT DISTINCT myJs.job_id FROM JOB_STATUS as myJs WHERE user_id = my_user_id
  );
  
  
END IF;
END$$
DELIMITER ;





DELIMITER $$
CREATE DEFINER=`root`@`%` PROCEDURE `UpdateJobTag`(IN `tag_name` VARCHAR(250))
BEGIN

DECLARE job_id INT;
DECLARE tag_id_var INT;
DECLARE cur CURSOR FOR SELECT id FROM JOB WHERE LOWER(text_description) LIKE LOWER(CONCAT('% ', tag_name, ' %'));

OPEN cur;

BEGIN
    DECLARE exit_flag BOOLEAN DEFAULT FALSE;
    DECLARE CONTINUE HANDLER FOR NOT FOUND SET exit_flag=True;
    INSERT IGNORE INTO TAG (tag, tag_type) VALUES (tag_name, "skills");
    SELECT id INTO tag_id_var FROM TAG WHERE tag = tag_name;
    DELETE FROM JOB_TAG WHERE tag_id=tag_id_var;

    cloop: LOOP    
    IF exit_flag THEN
        LEAVE cloop;
    END IF;
    FETCH cur INTO job_id;
    INSERT IGNORE INTO JOB_TAG (job_id, tag_id) VALUES (job_id, tag_id_var);
    END LOOP cloop;
END;
CLOSE cur;

END$$
DELIMITER ;







DELIMITER $$
CREATE DEFINER=`root`@`%` PROCEDURE `JobDescriptionHook`(IN `job_id_var` INT)
BEGIN

DECLARE tag_id_var INT;
DECLARE tag_name_var VARCHAR(250);
DECLARE tag_exist_in_jd INT;
DECLARE cur CURSOR FOR SELECT jt.tag_id as tag_id, t.tag as tag_name FROM TAG as t JOIN JOB_TAG as jt ON t.id = jt.tag_id
        WHERE jt.job_id = job_id_var;

OPEN cur;

BEGIN
    DECLARE exit_flag BOOLEAN DEFAULT FALSE;
    DECLARE CONTINUE HANDLER FOR NOT FOUND SET exit_flag=True;

    cloop: LOOP    
    IF exit_flag THEN
        LEAVE cloop;
    END IF;
    FETCH cur INTO tag_id_var, tag_name_var;

    SELECT count(1) INTO tag_exist_in_jd FROM JOB WHERE LOWER(text_description) LIKE LOWER(CONCAT('% ', tag_name_var, ' %')) AND id = job_id_var;

    IF tag_exist_in_jd < 1 THEN
        DELETE FROM JOB_TAG WHERE job_id=job_id_var AND tag_id=tag_id_var;
    END IF;    

    END LOOP cloop;
END;
CLOSE cur;

END$$
DELIMITER ;



CREATE TRIGGER `trigger JobDescriptionHook` AFTER UPDATE ON `JOB`
 FOR EACH ROW IF OLD.text_description <> NEW.text_description THEN
	CALL JobDescriptionHook(NEW.id);
END IF



CREATE TRIGGER `update tag when delete` AFTER DELETE ON `JOB_TAG`
 FOR EACH ROW UPDATE JOB SET tag_list= REPLACE(tag_list, concat(";", (SELECT tag FROM TAG WHERE id = OLD.tag_id LIMIT 1)) ,'') WHERE id=OLD.job_id



 CREATE TRIGGER `update tag when insert` AFTER INSERT ON `JOB_TAG`
 FOR EACH ROW UPDATE JOB SET tag_list=concat(tag_list, ";", (SELECT tag FROM TAG WHERE id = NEW.tag_id LIMIT 1)) WHERE id=NEW.job_id



 CREATE TRIGGER `user action: delete job status` BEFORE DELETE ON `JOB_STATUS`
 FOR EACH ROW UPDATE USER as u SET u.update_at = CURRENT_TIMESTAMP WHERE u.id = OLD.user_id



 CREATE TRIGGER `user action: insert job status` BEFORE INSERT ON `JOB_STATUS`
 FOR EACH ROW UPDATE USER as u SET u.update_at = CURRENT_TIMESTAMP WHERE u.id = NEW.user_id



 CREATE TRIGGER `user action: update job status` BEFORE UPDATE ON `JOB_STATUS`
 FOR EACH ROW UPDATE USER as u SET u.update_at = CURRENT_TIMESTAMP WHERE u.id = NEW.user_id