from typing import Any, Callable, Dict, List, Literal, Tuple, Union

from prompt_toolkit.formatted_text import FormattedText

NoneType = type(None)
ARGS_AND_KWARGS = Tuple[Tuple[Any, ...], Dict[str, Any]]
CALLABLE_ERR_HANDLER = Callable[[str, BaseException, str, str], Any]
PromptLikeMsg = Union[str, FormattedText, Callable[..., Union[FormattedText, List[Tuple[str, str]]]]]
LITERAL_EVENTS = Literal[
    "start", "close", "kb_interrupt", "eof", "command_not_found", "command_complete", "command_suggest"
]
