drop table if exists users;
create table users (
    id integer primary key autoincrement,
    username text not null,
    hash text not null
    -- salt text not null
);