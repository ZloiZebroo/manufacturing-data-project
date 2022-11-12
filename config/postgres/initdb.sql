CREATE TABLE test (
    a int,
    b varchar,
    c date
);

CREATE TABLE devices (
    device_name varchar,
    device_id varchar,
    detail_name varchar,
    detail_id varchar,
    component_name varchar,
    component_id varchar,
    value_name varchar,
    value_id varchar
);

CREATE TABLE measurements (
    value_id varchar,
    status varchar,
    value float,
    timestamp timestamp
);


CREATE INDEX measurements_value_id_idx on measurements using btree(value_id);
CREATE INDEX devices_value_id_idx on devices using btree(value_id);