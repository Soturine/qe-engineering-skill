# Human & Physical Process Risk Pack

Optional pack for manufacturing, logistics, field operations, IoT, RFID, scanners, devices or workflows where software state is coupled to physical actions.

## Activation

Enable only when project evidence indicates a physical/human operational process. Do not contaminate ordinary web/API projects with irrelevant scenarios.

## Scenario families

- required step omitted;
- step repeated;
- steps performed out of order;
- warning ignored;
- wrong item/container/device selected;
- two operators act on the same resource;
- shift/operator changes mid-process;
- scanner fails or produces duplicate reads;
- tag/barcode is damaged or unreadable;
- tag is swapped between physical items;
- two identity channels disagree;
- nearby RFID/tag is captured unintentionally;
- multiple tags are observed in one physical passage;
- physical quantity/content differs from digital record;
- device/network/power loss mid-operation;
- device/integration process restarts;
- message is delayed, duplicated or arrives out of order;
- browser/app refresh or session expiration occurs mid-flow;
- offline work reconnects with stale state;
- operator retries because UI feedback was delayed.

## Oracle discipline

The pack may propose scenarios, but it does not invent business outcomes. When the safe behavior is not defined, emit an ambiguity or exploratory charter. Security/data-integrity invariants may supply an oracle when explicitly backed by policy.

## Usability principle

Tests should reflect realistic operational pressure. Avoid fragile instructions that require perfect operator memory when the product is expected to prevent unsafe sequences.
