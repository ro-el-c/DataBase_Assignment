create database naverMovie;
use naverMovie;

create table movie (
	id int auto_increment primary key,
	title varchar(50),
    movie_rate varchar(10),
    netizen_rate float(4, 2),
    netizen_count int,
    journalist_score float(4, 2),
    journalist_count int,
    scope varchar(30),
    playing_time int,
    opening_date datetime,
    director varchar(20),
    image varchar(500),
    enter_date datetime default now()
);

select * from movie;
drop table movie;