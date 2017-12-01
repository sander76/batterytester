"""Start of a test.

Main entry point is class instantiation from one of the classes in the
`main_test` folder
"""

from batterytester.main_test.powerview_open_close_loop_test import \
    PowerViewOpenCloseLoopTest

test = PowerViewOpenCloseLoopTest(
    # name of the test. This will also be used as the folder name where
    # report data is stored.
    test_name="normal test",
    # how many loops to run
    loop_count=10,
    # delay between execution of test atoms.
    delay=80,
    # List of shade ids being used in the test
    shade_ids=[['1', 46232]],
    # ip address of the powerview hub
    hub_ip='192.168.0.106',
    # for reporting use the provided telegram api token.
    telegram_token=None,
    # Chat_id where messages need to be sent to.
    chat_id=None
)

if __name__ == "__main__":
    test.start_test()