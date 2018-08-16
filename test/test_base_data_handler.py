# from typing import Tuple
#
# import batterytester.core.helpers.message_subjects as subj
# from batterytester.components.datahandlers.base_data_handler import (
#     BaseDataHandler
# )
#
#
# def test_subscriptions():
#     inf = BaseDataHandler(None)
#
#     inf.subscriptions = ((subj.TEST_WARMUP, None), (subj.ATOM_RESULT, None))
#
#     subs = inf.get_subscriptions()
#
#     assert len(subs) == len(inf.subscriptions)
#     assert isinstance(subs, Tuple)
#     for sub in subs:
#         assert sub in inf.subscriptions
#
#     inf = BaseDataHandler(subscription_filters=[subj.ACTOR_RESPONSE_RECEIVED])
#     subs = [sub for sub in inf.get_subscriptions()]
#     assert len(subs) == 0
#
#     # assert subs[0][0] == subj.ACTOR_RESPONSE_RECEIVED
