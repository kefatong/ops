-- MySQL dump 10.14  Distrib 5.5.47-MariaDB, for Linux (x86_64)
--
-- Host: localhost    Database: ops
-- ------------------------------------------------------
-- Server version	5.5.47-MariaDB

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `Compliance`
--

DROP TABLE IF EXISTS `Compliance`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `Compliance` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(64) DEFAULT NULL,
  `deviceGroup` int(11) DEFAULT NULL,
  `taskGroup` int(11) DEFAULT NULL,
  `status` int(11) DEFAULT NULL,
  `isdelete` tinyint(1) DEFAULT NULL,
  `instaff` varchar(64) DEFAULT NULL,
  `inputtime` datetime DEFAULT NULL,
  `remarks` text,
  `enabled` tinyint(1) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `deviceGroup` (`deviceGroup`),
  KEY `taskGroup` (`taskGroup`),
  CONSTRAINT `Compliance_ibfk_1` FOREIGN KEY (`deviceGroup`) REFERENCES `deviceGroup` (`id`),
  CONSTRAINT `Compliance_ibfk_2` FOREIGN KEY (`taskGroup`) REFERENCES `deviceTaskGroup` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `Compliance`
--

LOCK TABLES `Compliance` WRITE;
/*!40000 ALTER TABLE `Compliance` DISABLE KEYS */;
INSERT INTO `Compliance` VALUES (1,'RHEL6合规修正',1,1,2,NULL,'administrator','2016-08-13 18:35:12','',1),(2,'RHEL6合规修正',1,1,2,NULL,'administrator','2016-08-13 19:41:06','',1);
/*!40000 ALTER TABLE `Compliance` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `ComplianceRecord`
--

DROP TABLE IF EXISTS `ComplianceRecord`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `ComplianceRecord` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `ComplianceRecord`
--

LOCK TABLES `ComplianceRecord` WRITE;
/*!40000 ALTER TABLE `ComplianceRecord` DISABLE KEYS */;
/*!40000 ALTER TABLE `ComplianceRecord` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `DeviceRelationshipDeviceGroup`
--

DROP TABLE IF EXISTS `DeviceRelationshipDeviceGroup`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `DeviceRelationshipDeviceGroup` (
  `deviceGroup_id` int(11) DEFAULT NULL,
  `device_id` int(11) DEFAULT NULL,
  KEY `deviceGroup_id` (`deviceGroup_id`),
  KEY `device_id` (`device_id`),
  CONSTRAINT `DeviceRelationshipDeviceGroup_ibfk_1` FOREIGN KEY (`deviceGroup_id`) REFERENCES `deviceGroup` (`id`),
  CONSTRAINT `DeviceRelationshipDeviceGroup_ibfk_2` FOREIGN KEY (`device_id`) REFERENCES `devices` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `DeviceRelationshipDeviceGroup`
--

LOCK TABLES `DeviceRelationshipDeviceGroup` WRITE;
/*!40000 ALTER TABLE `DeviceRelationshipDeviceGroup` DISABLE KEYS */;
INSERT INTO `DeviceRelationshipDeviceGroup` VALUES (1,1);
/*!40000 ALTER TABLE `DeviceRelationshipDeviceGroup` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `System`
--

DROP TABLE IF EXISTS `System`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `System` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `device_id` int(11) DEFAULT NULL,
  `an` varchar(64) DEFAULT NULL,
  `sn` varchar(64) DEFAULT NULL,
  `ip` varchar(20) DEFAULT NULL,
  `hostname` varchar(64) DEFAULT NULL,
  `power_ip` varchar(32) DEFAULT NULL,
  `os_version` varchar(64) DEFAULT NULL,
  `post` int(11) DEFAULT NULL,
  `status` int(11) DEFAULT NULL,
  `isdelete` tinyint(1) DEFAULT NULL,
  `instaff` varchar(64) DEFAULT NULL,
  `inputtime` datetime DEFAULT NULL,
  `remarks` text,
  `type` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `post` (`post`),
  CONSTRAINT `System_ibfk_1` FOREIGN KEY (`post`) REFERENCES `deviceTaskGroup` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `System`
--

LOCK TABLES `System` WRITE;
/*!40000 ALTER TABLE `System` DISABLE KEYS */;
INSERT INTO `System` VALUES (4,1,'SERVER001','SERVER001','172.16.46.141','cobbler_test','172.16.46.141','RHEL6-x86_64',1,1,NULL,'administrator','2016-08-13 20:30:33',NULL,1);
/*!40000 ALTER TABLE `System` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `TaskRelationshipTaskGroup`
--

DROP TABLE IF EXISTS `TaskRelationshipTaskGroup`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `TaskRelationshipTaskGroup` (
  `deviceTaskGroup_id` int(11) DEFAULT NULL,
  `deviceTask_id` int(11) DEFAULT NULL,
  `PQ` int(11) DEFAULT NULL,
  KEY `deviceTaskGroup_id` (`deviceTaskGroup_id`),
  KEY `deviceTask_id` (`deviceTask_id`),
  CONSTRAINT `TaskRelationshipTaskGroup_ibfk_1` FOREIGN KEY (`deviceTaskGroup_id`) REFERENCES `deviceTaskGroup` (`id`),
  CONSTRAINT `TaskRelationshipTaskGroup_ibfk_2` FOREIGN KEY (`deviceTask_id`) REFERENCES `deviceTasks` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `TaskRelationshipTaskGroup`
--

LOCK TABLES `TaskRelationshipTaskGroup` WRITE;
/*!40000 ALTER TABLE `TaskRelationshipTaskGroup` DISABLE KEYS */;
INSERT INTO `TaskRelationshipTaskGroup` VALUES (1,1,NULL);
/*!40000 ALTER TABLE `TaskRelationshipTaskGroup` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `alembic_version`
--

DROP TABLE IF EXISTS `alembic_version`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `alembic_version` (
  `version_num` varchar(32) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `alembic_version`
--

LOCK TABLES `alembic_version` WRITE;
/*!40000 ALTER TABLE `alembic_version` DISABLE KEYS */;
INSERT INTO `alembic_version` VALUES ('9e2cbd0c31f4');
/*!40000 ALTER TABLE `alembic_version` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `deviceGroup`
--

DROP TABLE IF EXISTS `deviceGroup`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `deviceGroup` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(64) DEFAULT NULL,
  `business` varchar(64) DEFAULT NULL,
  `isdelete` tinyint(1) DEFAULT NULL,
  `instaff` varchar(64) DEFAULT NULL,
  `inputtime` datetime DEFAULT NULL,
  `remarks` text,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `deviceGroup`
--

LOCK TABLES `deviceGroup` WRITE;
/*!40000 ALTER TABLE `deviceGroup` DISABLE KEYS */;
INSERT INTO `deviceGroup` VALUES (1,'ansible测试组','ansible测试',NULL,'administrator','2016-08-13 17:23:12','');
/*!40000 ALTER TABLE `deviceGroup` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `devicePowers`
--

DROP TABLE IF EXISTS `devicePowers`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `devicePowers` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `type` int(11) DEFAULT NULL,
  `enabled` tinyint(1) DEFAULT NULL,
  `ip` varchar(64) DEFAULT NULL,
  `user` varchar(64) DEFAULT NULL,
  `password_hash` varchar(256) DEFAULT NULL,
  `powerid` varchar(256) DEFAULT NULL,
  `device_id` int(11) DEFAULT NULL,
  `isdelete` tinyint(1) DEFAULT NULL,
  `remarks` text,
  `instaff` varchar(64) DEFAULT NULL,
  `inputtime` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `device_id` (`device_id`),
  CONSTRAINT `devicePowers_ibfk_1` FOREIGN KEY (`device_id`) REFERENCES `devices` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `devicePowers`
--

LOCK TABLES `devicePowers` WRITE;
/*!40000 ALTER TABLE `devicePowers` DISABLE KEYS */;
/*!40000 ALTER TABLE `devicePowers` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `deviceTaskGroup`
--

DROP TABLE IF EXISTS `deviceTaskGroup`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `deviceTaskGroup` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(64) DEFAULT NULL,
  `enabled` tinyint(1) DEFAULT NULL,
  `type` int(11) DEFAULT NULL,
  `isdelete` tinyint(1) DEFAULT NULL,
  `instaff` varchar(64) DEFAULT NULL,
  `inputtime` datetime DEFAULT NULL,
  `remarks` text,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `deviceTaskGroup`
--

LOCK TABLES `deviceTaskGroup` WRITE;
/*!40000 ALTER TABLE `deviceTaskGroup` DISABLE KEYS */;
INSERT INTO `deviceTaskGroup` VALUES (1,'系统初始化',1,4,NULL,'administrator','2016-08-13 17:27:57','');
/*!40000 ALTER TABLE `deviceTaskGroup` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `deviceTasks`
--

DROP TABLE IF EXISTS `deviceTasks`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `deviceTasks` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `taskname` varchar(64) DEFAULT NULL,
  `scriptname` varchar(256) DEFAULT NULL,
  `type` int(11) DEFAULT NULL,
  `arch` int(11) DEFAULT NULL,
  `md5code` varchar(128) DEFAULT NULL,
  `path` varchar(256) DEFAULT NULL,
  `version` varchar(20) DEFAULT NULL,
  `enabled` tinyint(1) DEFAULT NULL,
  `isdelete` tinyint(1) DEFAULT NULL,
  `instaff` varchar(64) DEFAULT NULL,
  `inputtime` datetime DEFAULT NULL,
  `remarks` text,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `deviceTasks`
--

LOCK TABLES `deviceTasks` WRITE;
/*!40000 ALTER TABLE `deviceTasks` DISABLE KEYS */;
INSERT INTO `deviceTasks` VALUES (1,'关闭Selinux','playbook1.yml',2,1,'278a92a8699ba745128005aecdde047c','./upload/script_dirs/2/278a92a8699ba745128005aecdde047c','',1,NULL,'administrator','2016-08-13 17:27:31','');
/*!40000 ALTER TABLE `deviceTasks` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `devices`
--

DROP TABLE IF EXISTS `devices`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `devices` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `device_id` int(11) DEFAULT NULL,
  `hostname` varchar(64) DEFAULT NULL,
  `ip` varchar(64) DEFAULT NULL,
  `an` varchar(64) DEFAULT NULL,
  `sn` varchar(64) DEFAULT NULL,
  `os` varchar(64) DEFAULT NULL,
  `manufacturer` varchar(64) DEFAULT NULL,
  `brand` varchar(64) DEFAULT NULL,
  `model` varchar(64) DEFAULT NULL,
  `cpumodel` varchar(64) DEFAULT NULL,
  `cpucount` int(11) DEFAULT NULL,
  `memsize` int(11) DEFAULT NULL,
  `disksize` varchar(64) DEFAULT NULL,
  `business` varchar(64) DEFAULT NULL,
  `powerstatus` int(11) DEFAULT NULL,
  `onstatus` int(11) DEFAULT NULL,
  `usedept` varchar(64) DEFAULT NULL,
  `usestaff` varchar(64) DEFAULT NULL,
  `mainuses` varchar(128) DEFAULT NULL,
  `isdelete` tinyint(1) DEFAULT NULL,
  `instaff` varchar(64) DEFAULT NULL,
  `inputtime` datetime DEFAULT NULL,
  `remarks` text,
  PRIMARY KEY (`id`),
  UNIQUE KEY `ix_devices_device_id` (`device_id`),
  UNIQUE KEY `ix_devices_sn` (`sn`),
  UNIQUE KEY `ix_devices_an` (`an`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `devices`
--

LOCK TABLES `devices` WRITE;
/*!40000 ALTER TABLE `devices` DISABLE KEYS */;
INSERT INTO `devices` VALUES (1,NULL,'ansbile','172.16.46.130','SERVER001','SERVER001','centos7.2','dell','poweredge','r720','intel',2,4,'80','ansible测试',1,1,'研发部','柯发通','测试ansible',NULL,NULL,'2016-08-13 17:22:53','');
/*!40000 ALTER TABLE `devices` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `histroyCommands`
--

DROP TABLE IF EXISTS `histroyCommands`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `histroyCommands` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `user_id` int(11) DEFAULT NULL,
  `command` varchar(512) DEFAULT NULL,
  `inputtime` datetime DEFAULT NULL,
  `remarks` text,
  PRIMARY KEY (`id`),
  KEY `user_id` (`user_id`),
  CONSTRAINT `histroyCommands_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `histroyCommands`
--

LOCK TABLES `histroyCommands` WRITE;
/*!40000 ALTER TABLE `histroyCommands` DISABLE KEYS */;
/*!40000 ALTER TABLE `histroyCommands` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `logs`
--

DROP TABLE IF EXISTS `logs`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `logs` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `user_id` int(11) DEFAULT NULL,
  `logtime` datetime DEFAULT NULL,
  `content` varchar(256) DEFAULT NULL,
  `action` varchar(32) DEFAULT NULL,
  `logobjtype` varchar(64) DEFAULT NULL,
  `logobj_id` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `user_id` (`user_id`),
  CONSTRAINT `logs_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `logs`
--

LOCK TABLES `logs` WRITE;
/*!40000 ALTER TABLE `logs` DISABLE KEYS */;
/*!40000 ALTER TABLE `logs` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `moduleClass`
--

DROP TABLE IF EXISTS `moduleClass`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `moduleClass` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(64) DEFAULT NULL,
  `separator` varchar(64) DEFAULT NULL,
  `isdelete` tinyint(1) DEFAULT NULL,
  `instaff` varchar(64) DEFAULT NULL,
  `inputtime` datetime DEFAULT NULL,
  `remarks` text,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `moduleClass`
--

LOCK TABLES `moduleClass` WRITE;
/*!40000 ALTER TABLE `moduleClass` DISABLE KEYS */;
INSERT INTO `moduleClass` VALUES (1,'系统管理','	',NULL,'administrator','2016-08-13 17:23:51','');
/*!40000 ALTER TABLE `moduleClass` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `pushCommandLogger`
--

DROP TABLE IF EXISTS `pushCommandLogger`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `pushCommandLogger` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `device_id` int(11) DEFAULT NULL,
  `command` text,
  `inputtime` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `device_id` (`device_id`),
  CONSTRAINT `pushCommandLogger_ibfk_1` FOREIGN KEY (`device_id`) REFERENCES `devices` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `pushCommandLogger`
--

LOCK TABLES `pushCommandLogger` WRITE;
/*!40000 ALTER TABLE `pushCommandLogger` DISABLE KEYS */;
/*!40000 ALTER TABLE `pushCommandLogger` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `roles`
--

DROP TABLE IF EXISTS `roles`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `roles` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(64) DEFAULT NULL,
  `default` tinyint(1) DEFAULT NULL,
  `permissions` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`),
  KEY `ix_roles_default` (`default`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `roles`
--

LOCK TABLES `roles` WRITE;
/*!40000 ALTER TABLE `roles` DISABLE KEYS */;
INSERT INTO `roles` VALUES (1,'manager',0,7),(2,'User',1,2),(3,'Administrator',0,8207);
/*!40000 ALTER TABLE `roles` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `taskClass`
--

DROP TABLE IF EXISTS `taskClass`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `taskClass` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(64) DEFAULT NULL,
  `module_id` int(11) DEFAULT NULL,
  `separator` varchar(64) DEFAULT NULL,
  `isdelete` tinyint(1) DEFAULT NULL,
  `instaff` varchar(64) DEFAULT NULL,
  `inputtime` datetime DEFAULT NULL,
  `remarks` text,
  PRIMARY KEY (`id`),
  KEY `module_id` (`module_id`),
  CONSTRAINT `taskClass_ibfk_1` FOREIGN KEY (`module_id`) REFERENCES `moduleClass` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `taskClass`
--

LOCK TABLES `taskClass` WRITE;
/*!40000 ALTER TABLE `taskClass` DISABLE KEYS */;
INSERT INTO `taskClass` VALUES (1,'系统部署',1,'  ',NULL,'administrator','2016-08-13 17:24:58',''),(2,'软件下发',1,'  ',NULL,'administrator','2016-08-13 17:25:04',''),(3,'合规巡检',1,'  ',NULL,'administrator','2016-08-13 17:25:13',''),(4,'初始化',1,'  ',NULL,'administrator','2016-08-13 17:25:24','');
/*!40000 ALTER TABLE `taskClass` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `users`
--

DROP TABLE IF EXISTS `users`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `users` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `email` varchar(64) DEFAULT NULL,
  `username` varchar(64) DEFAULT NULL,
  `password_hash` varchar(128) DEFAULT NULL,
  `role_id` int(11) DEFAULT NULL,
  `name` varchar(64) DEFAULT NULL,
  `location` varchar(64) DEFAULT NULL,
  `position` varchar(64) DEFAULT NULL,
  `about_me` text,
  `phone` varchar(11) DEFAULT NULL,
  `qq` varchar(13) DEFAULT NULL,
  `member_since` datetime DEFAULT NULL,
  `last_seen` datetime DEFAULT NULL,
  `confirmed` tinyint(1) DEFAULT NULL,
  `avatar_hash` varchar(32) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `ix_users_email` (`email`),
  UNIQUE KEY `ix_users_username` (`username`),
  KEY `role_id` (`role_id`),
  CONSTRAINT `users_ibfk_1` FOREIGN KEY (`role_id`) REFERENCES `roles` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `users`
--

LOCK TABLES `users` WRITE;
/*!40000 ALTER TABLE `users` DISABLE KEYS */;
INSERT INTO `users` VALUES (1,'kefatong@qq.com','administrator','pbkdf2:sha1:1000$C4FgJf1v$04f51a54e596f792d0734df25a2d0cc0d868d9cb',3,'Admin',NULL,NULL,NULL,NULL,NULL,'2016-08-13 21:21:40','2016-08-14 00:36:58',1,NULL);
/*!40000 ALTER TABLE `users` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2016-08-13 21:48:59
