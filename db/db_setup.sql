CREATE ROLE iisn_admin WITH PASSWORD 'abc123';
ALTER ROLE iisn_admin WITH LOGIN;

CREATE TABLE "DiningHall" ("id" SERIAL PRIMARY KEY, "name" TEXT);
CREATE TABLE "Genre" ("id" SERIAL PRIMARY KEY, "name" TEXT, "dininghall" INT references "DiningHall"(id));
CREATE TABLE "Item" ("id" SERIAL PRIMARY KEY, "name" TEXT, "genre" INT references "Genre"(id));
CREATE TABLE "Subscription" ("id" SERIAL PRIMARY KEY, "email" TEXT, "query" TEXT);

GRANT ALL PRIVILEGES ON DATABASE isitsteaknight TO iisn_admin;
GRANT ALL PRIVILEGES ON TABLE "DiningHall" TO iisn_admin;
GRANT ALL PRIVILEGES ON TABLE "Genre" TO iisn_admin;
GRANT ALL PRIVILEGES ON TABLE "Item" TO iisn_admin;
GRANT ALL PRIVILEGES ON sequence "Genre_id_seq" TO iisn_admin;
GRANT ALL PRIVILEGES ON sequence "Item_id_seq" TO iisn_admin;

INSERT INTO "DiningHall" (name) VALUES ('Brower Commons');
INSERT INTO "DiningHall" (name) VALUES ('Busch Dining Hall');
INSERT INTO "DiningHall" (name) VALUES ('Livingston Dining Commons');
INSERT INTO "DiningHall" (name) VALUES ('Neilson Dining Hall');
