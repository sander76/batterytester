from batterytester.components.actors.relay_actor import RelayActor
import time

if __name__=="__main__":
    actor = RelayActor(serial_port="PORT_2")
    actor.activate(pin=4,duration=1)

    time.sleep(2)


