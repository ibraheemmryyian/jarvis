import sys
from types import GeneratorType

class ExitStack:
    def __init__(self):
        self._stack = []

    def __enter__(self):
        return self

    def enter(self, value):
        if isinstance(value, GeneratorType):
            self._stack.append((value.gi_frame.f_code, value))
        else:
            self._stack.append((None, value))
        return value

    def __exit__(self, exc_type, exc_value, traceback):
        for f, obj in reversed(self._stack):
            if f is not None:  # If it's a generator, close it
                try:
                    obj.close()
                except Exception as e:
                    if exc_type is None:
                        exc_type = type(e)
                        exc_value = e
                        traceback = e.__traceback__
                    elif not isinstance(exc_value, exc_type):
                        exc_type = exc_type, exc_value
            del self._stack[-1]
        return False

    def __len__(self):
        return len(self._stack)

    def pop_all(self):
        "Return a list of the objects pushed onto this stack"
        items, self._stack[:] = self._stack, []
        for f, obj in items:
            if f is not None:  # If it's a generator, close it
                try:
                    obj.close()
                except Exception as e:
                    exc_type, exc_value, exc_tb = sys.exc_info()
                    exc_value = e
                    exc_type = type(e)
                    exc_tb = e.__traceback__
            del obj

    def __iter__(self):
        return iter(self._stack)

    def pop(self, f=None):
        "Return and remove the object pushed onto this stack most recently."
        if f is None or f is self._stack[-1][0]:
            return ExitStack.pop_all(self)
        for i, (f_, obj) in enumerate(self._stack[:-1]):
            if f_ == f:
                break
        obj.close()
        del self._stack[-1]
        return obj

    def __bool__(self):
        return bool(self._stack)

    def __repr__(self):
        return '<%s at 0x%x with %d saved excpts>' % (
            type(self).__name__, id(self), len(self))

class ContextDecorator:
    def __init__(self, func):
        self.func = func

    def __call__(self, *args, **kwargs):
        return self.func(*args, **kwargs)

    def __enter__(self, *args, **kwargs):
        return self.func.__enter__(*args, **kwargs)

    def __exit__(self, *args, **kwargs):
        return self.func.__exit__(*args, **kwargs)

def contextmanager(func):
    def wrapper(*args, **kwargs):
        gen = func(*args, **kwargs)
        gen.close = lambda: None
        return gen
    return ContextDecorator(wrapper)

class closing:
    "Close an object that has a 'close' method."
    def __init__(self, obj):
        self.obj = obj

    def __enter__(self):
        return self.obj

    def __exit__(self, *exc_info):
        try: 
            if self.obj.close():
                return
        finally:
            del self.obj