This sequence diagram renders with plantuml. For convenience a vscode plugin can be used.

@startuml
    participant SensorConnector
    participant IncomingParser
    participant BaseTest
    participant Atom
    participant Database
    loop Sensor data check
        SensorConnector->>SensorConnector: listen for incoming sensor data
        SensorConnector->>IncomingParser: Parse data
    end
    IncomingParser->>BaseTest: send to basetest
    BaseTest->>BaseTest:start the test

    loop Continue until loopcount is exhausted.
        loop Get the sequence of atoms to test and loop
            BaseTest->>BaseTest:interpret sensor data and \n control flow based on data.
            BaseTest->>Atom:execute the test
            note over Atom: Send a test command ie.\nPV hub command,\nDongle command\nSerial command
            Atom->>Atom:test execution and\nresult checking
            Atom->>BaseTest:report result.
            BaseTest->>Database:Store result and sensor data.
        end
    end
    BaseTest->>BaseTest:stop the test
@enduml