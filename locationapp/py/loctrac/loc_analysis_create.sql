create table user (
	user_id text not null primary key
);

create table geotag (
	id			integer primary key autoincrement,
	user_id 		text not null, 
	tag 			text not null, 
	lat 			numeric not null, 
	lon 			numeric not null
);

create table location (
	id			integer primary key autoincrement,
	user_id			text not null references user(user_id),
	date			text not null,
	session			text not null,
	time			text not null,
	lat			numeric not null,
	lon			numeric not null,
	time_delta		text not null,
	dist_delta		numeric not null,
	speed			numeric not null,
	traj_id			text not null,
	clust_id		text not null,
	clust_lat		numeric not null,
	clust_lon		numeric not null,
	ma_window 		numeric not null, 
	ma_time 		numeric not null, 
	ma_dist 		numeric not null, 
	ma_speed 		numeric not null, 
	ma_ke_mode 		numeric
);

create table priorlocation (
        user_id                 text not null primary key references user(user_id),
        date                    text not null,
        session                 text not null,
        time                    text not null,
        lat                     numeric not null,
        lon                     numeric not null,
        time_delta              text not null,
        dist_delta              numeric not null,
        speed                   numeric not null,
        traj_id                 text not null,
        clust_id                text not null,
        clust_lat               numeric not null,
        clust_lon               numeric not null,
        ma_window               numeric not null,
        ma_time                 numeric not null,
        ma_dist                 numeric not null,
        ma_speed                numeric not null,
        ma_ke_mode              numeric
);


create table geoproximity (
	id			integer primary key autoincrement,
	loc_id			integer not null references location(id),
	geotag_id		integer not null references geotag(id),
	date			text not null,
	time			text not null
)
