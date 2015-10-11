CREATE TABLE "DiningHall" ("id" SERIAL PRIMARY KEY, "name" TEXT);
CREATE TABLE "Genre" ("id" SERIAL PRIMARY KEY, "name" TEXT, "dininghall" INT references "DiningHall"(id));
CREATE TABLE "Item" ("id" SERIAL PRIMARY KEY, "name" TEXT, "genre" INT references "Genre"(id));

INSERT INTO "DiningHall" (name) VALUES ('Brower Commons');
INSERT INTO "DiningHall" (name) VALUES ('Busch Dining Hall');
INSERT INTO "DiningHall" (name) VALUES ('Livingston Dining Commons');
INSERT INTO "DiningHall" (name) VALUES ('Neilson Dining Hall');
