-- one row per 1-to-1 conversation (use the convention user_a_id < user_b_id)
CREATE TABLE Conversations (
  conversation_id   INT UNSIGNED PRIMARY KEY AUTO_INCREMENT,
  user_a_id         INT UNSIGNED NOT NULL,  -- smaller user_id
  user_b_id         INT UNSIGNED NOT NULL,  -- larger user_id
  created_at        TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  last_message_at   TIMESTAMP NULL,
  UNIQUE KEY uq_pair (user_a_id, user_b_id),            -- enforces single conversation per pair
  CONSTRAINT fk_user_a
    FOREIGN KEY (user_a_id) REFERENCES Users(user_id)
    ON DELETE CASCADE ON UPDATE RESTRICT,
  CONSTRAINT fk_user_b
    FOREIGN KEY (user_b_id) REFERENCES Users(user_id)
    ON DELETE CASCADE ON UPDATE RESTRICT
);