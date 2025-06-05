CREATE TABLE `nodos` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `nodo` VARCHAR(50) NOT NULL,
  `servidor` VARCHAR(100) NOT NULL,
  `mqtt_usr` VARCHAR(100) NOT NULL,
  `mqtt_pass` VARCHAR(150) NOT NULL,
  `mqtt_puerto` INT NOT NULL,
  PRIMARY KEY (`id`),
  CHECK (`mqtt_puerto` BETWEEN 1 AND 65535)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;