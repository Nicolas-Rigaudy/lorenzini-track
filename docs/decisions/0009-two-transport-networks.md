# 0009 — Two Transport Networks: Argos-Style Batches and MQTT

Status: accepted
Date: 2026-10-21 (owner decision of 2026-10-16)
Revises: the "no message bus" line that [0001](0001-product-direction.md) took from
`docs/research/07-technical-options.md`

## Context

Decision 0001 adopted simulated telemetry as a companion module to de-risk the
ingestion → store → serve pipeline. The technical options it rests on
(`docs/research/07-technical-options.md`, "What NOT to introduce") ruled out a message bus: real
ingestion is batch, and the simulated telemetry "can just call the ingestion API directly".
Decision 0007 made the simulated hammerhead fleet the flagship and left this line to be revisited
when MQTT arrived for the near-real-time trackers (milestone 0.3).

Real tags do not reach a database through one API call. Satellite tags reach their owners
through Argos, which delivers locations in batches after processing; acoustic receivers and
near-real-time trackers uplink small messages through a broker, with at-least-once delivery
and the duplicates that come with it. A gateway written against a direct API call would skip
the part of the pipeline the project exists to show.

## Decision

On 2026-10-16 the owner chose two transport networks for the simulated fleet (recorded in
`logics/backlog/item_002_gateway_ingestion_and_processing_pipeline_for_simulated_tags.md`):

- **Argos-style batch deliveries for satellite tags.** Each delivery is one CSV file in the
  `lt-argos-csv/1` format (`logics/architecture/adr_001_raw_tag_and_receiver_message_formats.md`)
  dropped into an inbox directory. The delivery time is in the file name; rows can be
  redelivered in a later batch.
- **MQTT for near-real-time trackers and receivers.** Mosquitto runs in `docker-compose.yml`
  next to PostGIS. Receivers publish on `lorenzini/sim/receivers/<receiver_id>/{detections,status}`
  with QoS 1, so duplicates are expected.

One gateway process consumes both networks, decodes, deduplicates and timestamps the messages,
and writes them to PostGIS. Implementation choices that follow from this:

- The simulator keeps writing files only (its output stays byte-identical for a seed). A
  replay step publishes the recorded MQTT log to the broker in publish order, duplicates
  included, so the gateway meets the same redeliveries a live broker would give it.
- Simulated time travels with each message as an MQTT 5 user property `published_at`. The
  gateway timestamps a message with it when present and with its own arrival time otherwise,
  which is what a live feed would get.
- The replay ends with a message on `lorenzini/sim/control/replay-done` carrying the number of
  messages sent, so a one-shot pipeline run knows when the gateway has seen everything.

## Reasoning

- The two networks match how the two tag types really report, so the uncertainty the map shows
  (late, duplicated, batched data) comes from the transport and not from a shortcut.
- Mosquitto is one small container; it does not bring the Kafka/SQS-style infrastructure the
  research doc warned against.
- Real ingestion of open datasets stays batch and keeps its scripts; only the simulated fleet
  uses the broker.

## Consequences

- `docker compose up` starts Mosquitto; the backend tests start a disposable broker next to the
  disposable PostGIS.
- The "no message bus" line in `docs/research/07-technical-options.md` is kept as written
  (research record) and read together with this decision.
- A real receiver feed could replace the replay by publishing to the same topics; a real Argos
  feed by dropping CSV files into the inbox.
