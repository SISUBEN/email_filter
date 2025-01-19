from enum import IntEnum, auto
from typing import List, Dict, Literal, Tuple
from dataclasses import dataclass
import re


@dataclass
class Transition:
    present: int
    condition: int
    _next: int


class TokenType(IntEnum):
    CHAR = auto()
    AT = auto()
    DOT = auto()
    INVALID = auto()


class EmailFilterState(IntEnum):
    INITIAL = auto()
    CHAR = auto()
    AT = auto()
    CHAR_AFTER_AT = auto()
    DOT_AFTER_AT = auto()
    DOT_AFTER_SECOND_DOT = auto()
    ACCEPT = auto()
    INVALID = auto()


class EmailFilterFSM:
    def __init__(self) -> None:
        states: List[int] = [int(state) for state in EmailFilterState]
        transition_table: List[Transition] = [
            # 初始状态
            Transition(
                EmailFilterState.INITIAL, TokenType.CHAR, EmailFilterState.CHAR
            ),
            Transition(
                EmailFilterState.INITIAL, TokenType.AT, EmailFilterState.INVALID
            ), 
            Transition(
                EmailFilterState.INITIAL, TokenType.DOT, EmailFilterState.INVALID
            ), 
            
            # 在 @ 前的合法状态
            Transition(
                EmailFilterState.CHAR, TokenType.CHAR, EmailFilterState.CHAR
            ),
            Transition(
                EmailFilterState.CHAR, TokenType.AT, EmailFilterState.AT),
            Transition(
                EmailFilterState.CHAR, TokenType.DOT, EmailFilterState.INVALID
            ), 
            
            # @ 后允许的状态
            Transition(
                EmailFilterState.AT, TokenType.CHAR, EmailFilterState.CHAR_AFTER_AT
            ),
            Transition(
                EmailFilterState.CHAR_AFTER_AT,
                TokenType.CHAR,
                EmailFilterState.CHAR_AFTER_AT,
            ),
            Transition(
                EmailFilterState.CHAR_AFTER_AT,
                TokenType.DOT,
                EmailFilterState.DOT_AFTER_AT,
            ),
            Transition(
                EmailFilterState.DOT_AFTER_AT,
                TokenType.CHAR,
                EmailFilterState.CHAR_AFTER_AT,
            ),
            # @ 的非法状态
            
            
            # 其他非法状态处理
            Transition(
                EmailFilterState.AT, TokenType.DOT, EmailFilterState.INVALID
            ),
            Transition(
                EmailFilterState.DOT_AFTER_AT, TokenType.DOT, EmailFilterState.INVALID
            ), 
        ]

        start_state = EmailFilterState.INITIAL
        accept_states: List[int] = [EmailFilterState.ACCEPT.value]

        self._fsm = FSM(
            states,
            transition_table,
            start_state,
            accept_states,
        )

    def _match_token(self, char: str) -> int:
        if re.match(r"[a-zA-Z0-9]", char):
            return TokenType.CHAR
        elif char == "@":
            return TokenType.AT
        elif char == ".":
            return TokenType.DOT
        else:
            return TokenType.INVALID

    def do_filter(self, email: str) -> str:
        filtered_email = ""
        buffer = ""
        for char in email:
            token = self._match_token(char)
            if token == TokenType.INVALID:
                filtered_email = ""
                buffer = ""
                break
            self._fsm.process(token)
            buffer += char
            if self._fsm.current_state == EmailFilterState.INVALID:
                filtered_email = ""
                buffer = ""
                break
        filtered_email += buffer
        return filtered_email


class FSM:
    def __init__(
        self,
        states: List[str],
        transitions: List[Transition],
        start_state: int,
        accept_states: List[int],
    ):
        self._states = set(states)
        self._transitions: Dict[Tuple[str, int], int] = {}
        self._start_state: int = start_state
        self._accept_state = set(accept_states)

        self.current_state: int = self._start_state

        if start_state not in self._states:
            raise ValueError(f"Invalid start state: {start_state}")

        for transition in transitions:
            self._validate_and_add_transition(transition)

    def _validate_and_add_transition(self, transition: Transition) -> None:
        present, condition, next_state = (
            transition.present,
            transition.condition,
            transition._next,
        )

        if present not in self._states:
            raise ValueError(f"Invalid present state: {present}")

        if next_state not in self._states:
            raise ValueError(f"Invalid next state: {next_state}")

        if (present, condition) in self._transitions:
            raise ValueError(
                f"Duplicate transition for {(present, condition)}" f" -> {next_state}"
            )
        self._transitions[(present, condition)] = next_state

    def is_accept_state(self) -> bool:
        return self.current_state in self._accept_state

    def is_start_state(self) -> bool:
        return self.current_state == self._start_state

    def reset(self) -> None:
        self.current_state = self._start_state

    def process(self, condition: int) -> None:
        if (self.current_state, condition) in self._transitions:
            self.current_state = self._transitions[(
                self.current_state, condition)]
