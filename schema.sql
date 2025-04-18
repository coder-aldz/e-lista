DROP TABLE IF EXISTS user;
DROP TABLE IF EXISTS trans;
DROP TABLE IF EXISTS receipt;
DROP TABLE IF EXISTS trans_saved;
DROP TABLE IF EXISTS item;


CREATE TABLE "user" (
	"user_id"	INTEGER NOT NULL UNIQUE,
	"username"	TEXT NOT NULL UNIQUE,
	"password"	TEXT NOT NULL,
	"user_type"	TEXT NOT NULL,
	PRIMARY KEY("user_id" AUTOINCREMENT)
);

CREATE TABLE "trans" (
	"trans_id"	INTEGER NOT NULL UNIQUE,
	"item_id"	TEXT NOT NULL,
	"receipt_id"	INTEGER NOT NULL,
	PRIMARY KEY("trans_id" AUTOINCREMENT),
	FOREIGN KEY("item_id") REFERENCES "item"("item_id"),
	FOREIGN KEY("receipt_id") REFERENCES "receipt"("receipt_id")
);

CREATE TABLE "receipt" (
	"receipt_id"	INTEGER NOT NULL UNIQUE,
	"receipt_date"	TEXT NOT NULL,
	"receipt_amount"	INTEGER NOT NULL,
	PRIMARY KEY("receipt_id" AUTOINCREMENT)
);

CREATE TABLE "trans_saved" (
	"user_id"	INTEGER NOT NULL,
	"receipt_id"	INTEGER NOT NULL,
	FOREIGN KEY("receipt_id") REFERENCES "receipt"("receipt_id"),
	FOREIGN KEY("user_id") REFERENCES "user"("user_id")
);

CREATE TABLE "item" (
	"item_id"	INTEGER NOT NULL UNIQUE,
	"qr_code"	INTEGER NOT NULL UNIQUE,
	"item_name"	TEXT NOT NULL,
	"price"	INTEGER NOT NULL,
	PRIMARY KEY("item_id" AUTOINCREMENT),
	FOREIGN KEY("item_id") REFERENCES "trans"("item_id")
);