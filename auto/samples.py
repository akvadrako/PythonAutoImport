"""Demonstrate some behavior."""

def ignore_error():
    """Raise an exeption and ignore it."""
    try:
        [].pop()
        raise RuntimeError('should not happen')
    except IndexError:
        pass  # ignore


def test_nested_reraise():
    """A naked raise throws an original exeption, not one ignored in a called function."""
    try:
        try:
            1 / 0
        except ZeroDivisionError as e:
            ignore_error()
            raise

    except Exception as e:
        exc = e

    assert isinstance(exc, ZeroDivisionError)


def test_nested_reraise_inline():
    """A naked raise with exceptions ignored inline depend on the python version."""
    try:
        try:
            1 / 0
        except ZeroDivisionError as e:
            try:
                [].pop()
                raise RuntimeError('should not happen')
            except IndexError:
                pass  # ignore

            raise
    except Exception as e:
        exc = e

    import sys
    if sys.version_info[0] < 3:
        assert isinstance(exc, IndexError)
    else:
        assert isinstance(exc, ZeroDivisionError)
