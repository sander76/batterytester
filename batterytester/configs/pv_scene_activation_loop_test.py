from batterytester.main_test.powerview_scene_activation_test import \
    PowerViewSceneActivationLoopTest

test = PowerViewSceneActivationLoopTest(
    # name of the test. This will also be used as the folder name where
    # report data is stored.
    test_name="normal test",
    # how many loops to run
    loop_count=100,
    # delay between execution of test atoms.
    delay=80,
    # List of shade ids being used in the test
    scene_ids=(56159, 12744),
    # ip address of the powerview hub
    hub_ip='192.168.0.106',
    # for reporting use the provided telegram api token.
    telegram_token=None,
    # Chat_id where messages need to be sent to.
    chat_id=None
)

if __name__ == "__main__":
    test.start_test()
