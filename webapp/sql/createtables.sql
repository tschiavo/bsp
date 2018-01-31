/* 
	This sql script is known to work for PostgreSQL 9.1

	user is a reserved word in postgres so using _user for our user TABLE
*/

----------------------------
-- Extensions
----------------------------
CREATE extension "cube";
CREATE extension "earthdistance";
CREATE extension "uuid-ossp";

----------------------------
-- Static System Tables
-- DO NOT CASCADE DELETE ON THESE REFERENCES
----------------------------
CREATE TABLE message_type (
	id      INTEGER NOT NULL,
	descr   VARCHAR(128) NOT NULL,
	PRIMARY KEY(id)
);

CREATE TABLE token_type (
    id      INTEGER NOT NULL,
    descr   VARCHAR(128) NOT NULL,
    PRIMARY KEY(id)
);

CREATE TABLE sharing_level (
	id          INTEGER NOT NULL,
	sort_order  INTEGER NOT NULL,
	descr       VARCHAR(128) NOT NULL,
	PRIMARY KEY(id)
);

CREATE TABLE shareable_item (
	id      INTEGER NOT NULL,
	descr   VARCHAR(128) NOT NULL,
	default_sharing_level_id  INTEGER NOT NULL REFERENCES sharing_level(id) ON DELETE CASCADE,
	PRIMARY KEY(id)
);

CREATE TABLE invitation_status (
	id	    INTEGER NOT NULL,
	descr   VARCHAR(128) NOT NULL,
	PRIMARY KEY(id)
);

CREATE TABLE mood_type (
	mt_id       INTEGER NOT NULL,
	descr  	    VARCHAR(32) NOT NULL,
	value 	    INTEGER NOT NULL,
	sort_order	INTEGER NOT NULL,
	image_filename 	VARCHAR(32) NOT NULL,
	PRIMARY KEY(mt_id)
);

CREATE TABLE vibe_sender_visibility (
    id  INTEGER NOT NULL,
    descr VARCHAR(32) NOT NULL,
    PRIMARY KEY (id),
    UNIQUE (descr)
);

CREATE TABLE vibe_quanta (
    id  INTEGER NOT NULL,
    value INTEGER NOT NULL,
    PRIMARY KEY (id),
    UNIQUE (id, value)
);

CREATE TABLE vibe_pairing (
    id INTEGER NOT NULL,
    sort_order INTEGER NOT NULL,
    PRIMARY KEY (id),
    UNIQUE (id, sort_order)
);
    
CREATE TABLE vibe_affect (
    id  INTEGER NOT NULL,
    pairing_id INTEGER NOT NULL REFERENCES vibe_pairing(id) ON DELETE CASCADE,
    polarity INTEGER NOT NULL CHECK (polarity = 1 OR polarity = -1),
    descr VARCHAR(32) NOT NULL,
    PRIMARY KEY (id),
    UNIQUE (pairing_id, polarity),
    UNIQUE (descr)
);

CREATE TABLE web_service_registry (
    service_id  INTEGER NOT NULL,
    name        VARCHAR(128),
    url         VARCHAR(128),
    PRIMARY KEY(service_id),
    UNIQUE (service_id, name)
);


----------------------------
-- Volatile System Data Tables
----------------------------
CREATE TABLE _user (
	u_id        UUID,
	screen_name	VARCHAR(100) NOT NULL,
	email       VARCHAR(384) NOT NULL,
	name        VARCHAR(128),
	country     VARCHAR(128),
	phone       VARCHAR(128),
	profile_pic BYTEA,
	profile_pic_mimetype VARCHAR(128),
	PRIMARY KEY(u_id)
);

CREATE TABLE password (
	u_id            UUID NOT NULL REFERENCES _user(u_id),
	password_hash   VARCHAR(256) NOT NULL,
	PRIMARY KEY(u_id)
);

CREATE TABLE web_service_call_log (
    service_id  INTEGER NOT NULL REFERENCES web_service_registry(service_id) ON DELETE CASCADE,
    call_timestamp TIMESTAMP NOT NULL
);

