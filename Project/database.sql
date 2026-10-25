CREATE DATABASE IF NOT EXISTS student_result_db;
USE student_result_db;

CREATE TABLE IF NOT EXISTS students (
    id INT AUTO_INCREMENT PRIMARY KEY,
    student_id VARCHAR(30) NOT NULL UNIQUE,
    name VARCHAR(100) NOT NULL,
    roll_no VARCHAR(30) NOT NULL UNIQUE,
    python_marks DECIMAL(5,2) NOT NULL,
    java_marks DECIMAL(5,2) NOT NULL,
    dbms_marks DECIMAL(5,2) NOT NULL,
    se_marks DECIMAL(5,2) NOT NULL,
    daa_marks DECIMAL(5,2) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
