# This file is part of the Alchemist front-end libraries
# Copyright (C) 2023  Natan Junges <natanajunges@gmail.com>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
# The code generated by this library is also under the GNU General Public
# License.

from typing import Union, TypeVar, Generic

_RuleTemplate = Union["_RuleTemplates", "_Rule", str]
_RuleTemplates = tuple[_RuleTemplate, ...] | list[_RuleTemplate]
_T = TypeVar("_T", list["_Rule"], "_Group", str)


class _Rule(Generic[_T]):
    @staticmethod
    def _filter(templates: _RuleTemplates) -> list["_Rule"]:
        rules: list[_Rule] = [_Rule.get(template) for template in templates if not isinstance(template, Switch) or template.enabled]
        rules = [rule for rule in rules if isinstance(rule, _Symbol) or len(rule.rules.rules if isinstance(rule.rules, _Group) else rule.rules) > 0]
        return rules

    @staticmethod
    def get(template: _RuleTemplate) -> "_Rule":
        if isinstance(template, tuple):
            return _Group(template)

        if isinstance(template, list):
            return _Optional(template)

        if isinstance(template, str):
            return _Symbol(template)

        return template

    def __init__(self, rules: _T) -> None:
        self.rules: _T = rules

    def __call__(self, indent: int, level: int, ambiguous: bool) -> str:
        raise NotImplementedError()


class _Group(_Rule[list[_Rule]]):
    def __init__(self, templates: _RuleTemplates) -> None:
        super().__init__(self._filter(templates))

    def __call__(self, indent: int, level: int, ambiguous: bool) -> str:
        code: str = ""

        for rule in self.rules:
            code += rule(indent, level, ambiguous)

        return code


class _Optional(_Rule[_Group]):
    def __init__(self, templates: list[_RuleTemplate]) -> None:
        super().__init__(_Group(templates))

    def __call__(self, indent: int, level: int, ambiguous: bool) -> str:
        code: str = "\n"
        code += f"\n{'    ' * indent}try:  # optional"
        code += f"\n{'    ' * (indent + 1)}paths{level + 1} = paths{level}"
        code += self.rules(indent + 1, level + 1, ambiguous)

        if ambiguous:
            code += f"\n{'    ' * (indent + 1)}GraphNode.merge_paths(paths{level}, paths{level + 1})"
        else:
            code += f"\n{'    ' * (indent + 1)}paths{level} = paths{level + 1}"

        code += f"\n{'    ' * indent}except (CompilerSyntaxError, CompilerEOIError):"
        code += f"\n{'    ' * (indent + 1)}pass"
        code += "\n"
        return code


class Switch(_Rule[_Group]):
    enabled: bool = False

    def __init__(self, *templates: _RuleTemplate) -> None:
        super().__init__(_Group(templates))

    def __call__(self, indent: int, level: int, ambiguous: bool) -> str:
        return self.rules(indent, level, ambiguous)


class repeat(_Rule[_Group]):  # pylint: disable=C0103
    def __init__(self, *templates: _RuleTemplate) -> None:
        super().__init__(_Group(templates))

    def __call__(self, indent: int, level: int, ambiguous: bool) -> str:
        code: str = "\n"
        code += f"\n{'    ' * indent}paths{level + 1} = paths{level}"
        code += "\n"
        code += f"\n{'    ' * indent}while True:  # repeat"
        code += f"\n{'    ' * (indent + 1)}try:"
        code += self.rules(indent + 2, level + 1, ambiguous)

        if ambiguous:
            code += f"\n{'    ' * (indent + 2)}GraphNode.merge_paths(paths{level}, paths{level + 1})"
        else:
            code += f"\n{'    ' * (indent + 2)}paths{level} = paths{level + 1}"

        code += f"\n{'    ' * (indent + 1)}except (CompilerSyntaxError, CompilerEOIError):"
        code += f"\n{'    ' * (indent + 2)}break"
        code += "\n"
        return code


class oneof(_Rule[list[_Rule]]):  # pylint: disable=C0103
    def __init__(self, *templates: _RuleTemplate) -> None:
        super().__init__(self._filter(templates))

    def __call__(self, indent: int, level: int, ambiguous: bool) -> str:
        if len(self.rules) == 1:
            return self.rules[0](indent, level, ambiguous)

        code: str = "\n"
        code += f"\n{'    ' * indent}# begin oneof"
        code += f"\n{'    ' * indent}paths{level + 1}: Paths = {{}}"

        if not ambiguous:
            code += "\n"
            code += f"\n{'    ' * indent}with suppress(BreakException):"

        for i, rule in enumerate(self.rules):
            code += "\n"
            code += f"\n{'    ' * (indent + int(not ambiguous))}try:  # option {i + 1}"
            code += f"\n{'    ' * (indent + 1 + int(not ambiguous))}paths{level + 2} = paths{level}"
            code += rule(indent + 1 + int(not ambiguous), level + 2, ambiguous)

            if ambiguous:
                code += f"\n{'    ' * (indent + 1)}GraphNode.merge_paths(paths{level + 1}, paths{level + 2})"
            else:
                code += f"\n{'    ' * (indent + 2)}paths{level + 1} = paths{level + 2}"

            if not ambiguous:
                code += f"\n{'    ' * (indent + 2)}assert len(paths{level + 1}) != 0"
                code += f"\n{'    ' * (indent + 2)}raise BreakException()"

            code += (
                f"\n{'    ' * (indent + int(not ambiguous))}except (CompilerSyntaxError, CompilerEOIError{'' if ambiguous else ', AssertionError'}):"
            )
            code += f"\n{'    ' * (indent + 1 + int(not ambiguous))}pass"

        code += "\n"

        if ambiguous:
            code += f"\n{'    ' * indent}if len(paths{level + 1}) == 0:"

        code += f"\n{'    ' * (indent + 1)}raise CompilerNoPathError(self)"
        code += "\n"
        code += f"\n{'    ' * indent}paths{level} = paths{level + 1}"
        code += f"\n{'    ' * indent}# end oneof"
        code += "\n"
        return code


class _Symbol(_Rule[str]):
    def __init__(self, symbol: str) -> None:
        super().__init__(symbol)

    def __call__(self, indent: int, level: int, ambiguous: bool) -> str:
        return f"\n{'    ' * indent}paths{level} = self._process_paths(paths{level}, {self.rules})"


class ProductionTemplate:  # pylint: disable=R0903
    _template: _RuleTemplate = ()
    _left_recursive: bool = True
    _ambiguous: bool = True

    @classmethod
    def generate(cls) -> str:
        if isinstance(cls._template, Switch) and not cls._template.enabled:  # pylint: disable=E1101
            return ""

        rule: _Rule = _Rule.get(cls._template)

        if not isinstance(rule, _Symbol) and len(rule.rules.rules if isinstance(rule.rules, _Group) else rule.rules) == 0:
            return ""

        code: str = f"class {cls.__name__}(Production):"

        if not cls._left_recursive:
            code += "\n    _left_recursive = False"
            code += "\n"

        code += "\n    def _derive(self) -> None:"
        code += '\n        input_path = cast(GraphNode, self.input_path)'
        code += "\n        paths0: Paths = {input_path.path: {input_path}}"
        code += rule(2, 0, cls._ambiguous).replace("\n\n\n", "\n\n")
        code += "\n        self.output_paths = paths0"
        return code