----------------------------
-- Account Management Tables
----------------------------
CREATE TABLE invite_token (
    invite_token    UUID NOT NULL,
    is_used         BOOLEAN NOT NULL,
    owner           UUID NOT NULL REFERENCES _user(u_id),
    user_u_id       UUID REFERENCES _user(u_id),
    PRIMARY KEY(invite_token)
);

CREATE TABLE password_reset_token (
    reset_token     UUID NOT NULL,
    is_used         BOOLEAN NOT NULL,
	creation_time	TIMESTAMP NOT NULL,
    u_id            UUID NOT NULL REFERENCES _user(u_id),
    PRIMARY KEY(reset_token)
);

----------------------------
-- Volatile User Data Tables
----------------------------
CREATE TABLE _user_session (
	sess_id     UUID NOT NULL,
	last_seen   TIMESTAMP,
	sess_start  TIMESTAMP,
	timedout    BOOLEAN NOT NULL,
	u_id        UUID NOT NULL REFERENCES _user(u_id) ON DELETE CASCADE,
	PRIMARY KEY(sess_id)
);
CREATE INDEX idx_user_session_uid ON _user_session (u_id);
CREATE INDEX idx_user_session_sessid_uid ON _user_session (sess_id, u_id);

CREATE TABLE place (
	place_id	UUID NOT NULL,
	u_id		UUID REFERENCES _user(u_id) ON DELETE CASCADE,
	latitude	DOUBLE PRECISION NOT NULL,
	longitude	DOUBLE PRECISION NOT NULL,
	altitude	DOUBLE PRECISION NOT NULL,
	descr		VARCHAR(128),
    dist_at     INTEGER NOT NULL DEFAULT 300,
    dist_near   INTEGER NOT NULL DEFAULT 1800,
    dist_area   INTEGER NOT NULL DEFAULT 5400,
	PRIMARY KEY(place_id)
);

CREATE TABLE location (
    loc_timestamp TIMESTAMP NOT NULL,
    loc_timezone VARCHAR(100) NOT NULL,
    loc_id      UUID NOT NULL,
	sess_id		UUID NOT NULL REFERENCES _user_session(sess_id) ON DELETE CASCADE,
	time		TIMESTAMP NOT NULL,
	latitude	DOUBLE PRECISION NOT NULL,
	longitude	DOUBLE PRECISION NOT NULL,
	altitude	DOUBLE PRECISION,
	accuracy	DOUBLE PRECISION NOT NULL,
	PRIMARY KEY(loc_id)
);
CREATE INDEX idx_location_sessid ON location (sess_id);
CREATE INDEX idx_location_sessid_time ON location (sess_id, time);
CREATE INDEX idx_location_time ON location (time);

CREATE TABLE location_traj (
	sess_id		        UUID NOT NULL REFERENCES _user_session(sess_id) ON DELETE CASCADE,
    traj_id             UUID NOT NULL,
    traj_timestamp      TIMESTAMP NOT NULL,
    traj_entry_time     TIMESTAMP NOT NULL,
    traj_exit_time      TIMESTAMP NOT NULL,
    traj_points         INTEGER NOT NULL,
    traj_accum_time     INTERVAL NOT NULL,
    traj_accum_dist     DOUBLE PRECISION NOT NULL,
    traj_avg_vel        DOUBLE PRECISION NOT NULL,
    traj_avg_ke         VARCHAR(50) NOT NULL,
    traj_frame_accum_time     INTERVAL NOT NULL,
    traj_frame_accum_dist     DOUBLE PRECISION NOT NULL,
    traj_frame_avg_vel        DOUBLE PRECISION NOT NULL,
    traj_frame_ke             VARCHAR(50) NOT NULL,
    PRIMARY KEY(traj_id)
);

