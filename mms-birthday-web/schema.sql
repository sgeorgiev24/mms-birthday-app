drop table if exists User;
drop table if exists Birthday;
drop table if exists Payment;

create table User (
	id integer primary key autoincrement,
	username text unique not null,
	email text unique not null,
	password text not null,
	name text not null,
	last_name text not null,
	birthday_date text not null,
	is_admin boolean not null check (is_admin in (0, 1)),
	is_active boolean not null check (is_admin in (0, 1))
);

create table Birthday (
	id integer primary key autoincrement,
	user_id integer not null,
	current_birthday_date text not null
);

create table Payment (
	id integer primary key autoincrement,
	birthday_id integer not null,
	user_id integer not null,
	is_paid boolean not null check (is_paid in (0, 1)),
	foreign key(birthday_id) references Birthday(id),
	foreign key(user_id) references User(id)
);
