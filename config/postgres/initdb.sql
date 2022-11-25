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


CREATE TABLE cnc_machine_data (
    entity varchar,
    param_name varchar,
    param_val_str  varchar,
    param_val_float float,
    timestamp timestamp
);


CREATE TABLE milling_machine_data
(
    entity          varchar,
    param_name      varchar,
    param_val_str   varchar,
    param_val_float float,
    timestamp       timestamp
);


CREATE INDEX measurements_value_id_idx on measurements using btree(value_id);
CREATE INDEX devices_value_id_idx on devices using btree(value_id);
CREATE INDEX cnc_machine_data_timestamp_idx on cnc_machine_data using btree(timestamp);
CREATE INDEX cnc_machine_data_param_name_idx on cnc_machine_data using btree(param_name);