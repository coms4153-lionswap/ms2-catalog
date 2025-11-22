CREATE TABLE reservations (
  reservation_id    CHAR(36) PRIMARY KEY,
  item_id           INT NOT NULL,
  buyer_id          INT NOT NULL,
  status            VARCHAR(20) NOT NULL,
  hold_expires_at   TIMESTAMP NOT NULL,
  updated_at        TIMESTAMP NOT NULL DEFAULT NOW()
);
