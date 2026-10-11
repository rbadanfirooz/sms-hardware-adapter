# SMS Hardware Adapter

A reusable hardware abstraction layer for cellular modems and edge devices, designed to provide reliable communication between SMS gateway software and modem hardware.

## Overview

The **SMS Hardware Adapter** provides a dedicated interface for communicating with cellular modem modules through serial connections. It encapsulates low-level hardware communication, AT command execution, modem initialization, connection monitoring, and communication error handling.

The project aims to isolate hardware-specific operations from higher-level application logic, making SMS gateway systems easier to maintain, test, and extend to different modem devices.

## Objectives

- Provide a consistent interface for serial modem communication.
- Encapsulate AT command transmission and response handling.
- Support configurable serial port parameters, including baud rate and communication timeouts.
- Manage modem initialization and readiness checks.
- Detect communication failures and expose meaningful error information.
- Provide a foundation for connection recovery and modem reconnection strategies.
- Reduce hardware dependencies within higher-level SMS gateway components.

## Scope

### In Scope

- Serial communication management.
- AT command request and response handling.
- Modem initialization and status verification.
- Communication timeout handling.
- Detection and reporting of serial communication errors.
- Hardware-specific configuration and adapter interfaces.
- Modem connection lifecycle management.

### Out of Scope

The following responsibilities belong to other components of the SMS gateway architecture:

- SMS PDU encoding and decoding.
- Multipart SMS assembly.
- SMS persistence and database management.
- Message classification and business rule evaluation.
- SMS delivery workflows and retry policies.
- ERP synchronization.
- Administrative API endpoints.

## Architecture

The adapter acts as the hardware communication boundary between the cellular modem and the rest of the SMS gateway.

```text
+-------------------------------+
|     SMS Gateway Components    |
+-------------------------------+
                |
                v
+-------------------------------+
|      SMS Hardware Adapter     |
|                               |
|  - Serial Communication       |
|  - AT Command Handling        |
|  - Modem Initialization       |
|  - Status Monitoring          |
|  - Error Reporting            |
+-------------------------------+
                |
                v
+-------------------------------+
|       Cellular Modem          |
|                               |
|  UART / Serial Interface      |
|  AT Command Interface         |
+-------------------------------+
```

The adapter should expose a stable interface so that higher-level components do not need to depend directly on serial-port implementation details or modem-specific communication logic.

## Supported Hardware

The initial development target is the **SIM7600 cellular modem family**, using a UART/serial interface.

The design should remain extensible to other cellular modem models that provide compatible AT command interfaces.

Actual compatibility depends on the modem firmware, supported AT commands, serial configuration, and hardware interface.

## Technology Stack

The initial implementation is based on:

- **Language:** Python
- **Communication:** UART / Serial
- **Hardware Interface:** AT Commands
- **Target Platform:** Linux-based edge devices
- **Initial Target Device:** Raspberry Pi
- **Initial Modem:** SIM7600

These technologies describe the initial development target; future implementations may introduce additional adapters or communication interfaces.

## Design Principles

### Hardware Abstraction

Higher-level components should interact with a defined adapter interface rather than directly accessing serial ports.

### Separation of Concerns

The adapter is responsible for hardware communication, not SMS business logic, persistence, or ERP integration.

### Reliability

Communication failures, unexpected modem responses, and timeouts should be handled explicitly.

### Configurability

Serial port settings and communication parameters should be configurable rather than hard-coded.

### Testability

The design should support testing with simulated serial responses so that core communication logic can be validated without requiring physical modem hardware for every test.

### Extensibility

Additional modem models should be supportable without requiring substantial changes to the gateway's higher-level components.

## Reliability Considerations

A production-ready implementation should account for:

- Serial port disconnection and reconnection.
- AT command response timeouts.
- Unexpected or malformed modem responses.
- Modem initialization failures.
- Concurrent command execution and response association.
- Recovery after temporary communication failures.
- Logging of communication errors without exposing sensitive information.

Recovery behavior must be coordinated carefully with command execution to avoid confusing responses or duplicating operations.

## Security Considerations

- Avoid logging sensitive message content or credentials unnecessarily.
- Restrict access to serial devices through operating-system permissions.
- Validate configuration values before opening serial connections.
- Keep hardware access and application-level permissions appropriately separated.

## Testing Strategy

Testing should cover the following areas:

- Serial connection initialization and shutdown.
- AT command transmission and response parsing.
- Timeout and communication failure handling.
- Modem readiness and status checks.
- Simulated disconnection and recovery scenarios.
- Compatibility with the target modem and firmware.

Hardware integration tests should be performed on the actual target device before a release is considered production-ready.

## Development Status

**Status:** Initial development / architecture definition.

The repository is intended to evolve into a reusable hardware adapter with clearly defined interfaces, documented behavior, and automated tests.

Features described as future or production-readiness goals should not be considered implemented until they have been verified in the source code and tested.

## Roadmap

- Define the hardware adapter interface.
- Implement serial connection management.
- Implement AT command transmission and response handling.
- Add modem initialization and readiness checks.
- Add structured error handling and logging.
- Implement and test recovery strategies.
- Add automated tests using simulated modem responses.
- Validate integration with SIM7600 hardware.
- Document supported commands, configuration, and limitations.

## License

Choose and add an appropriate open-source license before publishing this repository publicly. Ensure that all included source code and dependencies are authorized for redistribution.

## Contributing

Contributions should preserve the separation between hardware communication and higher-level SMS gateway responsibilities. Changes should include appropriate tests and documentation where applicable.
