from functools import reduce
from re import compile
from typing import Optional, cast

from denite import process
from denite.source.base import Base
from denite.util import Nvim, UserContext, Candidates

parse_re = compile(r"\[(\d+)\] (.*)")


class Source(Base):
    def __init__(self, vim: Nvim):
        super().__init__(vim)

        self.name = "nb"

    def on_init(self, context: UserContext) -> None:
        self.__set_proc(context, None)

    def gather_candidates(self, context: UserContext) -> Candidates:
        exe = self.vim.call("denite#nb#executable")
        if not exe:
            return []

        if self.__proc(context):
            return self.__async_gather_candidates(context, context["async_timeout"])

        proc = process.Process(
            [exe, "--no-color", "ls", "-asr"], context, context["path"]
        )
        self.__set_proc(context, proc)
        return self.__async_gather_candidates(context, context["async_timeout"])

    def __async_gather_candidates(
        self, context: UserContext, timeout: int
    ) -> Candidates:
        proc = self.__proc(context)
        if not proc:
            context["is_async"] = False
            return []
        outs, errs = proc.communicate(timeout=timeout)
        if errs:
            self.error_message(context, errs)
        context["is_async"] = not proc.eof()
        if proc.eof():
            self.__set_proc(context, None)

        def make_candidates(a: Candidates, b: str) -> Candidates:
            m = parse_re.match(b)
            if m:
                a += [
                    {
                        "word": m.group(2),
                        "abbr": f"{m.group(1)} {m.group(2)}",
                        "action__id": int(m.group(1)),
                    }
                ]
            return a

        return reduce(make_candidates, outs, [])

    def __proc(self, context: UserContext) -> Optional[process.Process]:
        return cast(process.Process, context["__proc"]) if context["__proc"] else None

    def __set_proc(self, context: UserContext, proc: Optional[process.Process]) -> None:
        context["__proc"] = proc
