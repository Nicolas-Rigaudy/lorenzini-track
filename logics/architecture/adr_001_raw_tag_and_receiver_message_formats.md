## adr_001_raw_tag_and_receiver_message_formats - Raw tag and receiver message formats
> Date: 2026-10-20
> Status: Accepted
> Related request: (none yet)
> Related backlog: `logics/backlog/item_001_simulated_shark_tag_fleet.md`
> Related task: `logics/tasks/task_002_simulated_shark_tag_fleet.md`
> Drivers: item_002 needs a fixed input contract; the simulator must stay replaceable by real tag feeds
> Reminder: Update status, linked refs, decision rationale, consequences, and follow-up work when you edit this doc.

# Overview
- The simulator writes Argos-style CSV deliveries, MQTT-style receiver messages and a truth side channel in the formats below; the gateway (item_002) reads only the first two.

# Context
- The gateway must be written against raw messages, not against simulator internals, so that a real Argos or receiver feed could replace the simulator. Real feeds are not public (`docs/decisions/0004-no-live-tracking-data.md`), so the formats are modelled on typical Argos CSV exports and receiver MQTT uplinks, and every record is flagged simulated.

# Decision
- Output is byte-identical for the same seed and config: sorted keys, fixed numeric precision, fixed row and file order, no wall clock. `manifest.json` lists every file with its SHA-256.
- `argos/<program>_<YYYYmmddTHHMMZ>.csv` (`lt-argos-csv/1`): one batch per daily delivery. Columns: `program, platform_id, satellite, loc_date, loc_class, latitude, longitude, nb_messages, raw_data, simulated`. Class Z rows have empty coordinates. `raw_data` is 6 bytes as upper-case hex: type 0x01, battery mV (uint16 BE), transmissions since deployment (uint24 BE). Rows can be redelivered in a later batch, identical to the first.
- `mqtt/publishes.jsonl` (`lt-mqtt-log/1`): the MQTT log in publish order, one record per publish `{published_at, qos, topic, payload}`. Topics are `lorenzini/sim/receivers/<receiver_id>/detections` and `.../status`. Payloads (`lt-receiver-detections/1`, `lt-receiver-status/1`) carry `receiver_id`, a per-receiver `seq`, `sent_at`, and either `detections[{detected_at, transmitter_id}]` or `status_at` and `detections_total`. QoS 1 means duplicates: a redelivered message repeats the same `receiver_id` and `seq` and an identical payload. Receiver outages delay `sent_at` past the detection or status time.
- `deployments.jsonl` (`lt-deployment/1`): one record per shark (with its Argos platform and acoustic transmitter) and per receiver.
- `truth/*.jsonl` (`lt-truth/1`): true tracks, true positions behind each Argos fix and tag end of life. For validation only; the gateway must not read them.
- Every record carries `simulated: true`.

# Consequences
- Changing a field means bumping that format's version suffix and this document together.
- Dedup keys for the gateway are `(platform_id, loc_date)` for Argos and `(receiver_id, seq)` for receivers.

# References
- Related request: (none yet)
- Related backlog: `logics/backlog/item_001_simulated_shark_tag_fleet.md`
- Related task: `logics/tasks/task_002_simulated_shark_tag_fleet.md`
