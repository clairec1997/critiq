-- MySQL dump 10.14  Distrib 5.5.64-MariaDB, for Linux (x86_64)
--
-- Host: localhost    Database: critiq_db
-- ------------------------------------------------------
-- Server version	5.5.64-MariaDB

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
-- Current Database: `critiq_db`
--

CREATE DATABASE /*!32312 IF NOT EXISTS*/ `critiq_db` /*!40100 DEFAULT CHARACTER SET latin1 */;

USE `critiq_db`;

--
-- Table structure for table `chapters`
--

DROP TABLE IF EXISTS `chapters`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `chapters` (
  `cid` int(11) NOT NULL AUTO_INCREMENT,
  `cnum` int(11) DEFAULT NULL,
  `sid` int(11) NOT NULL,
  `filename` varchar(100) DEFAULT NULL,
  PRIMARY KEY (`cid`),
  KEY `sid` (`sid`),
  CONSTRAINT `chapters_ibfk_1` FOREIGN KEY (`sid`) REFERENCES `works` (`sid`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=9 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `chapters`
--

LOCK TABLES `chapters` WRITE;
/*!40000 ALTER TABLE `chapters` DISABLE KEYS */;
INSERT INTO `chapters` VALUES (1,1,1,'/students/critiq/critiq/draft/uploaded/sid1cnum1.html'),(2,1,2,'/students/critiq/critiq/draft/uploaded/sid2cnum1.html'),(3,2,2,'/students/critiq/critiq/draft/uploaded/sid2cnum2.html'),(4,2,1,'/students/critiq/critiq/draft/uploaded/sid1cnum2.html'),(5,3,2,'/students/critiq/critiq/draft/uploaded/sid2cnum3.html'),(6,1,3,'/students/critiq/critiq/draft/uploaded/sid3cnum1.html'),(7,1,4,'/students/critiq/critiq/draft/uploaded/sid4cnum1.html'),(8,2,4,'/students/critiq/critiq/draft/uploaded/sid4cnum2.html');
/*!40000 ALTER TABLE `chapters` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `reviewCredits`
--

DROP TABLE IF EXISTS `reviewCredits`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `reviewCredits` (
  `rid` int(11) NOT NULL,
  `cid` int(11) NOT NULL,
  PRIMARY KEY (`rid`,`cid`),
  KEY `cid` (`cid`),
  CONSTRAINT `reviewCredits_ibfk_1` FOREIGN KEY (`rid`) REFERENCES `reviews` (`rid`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `reviewCredits_ibfk_2` FOREIGN KEY (`cid`) REFERENCES `chapters` (`cid`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `reviewCredits`
--

LOCK TABLES `reviewCredits` WRITE;
/*!40000 ALTER TABLE `reviewCredits` DISABLE KEYS */;
INSERT INTO `reviewCredits` VALUES (1,1),(2,4),(3,2),(4,6);
/*!40000 ALTER TABLE `reviewCredits` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `reviews`
--

DROP TABLE IF EXISTS `reviews`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `reviews` (
  `rid` int(11) NOT NULL AUTO_INCREMENT,
  `commenter` int(11) NOT NULL,
  `ishelpful` int(11) DEFAULT NULL,
  `reviewText` varchar(2000) DEFAULT NULL,
  PRIMARY KEY (`rid`),
  KEY `commenter` (`commenter`),
  CONSTRAINT `reviews_ibfk_1` FOREIGN KEY (`commenter`) REFERENCES `users` (`uid`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `reviews`
--

LOCK TABLES `reviews` WRITE;
/*!40000 ALTER TABLE `reviews` DISABLE KEYS */;
INSERT INTO `reviews` VALUES (1,1,NULL,'wow, great story!'),(2,2,NULL,'as a recent teen i feel personally attacked by this content'),(3,2,NULL,'i can comment on my own work and i love it thank you for quality content\r\n'),(4,2,NULL,'this is incredibly insightful and i look forward to witnessing more of your work');
/*!40000 ALTER TABLE `reviews` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `taglink`
--

DROP TABLE IF EXISTS `taglink`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `taglink` (
  `tid` int(11) NOT NULL,
  `sid` int(11) NOT NULL,
  KEY `sid` (`sid`),
  KEY `tid` (`tid`),
  CONSTRAINT `taglink_ibfk_1` FOREIGN KEY (`sid`) REFERENCES `works` (`sid`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `taglink_ibfk_2` FOREIGN KEY (`tid`) REFERENCES `tags` (`tid`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `taglink`
--

LOCK TABLES `taglink` WRITE;
/*!40000 ALTER TABLE `taglink` DISABLE KEYS */;
INSERT INTO `taglink` VALUES (2,1),(4,1),(15,1),(16,1),(1,1),(2,1),(3,1),(3,1),(1,2),(2,2),(5,2),(6,2),(7,2),(10,2),(17,2),(18,2),(23,2),(26,2),(27,2),(29,2),(31,2),(1,2),(3,2),(3,2),(2,2),(1,3),(7,3),(10,3),(18,3),(1,3),(4,3),(3,3),(2,3),(10,4),(1,4),(2,4),(3,4),(3,4);
/*!40000 ALTER TABLE `taglink` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `tags`
--

DROP TABLE IF EXISTS `tags`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `tags` (
  `tid` int(11) NOT NULL AUTO_INCREMENT,
  `ttype` varchar(20) NOT NULL,
  `tname` varchar(50) NOT NULL,
  PRIMARY KEY (`tid`),
  UNIQUE KEY `tname` (`tname`)
) ENGINE=InnoDB AUTO_INCREMENT=34 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `tags`
--

LOCK TABLES `tags` WRITE;
/*!40000 ALTER TABLE `tags` DISABLE KEYS */;
INSERT INTO `tags` VALUES (1,'genre','Romance'),(2,'genre','Fantasy'),(3,'genre','Horror'),(4,'genre','Sci-Fi'),(5,'genre','Historical'),(6,'genre','Mystery'),(7,'genre','Humor'),(8,'genre','Literary'),(9,'genre','Thriller'),(10,'genre','Suspense'),(11,'genre','Poetry'),(12,'audience','General'),(13,'audience','Young Adult'),(14,'audience','18+'),(15,'warnings','Violence'),(16,'warnings','Gore'),(17,'warnings','Rape or Sexual Assault'),(18,'warnings','Sexual Content'),(19,'warnings','Racism'),(20,'warnings','Homophobia'),(21,'warnings','Suicidal Content'),(22,'warnings','Abuse'),(23,'warnings','Animal Cruelty'),(24,'warnings','Self-Harm'),(25,'warnings','Eating Disorder'),(26,'warnings','Incest'),(27,'warnings','Child Abuse or Pedophilia'),(28,'warnings','Death or Dying'),(29,'warnings','Pregnancy or Childbirth'),(30,'warnings','Miscarriages orAbortion'),(31,'warnings','Mental Illness'),(32,'isFin','Finished'),(33,'isFin','Work in Progress');
/*!40000 ALTER TABLE `tags` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `users`
--

DROP TABLE IF EXISTS `users`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `users` (
  `uid` int(11) NOT NULL AUTO_INCREMENT,
  `username` varchar(30) DEFAULT NULL,
  `passhash` char(60) DEFAULT NULL,
  `commentscore` decimal(10,0) DEFAULT NULL,
  PRIMARY KEY (`uid`),
  UNIQUE KEY `username` (`username`),
  KEY `username_2` (`username`)
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `users`
--

LOCK TABLES `users` WRITE;
/*!40000 ALTER TABLE `users` DISABLE KEYS */;
INSERT INTO `users` VALUES (1,'e','$2b$12$Ur/GY6v/v831mJdBD8o9bOFI5tCTNUwzLliJxHikkqaZBjZPN/c5a',NULL),(2,'sbussey','$2b$12$w53pirC8UMbHSPY9q37.HeOTpa3rB3MtGhasEPV6OH7RbtSdmnEDe',NULL),(3,'scott','$2b$12$X.xsPPzIRyjjTiUK6/qBHOtSfZwIySFynNsbYhP8e7QW6W2cAeuli',NULL),(4,'claire','$2b$12$y9sVbK.WTrAaE6czj756fuu6hsQR5efMZk9q1f1U.sZf5NI7aqeUa',NULL),(5,'sophia','$2b$12$yku/OWhnAgi85/jG7HCY5eNDT6k/uGS5jzxduwpWd3vbVqWv1yYD6',NULL);
/*!40000 ALTER TABLE `users` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `works`
--

DROP TABLE IF EXISTS `works`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `works` (
  `sid` int(11) NOT NULL AUTO_INCREMENT,
  `uid` int(11) NOT NULL,
  `title` varchar(200) DEFAULT NULL,
  `updated` date DEFAULT NULL,
  `summary` varchar(2000) DEFAULT NULL,
  `stars` float DEFAULT NULL,
  PRIMARY KEY (`sid`),
  KEY `uid` (`uid`),
  CONSTRAINT `works_ibfk_1` FOREIGN KEY (`uid`) REFERENCES `users` (`uid`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `works`
--

LOCK TABLES `works` WRITE;
/*!40000 ALTER TABLE `works` DISABLE KEYS */;
INSERT INTO `works` VALUES (1,1,'Claire test 1',NULL,'wee!',NULL),(2,2,'test it ',NULL,'ahhhhh',NULL),(3,1,'whoop!',NULL,'be bop de doop',NULL),(4,4,'Claire\'s Big Adventure',NULL,'Claire walks a dog.',NULL);
/*!40000 ALTER TABLE `works` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2019-12-01 18:46:13
