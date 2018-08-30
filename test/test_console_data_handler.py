
import batterytester.core.helpers.message_subjects as subj
from batterytester.components.datahandlers.console_data_handler import \
    ConsoleDataHandler


def test_subscriptions():
    inf = ConsoleDataHandler()

    subs = inf.get_subscriptions()

    assert len(subs) == len(inf.subscriptions)
    for sub in subs:
        assert sub in inf.subscriptions

    inf = ConsoleDataHandler(
        subscription_filters=[subj.ACTOR_RESPONSE_RECEIVED]
    )
    subs = [sub for sub in inf.get_subscriptions()]
    assert len(subs) == 1
    assert subs[0][0] == subj.ACTOR_RESPONSE_RECEIVED
