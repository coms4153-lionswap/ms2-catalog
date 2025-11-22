CREATE TABLE Items (
  item_id      INT UNSIGNED PRIMARY KEY AUTO_INCREMENT,
  seller_id    INT UNSIGNED NOT NULL,
  product_name VARCHAR(160) NOT NULL,
  description  VARCHAR(500),
  price        DECIMAL(10,2) NOT NULL CHECK (price >= 0),
  `condition`  ENUM('New','LikeNew','Good','Fair','Poor') NOT NULL,
  category     VARCHAR(80)  NULL,
  `status`     ENUM('Listed','Reserved','Sold','Withdrawn') NOT NULL DEFAULT 'Listed',
  listed_at    DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at   DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  FULLTEXT KEY fts_items (product_name, description),
  KEY idx_items_listed (listed_at),
  KEY idx_items_price (price),
  KEY idx_items_status (`status`),
  KEY idx_items_condition (`condition`),
  KEY idx_items_category (category),
  CONSTRAINT fk_items_seller
    FOREIGN KEY (seller_id)
    REFERENCES Users(user_id)
    ON UPDATE CASCADE
    ON DELETE RESTRICT
);