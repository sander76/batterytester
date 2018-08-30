from typing import Tuple, List

import batterytester.core.helpers.message_subjects as subj
from batterytester.components.datahandlers.messaging import Messaging


def test_subscriptions():
    inf = Messaging()
    subs = inf.get_subscriptions()
    assert len(subs) == len(inf.subscriptions)
    for sub in subs:
        assert sub in inf.subscriptions

    inf = Messaging(subscription_filters=[subj.ACTOR_RESPONSE_RECEIVED])
    subs = [sub for sub in inf.get_subscriptions()]
    assert len(subs) == 0

    inf = Messaging(subscription_filters=(subj.ATOM_WARMUP,))
    subs = [sub for sub in inf.get_subscriptions()]
    assert len(subs) == 1
