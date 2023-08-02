from enum import Enum
from typing import TYPE_CHECKING, Any, Callable, Dict, List, Optional, Type, Union

if TYPE_CHECKING:
    from eggella.app import Eggella


class IntStateGroup(int, Enum):
    @classmethod
    def last(cls) -> "IntStateGroup":
        return cls.list()[-1]

    @classmethod
    def list(cls) -> List["IntStateGroup"]:
        return list(cls.__iter__())

    @classmethod
    def first(cls) -> "IntStateGroup":
        return cls.list()[0]


class Fsm:
    def __init__(self, state: Type["IntStateGroup"]):
        self.ctx: Dict[str, Any] = {}
        self.handlers: Dict[IntStateGroup, Callable] = {}

        self._all_states = state.list()
        self._start_state = state.first()
        self._end_state = state.last()
        self._current_state: Optional[IntStateGroup] = None

    def add_handler(self, state: IntStateGroup, func: Callable):
        self.handlers[state] = func

    def is_finish(self) -> bool:
        return self._current_state is None

    def on_state(self, state: "IntStateGroup"):
        def decorator(func):
            self.handlers[state] = func
            return func

        return decorator

    def _exec_state(self, state: "IntStateGroup"):
        if not self.handlers.get(state, None):
            raise KeyError(f"State {state} is not registered")
        return self.handlers[state]()

    def set(self, state: "IntStateGroup"):
        self._current_state = state
        return self._exec_state(self._current_state)

    def clear(self):
        self.ctx.clear()

    def run(self, state: Optional["IntStateGroup"] = None):
        self._current_state = state or self._start_state
        return self._exec_state(self._current_state)

    def finish(self) -> None:
        self.ctx.clear()
        self._current_state = None

    def actual(self):
        if self._current_state:
            return self._exec_state(self._current_state)

    def next(self):
        index = self._all_states.index(self._current_state)
        if index < len(self._all_states):
            self._current_state = self._all_states[index + 1]
            return self._exec_state(self._current_state)
        elif index == len(self._all_states) - 1 and self._all_states[index] == self._end_state:
            self.finish()
            return
        else:
            raise IndexError("States out of range")

    def prev(self):
        index = self._all_states.index(self._current_state)
        if index < len(self._all_states) and index != 0:
            self._current_state = self._all_states[index - 1]
            return self._exec_state(self._current_state)
        elif self._current_state == self._all_states[0]:
            self.finish()
            return
        else:
            raise IndexError("States out of range")

    def __getitem__(self, item):
        return self.ctx[item]

    def __setitem__(self, key, value):
        self.ctx[key] = value


class FsmController:
    def __init__(self, app: "Eggella"):
        self.fsm_storage: Dict[str, Fsm] = {}
        self._current_fsm: Optional[Fsm] = None
        self.__app = app

    def __getitem__(self, item):
        if self._current_fsm:
            return self._current_fsm[item]
        raise AttributeError("Need activate FSM first")

    def __setitem__(self, key, value):
        if not self._current_fsm:
            raise AttributeError("Need invoke FSM first")
        self._current_fsm[key] = value

    def is_active(self):
        return self._current_fsm is not None

    @property
    def ctx(self):
        if self._current_fsm:
            return self._current_fsm.ctx
        raise AttributeError("Need invoke FSM first")

    def attach(self, states: Type[IntStateGroup]):
        self.fsm_storage[states.__name__] = Fsm(states)

    def state(self, state: IntStateGroup):
        """state decorator"""
        if not self.fsm_storage.get(state.__class__.__name__):
            raise RuntimeError(
                f"State `{state.__class__.__name__}` is not registered in `{self.__app.app_name}`\n"
                f"Register this state group in application "
                f"by `register_states({state.__class__.__name__}) method`"
            )
        return self.fsm_storage[state.__class__.__name__].on_state(state)

    def current(self):
        return self._current_fsm.actual()

    def run(self, state: Union[IntStateGroup, Type[IntStateGroup]]):
        if isinstance(state, IntStateGroup):
            self._current_fsm = self.fsm_storage[state.__class__.__name__]
            return self._current_fsm.run(state)
        else:
            self._current_fsm = self.fsm_storage[state.__name__]
            return self._current_fsm.run(state.first())

    def prev(self):
        if not self._current_fsm:
            raise AttributeError("Need activate FSM first")
        self._current_fsm.prev()

    def next(self):
        if not self._current_fsm:
            raise AttributeError("Need activate FSM first")
        self._current_fsm.next()

    def set(self, state: IntStateGroup):
        if not self._current_fsm:
            raise AttributeError("Need activate FSM first")
        self._current_fsm.set(state)

    def finish(self):
        if not self._current_fsm:
            raise AttributeError("Need activate FSM first")
        self._current_fsm.finish()
        self._current_fsm = None


if __name__ == "__main__":

    class MyStates(IntStateGroup):
        a = 1
        b = 2

    print(type(MyStates))
    print(type(MyStates.a))
    # print(MyStates.__name__)
    # print(MyStates.first().__class__.__name__)
    # print(MyStates.a.__class__.__name__)
