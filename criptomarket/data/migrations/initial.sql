CREATE TABLE "MOVEMENTS" (
	"id"	INTEGER NOT NULL UNIQUE,
	"date"	TEXT NOT NULL,
	"time"	TEXT NOT NULL,
	"from_moneda"	TEXT NOT NULL,
	"from_cantidad"	REAL NOT NULL,
	"to_moneda"	TEXT NOT NULL,
	"to_cantidad"	REAL NOT NULL,
	"valor_en_euros"	REAL NOT NULL,
	PRIMARY KEY("id" AUTOINCREMENT)
)