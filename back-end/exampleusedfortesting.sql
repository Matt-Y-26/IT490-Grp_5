-- Adminer 4.7.7 PostgreSQL dump

\connect "users";

DROP TABLE IF EXISTS "users";
CREATE TABLE "public"."users" (
    "username" character varying(255) NOT NULL,
    "hashed" character varying(255) NOT NULL
) WITH (oids = false);