CREATE TABLE location_clust (
    traj_id             UUID NOT NULL REFERENCES location_traj(traj_id) ON DELETE CASCADE,
    clust_id            UUID NOT NULL,
    clust_entry_time    TIMESTAMP NOT NULL,
    clust_exit_time     TIMESTAMP NOT NULL,
    clust_points        INTEGER NOT NULL,
    clust_accum_time    INTERVAL NOT NULL,
    clust_accum_dist    DOUBLE PRECISION NOT NULL,
    clust_avg_vel       DOUBLE PRECISION NOT NULL,
    clust_avg_ke        VARCHAR(50) NOT NULL,
    clust_avg_lat       DOUBLE PRECISION NOT NULL,
    clust_avg_lon       DOUBLE PRECISION NOT NULL,
    PRIMARY KEY(clust_id)
);

/*
    data needs to be recalculated each time a place changes.
    ugly, but ok for now.
*/
CREATE TABLE location_clust_2_place_map (
    clust_id    UUID NOT NULL REFERENCES location_clust(clust_id) ON DELETE CASCADE,
    place_id    UUID NOT NULL REFERENCES place(place_id) ON DELETE CASCADE,
    proximity   INTEGER NOT NULL,
    dist        DOUBLE PRECISION NOT NULL,
    PRIMARY KEY(clust_id, place_id)
);

/*
    generic root message
*/

CREATE TABLE message (
	id              UUID NOT NULL,
    sess_id         UUID NOT NULL REFERENCES _user_session ON DELETE CASCADE,
	message_type_id	INTEGER NOT NULL REFERENCES message_type(id),
	head_id	        UUID NOT NULL, 
	parent_id       UUID NOT NULL,
	owner_u_id      UUID NOT NULL REFERENCES _user(u_id) ON DELETE CASCADE,
	from_u_id       UUID NOT NULL REFERENCES _user(u_id) ON DELETE CASCADE,
	to_u_id         UUID NOT NULL REFERENCES _user(u_id) ON DELETE CASCADE,
    sharing_level_id INTEGER REFERENCES sharing_level(id) NOT NULL,
	body            VARCHAR(1000),
	updated_timestamp   TIMESTAMP NOT NULL,
    created_timestamp   TIMESTAMP NOT NULL,
	is_archived     BOOLEAN NOT NULL,
	PRIMARY KEY(id)
);

CREATE VIEW message_view as (
    select *, (owner_u_id = from_u_id) as is_originator
    from message
);
    

/*
    twitter tokens
*/
CREATE TABLE token (
	message_id      UUID NOT NULL REFERENCES message(id) ON DELETE CASCADE,
    token_type_id   INTEGER NOT NULL REFERENCES token_type(id),
    value           VARCHAR(100) NOT NULL
);

CREATE VIEW token_view AS
    SELECT m.*, t.token_type_id, t.value, tt.descr
    FROM message m, token t, token_type tt
    WHERE m.id = t.message_id
      AND t.token_type_id = tt.id
;

/*
    mood message sub type
*/

CREATE TABLE mood_message (
	message_id	    UUID NOT NULL REFERENCES message(id) ON DELETE CASCADE,
	mood_type_id  	INTEGER NOT NULL REFERENCES mood_type(mt_id),
    fuzzy_location  VARCHAR(384),
    fuzzy_location_lookup_attempt_time TIMESTAMP,  
    fuzzy_weather  VARCHAR(384),
    fuzzy_weather_lookup_attempt_time TIMESTAMP,  
	PRIMARY KEY(message_id)
);

CREATE VIEW mood_message_view AS
	SELECT * 
	FROM message, mood_message 
	WHERE message.id = mood_message.message_id
;

/*
    invite message sub type
*/
CREATE TABLE invite_message (
	message_id		        UUID NOT NULL REFERENCES message(id) ON DELETE CASCADE,
	invitation_status_id  	INTEGER NOT NULL REFERENCES invitation_status(id) NOT NULL,
	PRIMARY KEY(message_id)
);

