-- reservations
-- auto-generated definition
create table reservations
(
    id                   bigserial
        primary key,
    reservation_group_id bigint  not null,
    user_id              bigint  not null
        references users
            on delete cascade,
    exam_schedule_id     bigint
        references exam_schedules
            on delete cascade,
    date                 date    not null,
    start_hour           integer not null,
    end_hour             integer not null,
    reserved_count       integer not null,
    is_confirmed         boolean,
    created_at           timestamp default now(),
    updated_at           timestamp default now()
);

-- alter table reservations
--     owner to postgres;

create index ix_reservations_reservation_group_id
    on reservations using btree (reservation_group_id);

create index ix_reservations_id
    on reservations using btree (id);


-- exam_schedule.py
-- auto-generated definition
create table exam_schedules
(
    id                   bigserial
        primary key,
    date                 date    not null,
    start_hour           integer not null,
    end_hour             integer not null,
    total_reserved_count integer not null
);

-- alter table exam_schedules
--     owner to postgres;

create index ix_exam_schedules_id
    on exam_schedules using btree (id);

-- user
-- auto-generated definition
create table users
(
    id              bigserial
        primary key,
    username        varchar not null unique,
    email           varchar not null unique,
    hashed_password varchar not null,
    role            varchar not null
);

-- alter table users
--     owner to postgres;

create index ix_users_id
    on users using btree (id);

create index ix_users_username
    on users using btree (username);

create unique index ix_users_email
    on users using btree (email);
