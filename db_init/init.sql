CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50),
    email VARCHAR(50)
);

INSERT INTO users (name, email) VALUES
    ('Bridget Bataringaya' , 'bataringaya.bridget@students.mak.ac.ug'),
    ('Collins Nsubuga'     , 'nsubuga.collins@students.mak.ac.ug'),
    ('Edna Takaisa Kirabo' , 'kirabo.ednatakaisa@students.mak.ac.ug'),
    ('Isaac Mwesigwa'      , 'mwesigwa.isaac63@students.mak.ac.ug'),
    ('James Ayeta'         , 'wamumbi.ayeta@students.mak.ac.ug'),
    ('Judith Kemirembe'    , 'kemirembe.judith@students.mak.ac.ug'),
    ('Lilian Nankunda'     , 'nankunda.lilian@students.mak.ac.ug'),
    ('Moses Mushabe'       , 'mushabe.moses@students.mak.ac.ug'),
    ('Rachael Najjuko'     , 'najjuko.rachaelmirembe@students.mak.ac.ug'),
    ('Yusuf Mugoya'        , 'mugoya.yusuf@students.mak.ac.ug');