/*
    yo to parent message map. allows yo messages to be in response to
    any other message type. a way to have a private conversation
    about a message yet allows yo messages to remain a standalone 
    first class message type too

    the owner and parent_owner_id is here to preserve the design intention
    of having each person own their own data and run their own service
    if they choose. there will be 2 rows for each mapping.
*/
CREATE TABLE yo_2_parent_message_map (
    parent_message_id UUID NOT NULL REFERENCES message(id) ON DELETE CASCADE,
    yo_message_id UUID NOT NULL REFERENCES message(id) ON DELETE CASCADE,
    PRIMARY KEY(parent_message_id, yo_message_id)
);

CREATE VIEW yo_2_parent_message_map_view as
    SELECT a.*, b.owner_u_id as yo_owner_u_id, c.owner_u_id as parent_owner_u_id
    FROM yo_2_parent_message_map a, message b, message c
    WHERE a.yo_message_id = b.id and
          a.parent_message_id = c.id
;



/*
    yo message sub type
*/
CREATE TABLE yo_message (
	message_id	UUID NOT NULL REFERENCES message(id) ON DELETE CASCADE,
    show_all    BOOLEAN NOT NULL default FALSE,

	PRIMARY KEY(message_id)
);

CREATE TABLE yo_reply (
	message_id		UUID NOT NULL REFERENCES yo_message(message_id) ON DELETE CASCADE,
	from_u_id  	    UUID NOT NULL REFERENCES _user(u_id) ON DELETE CASCADE,
	time_stamp  	TIMESTAMP NOT NULL,
	body            VARCHAR(384),
    been_viewed     BOOLEAN NOT NULL
);

CREATE VIEW yo_message_view AS 
    SELECT *
    FROM message, yo_message
    WHERE message.id = yo_message.message_id
;

/*
    vibe message sub type
*/
CREATE TABLE vibe_message (
	message_id		        UUID NOT NULL REFERENCES message(id) ON DELETE CASCADE,
    sender_visibility_id    INTEGER REFERENCES vibe_sender_visibility(id) NOT NULL,
    PRIMARY KEY (message_id)
);

CREATE TABLE vibe_message_affect (
	message_id  UUID NOT NULL REFERENCES vibe_message(message_id) ON DELETE CASCADE,
    affect_id   INTEGER REFERENCES vibe_affect(id) NOT NULL,
    quanta_id   INTEGER REFERENCES vibe_quanta(id) NOT NULL,
    PRIMARY KEY (message_id),
    UNIQUE (message_id, affect_id)
);

CREATE VIEW vibe_message_view AS
    SELECT message.*,
           vibe_message.sender_visibility_id,
           vibe_sender_visibility.descr AS sender_visibility_descr,
           vibe_affect.polarity AS affect_polarity,
           vibe_affect.descr AS affect_descr,
           vibe_quanta.value AS affect_quanta
    FROM message, vibe_message, vibe_message_affect, vibe_affect, vibe_quanta, vibe_sender_visibility, vibe_pairing
    WHERE message.id = vibe_message.message_id
      AND vibe_message.message_id = vibe_message_affect.message_id
      AND vibe_message.sender_visibility_id = vibe_sender_visibility.id
      AND vibe_message_affect.affect_id = vibe_affect.id
      AND vibe_message_affect.quanta_id = vibe_quanta.id
      AND vibe_affect.pairing_id = vibe_pairing.id
    ORDER BY message.created_timestamp, vibe_pairing.sort_order ASC
;

/*
    relationship tables
*/
CREATE TABLE relationship (
	id			        UUID NOT NULL,
	owner_u_id		    UUID REFERENCES _user(u_id) ON DELETE CASCADE,
	other_u_id		    UUID REFERENCES _user(u_id) ON DELETE CASCADE,
	sharing_level_id	INTEGER REFERENCES sharing_level(id) NOT NULL,
	PRIMARY KEY(owner_u_id, other_u_id)
);

CREATE VIEW relationships_view AS
	SELECT * 
	FROM _user, relationship 
	WHERE _user.u_id = relationship.other_u_id
;

