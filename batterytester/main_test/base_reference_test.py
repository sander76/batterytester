from batterytester.main_test.base_test import BaseTest


class BaseReferenceTest(BaseTest):
    def __init__(self,learning_mode):
        pass

    def perform_test(self, current_loop, idx, atom):
        return super().perform_test(current_loop, idx, atom)



