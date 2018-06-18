import batterytester.components.actors.tools as actor_tools
import batterytester.core.atom as atoms


def get_empty_sequence(_actors):
    return []


def get_unknown_exception_sequence(_actors):
    example_actor = actor_tools._get_actor(_actors, 'fake_actor')

    _val = (
        atoms.Atom(
            name='unknown exception action',
            command=example_actor.raise_unknown_exception,
            duration=1),
    )
    return _val


def get_fatal_exception_sequence(_actors):
    example_actor = actor_tools._get_actor(_actors, 'fake_actor')

    _val = (
        atoms.Atom(
            name='fatal test exception action',
            command=example_actor.raise_fatal_test_exception,
            duration=1),
    )
    return _val


def get_non_fatal_exception_sequence(_actors):
    example_actor = actor_tools._get_actor(_actors, 'fake_actor')

    _val = (
        atoms.Atom(
            name='fatal test exception action',
            command=example_actor.raise_non_fatal_test_exception,
            duration=1),
    )
    return _val


def get_sequence(_actors):
    example_actor = actor_tools._get_actor(_actors, 'fake_actor')

    _val = (
        atoms.Atom(
            name='close shade',
            command=example_actor.close,
            duration=1
        ),
    )
    return _val


def get_open_response_sequence(_actors):
    example_actor = actor_tools._get_actor(_actors, 'fake_actor')

    _val = (
        atoms.Atom(
            name='open with response',
            command=example_actor.open_with_reponse,
            duration=1
        ),
    )
    return _val


def get_reference_sequence(_actors):
    example_actor = actor_tools._get_actor(_actors, 'fake_actor')

    _val = (
        atoms.BooleanReferenceAtom(
            name='non fatal exception',
            command=example_actor.raise_non_fatal_test_exception,
            duration=1,
            reference={"a": False}

        ),
    )
    return _val
