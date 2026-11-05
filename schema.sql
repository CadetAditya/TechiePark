-- Techie Park Database Schema (MySQL)

CREATE DATABASE IF NOT EXISTS techiepark 
  CHARACTER SET utf8mb4 
  COLLATE utf8mb4_unicode_ci;

USE techiepark;

-- 1. Users Table
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    full_name VARCHAR(120) NOT NULL,
    email VARCHAR(255) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NULL,
    auth_provider VARCHAR(50) DEFAULT 'local', -- 'local' or 'google'
    google_id VARCHAR(255) NULL UNIQUE,
    avatar_url VARCHAR(500) NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 2. Profiles Table (For personal info completion step)
CREATE TABLE IF NOT EXISTS profiles (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL UNIQUE,
    bio TEXT NULL,
    linkedin_url VARCHAR(500) NULL,
    leetcode_url VARCHAR(500) NULL,
    github_url VARCHAR(500) NULL,
    cv_filename VARCHAR(255) NULL,
    is_completed BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 3. Skills Master Table
CREATE TABLE IF NOT EXISTS skills (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 4. User Skills Mapping Table
CREATE TABLE IF NOT EXISTS user_skills (
    user_id INT NOT NULL,
    skill_id INT NOT NULL,
    PRIMARY KEY (user_id, skill_id),
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (skill_id) REFERENCES skills(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 5. Seed some initial popular skills
INSERT IGNORE INTO skills (name) VALUES 
('React'), ('Vue'), ('Next.js'), ('HTML5'), ('CSS3'), ('JavaScript'), ('TypeScript'),
('Python'), ('FastAPI'), ('Django'), ('Flask'), ('Node.js'), ('Express'), ('Java'), ('Spring Boot'),
('C++'), ('Go'), ('Rust'), ('MySQL'), ('PostgreSQL'), ('MongoDB'), ('Redis'),
('Docker'), ('Kubernetes'), ('AWS'), ('GCP'), ('Machine Learning'), ('Deep Learning'),
('PyTorch'), ('TensorFlow'), ('NLP'), ('Computer Vision');

