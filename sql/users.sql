CREATE TABLE Users (
  user_id           INT UNSIGNED PRIMARY KEY AUTO_INCREMENT,
  uni               VARCHAR(32)  NOT NULL,    -- e.g., yl5961
  student_name      VARCHAR(120) NOT NULL,
  dept_name         VARCHAR(120),
  email             VARCHAR(255) NOT NULL,
  phone             VARCHAR(32),
  avatar_url        VARCHAR(512),
  credibility_score DECIMAL(4,2) NOT NULL DEFAULT 0.00, -- 0–5
  last_seen_at      DATETIME
)
