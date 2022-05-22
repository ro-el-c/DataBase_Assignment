create database medical_care;
use medical_care;

create table Patient(
	pno varchar(2) primary key,
    name varchar(10) not null,
    age int not null,
    gender varchar(1)
);

insert into patient(pno, name, age, gender)
values
('P1', 'Olivia', 15, 'F'),
('P2', 'James', 20, 'M'),
('P3', 'Sophia', 25, 'F'),
('P4', 'Wayne', 30, 'M'),
('P5', 'Emma', 40, 'F');


insert into patient(pno, name, age, gender)
values ('P6', 'Test', 24, 'F');

delete from patient where pno='P6';

select * from patient;

create table Doctor(
	dno varchar(2) primary key,
    name varchar(10) not null,
    dept varchar(5) not null,
    gender varchar(1)
);

insert into doctor(dno, name, dept, gender)
values
('D1', 'Amelia', '치과', 'F'),
('D2', 'Robert', '정신과', 'M'),
('D3', 'Chloe', '외과', 'F'),
('D4', 'John', '안과', 'M'),
('D5', 'David', '내과', 'M');

select * from doctor;

create table Record(
    dno varchar(2),
    pno varchar(2),
    fee int not null,
    d_date datetime default now(),
    
    foreign key (dno) references doctor(dno)
				ON UPDATE CASCADE
                ON DELETE CASCADE,
	foreign key (pno) references patient(pno)
				ON UPDATE CASCADE
                ON DELETE CASCADE
);

drop table record;
select * from record;

insert into record(dno, pno, fee, d_date)
values
('D1', 'P1', 5000, '2022-01-10'),
('D1', 'P1', 10000, '2022-03-02'),
('D1', 'P3', 20000, '2022-04-20'),
('D1', 'P1', 5000, '2022-08-21'),
('D2', 'P1', 10000, '2022-06-02'),
('D2', 'P3', 15000, '2022-01-20'),
('D2', 'P2', 5000, '2022-09-01'),
('D2', 'P4', 10000, '2022-10-25'),
('D3', 'P3', 15000, '2022-07-25'),
('D3', 'P3', 30000, '2022-03-20'),
('D3', 'P4', 5000, '2022-02-15'),
('D3', 'P5', 15000, '2022-08-30'),
('D4', 'P3', 10000, '2022-11-05'),
('D4', 'P1', 20000, '2022-12-08'),
('D4', 'P3', 25000, '2022-05-01'),
('D4', 'P1', 15000, '2022-12-23'),
('D5', 'P3', 10000, '2022-06-07'),
('D5', 'P2', 5000, '2022-10-15'),
('D5', 'P1', 10000, '2022-03-15');

insert into record(dno, pno, fee, d_date)
values
('D1', 'P1', 5000, '2022-06-10');

delete from record where (dno='D1' and pno='P1' and fee=5000 and d_date='2022-06-10');

DROP TABLE RECORD;

select * from record;

-- 2번 단일 테이블에 대한 검색문

select name, age, gender
from patient
where (age >= 30 and age <40) or gender='F'
order by age;

select * from record;

select month(d_date) as month, count(*) as count
from record r
where r.fee <= 10000
group by month(d_date)
having count(*)>=2
order by count(*) desc;


-- 3번 복수 테이블에 대한 검색문
select * from patient;
select * from doctor;
select * from record;

-- 3-1
-- select d.name, d.dept
-- from doctor d, (select distinct r.dno from patient p, record r where p.pno = r.pno and p.name='Olivia') as oliviaDno
-- where d.dno = oliviaDno.dno;

select d.name, d.dept
from doctor d
where d.dno in (select r.dno
				from patient p, record r
				where p.pno = r.pno
                and p.name='Olivia');

select distinct r.dno from patient p, record r where p.pno = r.pno and p.name='Olivia';

-- 3-2
select r.dno, count(*) as record_count
from patient p, record r
where p.pno = r.pno and p.name='Olivia'
group by r.dno
order by count(*) desc;

-- 3-3
-- select d.name, d.dept
-- from doctor d, (select r.dno from patient p, record r where p.pno = r.pno and p.name='Olivia' group by r.dno having count(*)>=2) as oliviaDno
-- where d.dno = oliviaDno.dno;

select d.name, d.dept
from doctor d
where d.dno in (select r.dno
				from patient p, record r
				where p.pno = r.pno
                and p.name='Olivia'
                group by r.dno
                having count(*)>=2);

select r.dno, count(*) from patient p, record r where p.pno = r.pno and p.name='Olivia' group by r.dno having count(*)>=2;

-- 3-4
select distinct d.name, d.dept
from patient p, doctor d, record r
where p.pno=r.pno and d.dno=r.dno
and r.dno not in (select r.dno
				  from patient p, record r
				  where p.pno = r.pno and p.name='James'
				  group by r.dno)
		  and p.name='Olivia';

-- 3-5
-- 모든 의사의 진료를 한 번이라도 받은 환자의 아이디와 이름을 검색하라.
select distinct p.pno, p.name
from patient p
where p.pno in (select distinct r1.pno
				from record r1
				where not exists (select d.dno
								  from doctor d
								  where d.dno not in (select r2.dno
													  from record r2
                                                      where r2.pno=r1.pno)));
                                                      
select * from record;

select d.dno
from doctor d
where d.dno not in (select r2.dno
					from record r1, record r2
                    where r2.pno=r1.pno);

select distinct r1.pno
from record r1
where not exists (select d.dno
				  from doctor d
				  where d.dno not in (select r2.dno
									  from record r2
                                      where r2.pno=r1.pno));
                              
select distinct r1.pno, r1.dno
from record r1, record r2
where r1.pno=r2.pno
order by r1.pno;

select * from patient;     
select * from doctor;                
select * from record;
