from batterytester.test_atom import ReferenceTestAtom


class BooleanReferenceTestAtom(ReferenceTestAtom):
    def __init__(
            self,
            name,
            command,
            duration,
            reference,
            arguments=None,
            result_key: str = None):
        super().__init__(
            name, command, arguments,
            duration, result_key
        )
        self.reference_data = reference