CREATE TABLE personal_sharing_level (
	u_id                UUID REFERENCES _user(u_id) ON DELETE CASCADE,
	shareable_item_id	INTEGER REFERENCES shareable_item(id) NOT NULL,
	sharing_level_id	INTEGER REFERENCES sharing_level(id) NOT NULL,
	PRIMARY KEY(u_id, shareable_item_id)
);

----------------------------
-- Indexes
----------------------------
CREATE UNIQUE INDEX idx_u_user_sn ON _user (screen_name);
CREATE UNIQUE INDEX idx_u_enity_email ON _user (email);

----------------------------
-- Static Data
----------------------------
INSERT INTO _user (u_id, screen_name, email) VALUES 
	('00000000-0000-0000-0000-000000000000','Anonymous','nobody@nowhere')
;

INSERT INTO mood_type (mt_id, sort_order, value, descr, image_filename) VALUES
	(1, 1000, 1, 'level 6', 'e6.png'),
	(6, 2000, 2, 'level 5', 'e5.png'),
	(2, 3000, 3, 'level 4', 'e4.png'),
	(3, 4000, 4, 'level 3', 'e3.png'),
	(4, 5000, 5, 'level 2', 'e2.png'),
	(5, 6000, 6, 'level 1', 'e1.png')
;

INSERT INTO message_type (id, descr) VALUES
	(0, 'mood'),
	(1, 'invite'),
	(2, 'yo'),
	(3, 'vibe')
;

INSERT INTO token_type (id, descr) VALUES
	(0, 'user'),
	(1, 'tag'),
	(2, 'url')
;

INSERT INTO vibe_sender_visibility (id, descr) VALUES
    (0, 'anonymous'),
    (1, 'hidden'),
    (2, 'revealed')
;

INSERT INTO vibe_quanta(id, value) VALUES
    (0, 1),
    (1, 2),
    (2, 3),
    (3, 5),
    (4, 8),
    (5, 13)
;

INSERT INTO vibe_pairing (id, sort_order) VALUES
    (0, 100),
    (1, 200),
    (2, 300),
    (3, 400),
    (4, 500),
    (5, 600),
    (6, 700)
;

INSERT INTO vibe_affect (id, pairing_id, polarity, descr) VALUES
    (0, 0, 1, 'calming'),
    (1, 0, -1, 'disruptive'),
    (2, 1, 1, 'clarifying'),
    (3, 1, -1, 'confusing'),
    (4, 2, 1, 'constructive'),
    (5, 2, -1, 'destructive'),
    (6, 3, 1, 'cleansing'),
    (7, 3, -1, 'toxic'),
    (8, 4, 1, 'energizing'),
    (9, 4, -1, 'draining'),
    (10, 5, 1, 'liberating'),
    (11, 5, -1, 'limiting'),
    (12, 6, 1, 'unifying'),
    (13, 6, -1, 'divisive')
;

INSERT INTO invitation_status (id, descr) VALUES
	(0, 'pending'),
	(1, 'accepted'),
	(2, 'rejected')
;

INSERT INTO sharing_level (id, sort_order, descr) VALUES
	(0, 100, 'private'),
	(1, 200, 'intimate'),
	(2, 300, 'trusted'),
	(3, 400, 'friend'),
	(4, 500, 'aquaintance'),
	(5, 600, 'public')
;

INSERT INTO shareable_item (id, descr, default_sharing_level_id) VALUES
	(1, 'profile.screen_name', 5),
	(2, 'profile.name', 0),
	(3, 'profile.email', 0),
	(4, 'profile.country', 0),
	(5, 'profile.phone', 0),
	(6, 'profile.pic', 0),
	(7, 'mood.current', 0),
	(8, 'mood.history_limited', 0),
	(9, 'mood.history_all', 0)
;

INSERT INTO web_service_registry (service_id, name, url) VALUES
    (1, 'wunderground', 'http://api.wunderground.com'),
    (2, 'openstreetmap', 'http://nominatim.openstreetmap.org')
;
