DROP TABLE IF EXISTS users;
DROP TABLE IF EXISTS castings;
DROP TABLE IF EXISTS stores;
DROP TABLE IF EXISTS brands;
DROP TABLE IF EXISTS chases;

CREATE TYPE user_role AS ENUM ('member', 'admin');
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(100) NOT NULL,
    name VARCHAR(100) NOT NULL,
    image text NOT NULL,
    role user_role NOT NULL DEFAULT 'member',
    active BOOLEAN NOT NULL DEFAULT TRUE,
    banned BOOLEAN NOT NULL DEFAULT FALSE,
    deleted BOOLEAN NOT NULL DEFAULT FALSE,
    last_login TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    last_activity TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    created TIMESTAMPTZ DEFAULT NOW() NOT NULL,
    modified TIMESTAMPTZ DEFAULT NOW() NOT NULL,
    UNIQUE (email)
);


CREATE  OR REPLACE FUNCTION
    update_timestamp()
RETURNS
    TRIGGER LANGUAGE plpgsql AS $$
BEGIN
    NEW.modified := NOW();
    RETURN NEW;
END;
$$;

CREATE TABLE stores (
    id SERIAL PRIMARY KEY,
    code CHAR(2) NOT NULL UNIQUE,
    name VARCHAR(50) NOT NULL UNIQUE,
    icon VARCHAR(100),
    active BOOLEAN NOT NULL DEFAULT True,
    deleted BOOLEAN NOT NULL DEFAULT False,
    created TIMESTAMPTZ DEFAULT NOW() NOT NULL,
    modified TIMESTAMPTZ DEFAULT NOW() NOT NULL
);


CREATE TRIGGER set_timestamp
    BEFORE UPDATE ON stores
    FOR EACH ROW
    EXECUTE PROCEDURE update_timestamp();


INSERT INTO stores (code, name, icon) 
VALUES  ('KR', 'Kroger', 'images/KR.png'),
        ('WM', 'Walmart', 'images/WM.png'),
        ('TG', 'Target', 'images/TG.png'),
        ('BB', 'Best Buy', 'images/BB.png'),
        ('DG', 'Dollar General', 'images/DG.png'),
        ('DT', 'Dollar Tree', 'images/DT.png'),
        ('KM', 'KMart', 'images/KM.png'),
        ('WG', 'Walgreens', 'images/WG.png'),
        ('GS', 'GameStop', 'images/GS.png');
        
CREATE TABLE brands (
    id SERIAL PRIMARY KEY,
    code CHAR(2) NOT NULL UNIQUE,
    name VARCHAR(50) NOT NULL UNIQUE,
    mfgr VARCHAR(50),
    icon VARCHAR(100),
    active BOOLEAN NOT NULL DEFAULT True,
    deleted BOOLEAN NOT NULL DEFAULT False,
    created TIMESTAMPTZ DEFAULT NOW() NOT NULL,
    modified TIMESTAMPTZ DEFAULT NOW() NOT NULL
);


CREATE TRIGGER set_timestamp
    BEFORE UPDATE ON brands
    FOR EACH ROW
    EXECUTE PROCEDURE update_timestamp();


INSERT INTO brands (code, name, mfgr) 
VALUES ('HW', 'Hot Wheels', 'Mattel'),
       ('MB', 'Matchbox', 'Mattel'),
       ('M2', 'M2 Machines', 'Castline');

CREATE TABLE chases (
    id SERIAL PRIMARY KEY,
    code CHAR(2) NOT NULL UNIQUE,
    name VARCHAR(50) NOT NULL UNIQUE,
    icon VARCHAR(100),
    active BOOLEAN NOT NULL DEFAULT True,
    deleted BOOLEAN NOT NULL DEFAULT False,
    created TIMESTAMPTZ DEFAULT NOW() NOT NULL,
    modified TIMESTAMPTZ DEFAULT NOW() NOT NULL
);


CREATE TRIGGER set_timestamp
    BEFORE UPDATE ON chases
    FOR EACH ROW
    EXECUTE PROCEDURE update_timestamp();


INSERT INTO chases (code, name, icon) 
VALUES ('ST', 'Super Treasure Hunt', 'images/ST.png'),
       ('TH', 'Treasure Hunt', 'images/TH.png'),
       ('CH', 'Chase', 'images/CH.png');
        
CREATE TABLE castings (
    id SERIAL PRIMARY KEY,
    
    year INT NOT NULL,
    number INT NOT NULL,
    name VARCHAR(100) NOT NULL,
    assortment VARCHAR(100) NOT NULL,
    recolor INT NOT NULL,
    series VARCHAR(50) DEFAULT NULL,
    special VARCHAR(50) DEFAULT NULL,
    color CHAR(6) DEFAULT NULL,
    mpn VARCHAR(10) DEFAULT NULL,
    image VARCHAR(200) DEFAULT NULL,
    thumbnail VARCHAR(100) DEFAULT NULL,
  
    brand CHAR(2) REFERENCES brands(code) ON UPDATE CASCADE,
    store CHAR(2) DEFAULT NULL REFERENCES stores(code) ON UPDATE CASCADE,
    chase CHAR(2) DEFAULT NULL  REFERENCES chases(code) ON UPDATE CASCADE,
  
    active BOOLEAN NOT NULL DEFAULT True,
    deleted BOOLEAN NOT NULL DEFAULT False,
    created TIMESTAMPTZ DEFAULT NOW() NOT NULL,
    modified TIMESTAMPTZ DEFAULT NOW() NOT NULL,
    
    UNIQUE (brand, year, number, mpn)
);        