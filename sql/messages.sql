-- messages in a conversation
CREATE TABLE Messages (
  message_id       INT UNSIGNED PRIMARY KEY AUTO_INCREMENT,
  conversation_id  INT UNSIGNED NOT NULL,
  sender_id        INT UNSIGNED NOT NULL,
  message_type     ENUM('TEXT','IMAGE','SYSTEM') NOT NULL DEFAULT 'TEXT',
  body             TEXT NOT NULL,                       -- store the text; for IMAGE/SYSTEM, keep a short payload
  attachment_url   VARCHAR(1024) NULL,                  -- optional: for IMAGE, docs, etc.
  created_at       TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT fk_msg_convo
    FOREIGN KEY (conversation_id) REFERENCES Conversations(conversation_id)
    ON DELETE CASCADE ON UPDATE RESTRICT
);