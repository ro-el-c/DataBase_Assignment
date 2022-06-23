create database navermovie;
use navermovie;

-- 테이블 생성
create table movie(
	mcode int primary key,
    title varchar(100) not null,
    subtitle varchar(100),
    viewer_rate double,
    viewer_cnt int,
    ntz_rate double,
    ntz_cnt int,
    jour_rate double,
    jour_cnt int,
    playing_time int,
    sum_audi int,
    mainimgurl varchar(500)
);


CREATE TABLE genre (
	mcode int not null,
	genre varchar(50) not null,
    primary key(mcode, genre),
    foreign key (mcode) references movie(mcode)
);


create table nation(
	mcode int not null,
	nation	varchar(100) not null,
    primary key(mcode, nation),
    foreign key (mcode) references movie(mcode)
);


create table opening_date(
	mcode int not null,
    open_reopen varchar(10) not null,
    opening_date date,
    primary key(mcode, opening_date),
    foreign key (mcode) references movie(mcode)
);


create table rate(
	mcode int not null,
    rate_nation varchar(100),
    rate varchar(20) not null,
    primary key(mcode, rate_nation),
    foreign key (mcode) references movie(mcode)
);


CREATE TABLE photo (
	mcode int not null,
	photo_src varchar(500) not null,
    primary key(mcode, photo_src),
    foreign key (mcode) references movie(mcode)
);


CREATE TABLE director (
	dno	int	primary key,
	dname varchar(100)	not null,
    dname_eng varchar(200),
    d_imgurl varchar(500)
);


CREATE TABLE actor (
	ano	int primary key,
	aname varchar(100) not null,
    aname_eng varchar(200),
    a_status int not null,
	a_birth date,
    a_death date,
    a_imgurl varchar(500)
);


CREATE TABLE movie_director (
	mcode	int not null,
	dno	int	NOT NULL,
    primary key(mcode,dno),
    foreign key (mcode) references movie(mcode),
    foreign key (dno) references director(dno)
);


CREATE TABLE movie_actor (
	mcode	int	NOT NULL,
	ano	int	NOT NULL,
	role_ms	VARCHAR(10),
	role_name VARCHAR(100),
	primary key(mcode,ano),
    foreign key (mcode) references movie(mcode),
    foreign key (ano) references actor(ano)
);


CREATE TABLE review (
	rno	int primary key,
	mcode	int,
	r_nickname	VARCHAR(50),
	r_date	date,
	r_view	int,
	r_title	VARCHAR(1000),
	r_content	longtext,
	r_goodcnt	int	default 0,
    foreign key (mcode) references movie(mcode)
);


CREATE TABLE grade (
	gno int primary key auto_increment,
	mcode int not null,
	g_nickname	varCHAR(50),
	grade int not null,
	g_content	VARCHAR(4000),
	g_date	date,
    foreign key (mcode) references movie(mcode)
);


-- 인덱스 생성
create index idx_dname on director(dname);
create index idx_aname on actor(aname);
create index idx_genre on genre(genre);
create index idx_nation on nation(nation);