# Transmuter front-end, front-end libraries and utilities for the
# Transmuter language processing infrastructure
# Copyright (C) 2024  Natan Junges <natanajunges@gmail.com>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

from ..common import TransmuterCondition
from ..syntactic import transmuter_once, TransmuterNonterminalType, TransmuterParsingState, TransmuterParser, TransmuterSymbolMatchError
from .common import lexical, syntactic
from .lexical import Whitespace, Identifier, Colon, Semicolon, CommercialAt, LeftParenthesis, RightParenthesis, VerticalLine, Solidus, DoubleVerticalLine, Comma, DoubleAmpersand, PlusSign, HyphenMinus, Ignore, Start, Asterisk, QuestionMark, ExpressionRange, LeftCurlyBracket, LeftCurlyBracketSolidus, RightCurlyBracket, OrdChar, QuotedChar, FullStop, BracketExpression, ExclamationMark, LeftSquareBracket, LeftSquareBracketSolidus, RightSquareBracket


class Grammar(TransmuterNonterminalType):
    @staticmethod
    def start(conditions: set[type[TransmuterCondition]]) -> bool:
        return True

    @classmethod
    def descend(cls, parser: TransmuterParser, current_state: TransmuterParsingState) -> set[TransmuterParsingState]:
        next_states0 = {current_state}
        next_states0 = parser.call(Production, next_states0)

        while True:  # begin iteration
            next_states1 = next_states0

            try:
                next_states1 = parser.call(Production, next_states1)
            except TransmuterSymbolMatchError:
                break

            next_states0 = next_states1  # end iteration

        return next_states0


class Production(TransmuterNonterminalType):
    @classmethod
    def descend(cls, parser: TransmuterParser, current_state: TransmuterParsingState) -> set[TransmuterParsingState]:
        next_states0 = {current_state}
        next_states0 = parser.call(ProductionHeader, next_states0)
        next_states0 = parser.call(ProductionBody, next_states0)
        return next_states0


class ProductionHeader(TransmuterNonterminalType):
    @classmethod
    def descend(cls, parser: TransmuterParser, current_state: TransmuterParsingState) -> set[TransmuterParsingState]:
        next_states0 = {current_state}
        next_states0 = parser.call(Identifier, next_states0)

        if lexical in parser.lexer.conditions:  # begin conditional optional
            next_states1 = next_states0

            try:
                next_states1 = parser.call(Condition, next_states1)
            except TransmuterSymbolMatchError:
                pass
            else:
                next_states0 = next_states1  # end conditional optional

        try:  # begin optional
            next_states1 = next_states0
            next_states1 = parser.call(ProductionSpecifiers, next_states1)
        except TransmuterSymbolMatchError:
            pass
        else:
            next_states0 = next_states1  # end optional

        next_states0 = parser.call(Colon, next_states0)
        return next_states0


class ProductionBody(TransmuterNonterminalType):
    @classmethod
    def descend(cls, parser: TransmuterParser, current_state: TransmuterParsingState) -> set[TransmuterParsingState]:
        next_states0 = {current_state}
        next_states0 = parser.call(SelectionExpression, next_states0)
        next_states0 = parser.call(Semicolon, next_states0)
        return next_states0


class Condition(TransmuterNonterminalType):
    @classmethod
    def descend(cls, parser: TransmuterParser, current_state: TransmuterParsingState) -> set[TransmuterParsingState]:
        next_states0 = {current_state}
        next_states0 = parser.call(CommercialAt, next_states0)
        next_states0 = parser.call(DisjunctionCondition, next_states0)
        return next_states0


class ProductionSpecifiers(TransmuterNonterminalType):
    @classmethod
    def descend(cls, parser: TransmuterParser, current_state: TransmuterParsingState) -> set[TransmuterParsingState]:
        next_states0 = {current_state}
        next_states0 = parser.call(LeftParenthesis, next_states0)
        next_states0 = parser.call(ProductionSpecifierList, next_states0)
        next_states0 = parser.call(RightParenthesis, next_states0)
        return next_states0


class SelectionExpression(TransmuterNonterminalType):
    @classmethod
    def descend(cls, parser: TransmuterParser, current_state: TransmuterParsingState) -> set[TransmuterParsingState]:
        next_states0 = {current_state}
        next_states0 = parser.call(SequenceExpression, next_states0)

        while True:  # begin iteration
            next_states1 = next_states0

            try:
                while transmuter_once:  # begin selection
                    try:  # begin option 1
                        next_states2 = next_states1
                        next_states2 = parser.call(VerticalLine, next_states2)
                    except TransmuterSymbolMatchError:
                        pass
                    else:
                        next_states1 = next_states2
                        break  # end option 1

                    if syntactic in parser.lexer.conditions:  # begin conditional option 2
                        next_states2 = next_states1

                        try:
                            next_states2 = parser.call(Solidus, next_states2)
                        except TransmuterSymbolMatchError:
                            pass
                        else:
                            next_states1 = next_states2
                            break  # end conditional option 2

                    raise TransmuterSymbolMatchError()  # end selection

                next_states1 = parser.call(SequenceExpression, next_states1)
            except TransmuterSymbolMatchError:
                break

            next_states0 = next_states1  # end iteration

        return next_states0


class DisjunctionCondition(TransmuterNonterminalType):
    @classmethod
    def descend(cls, parser: TransmuterParser, current_state: TransmuterParsingState) -> set[TransmuterParsingState]:
        next_states0 = {current_state}
        next_states0 = parser.call(ConjunctionCondition, next_states0)

        while True:  # begin iteration
            next_states1 = next_states0

            try:
                next_states1 = parser.call(DoubleVerticalLine, next_states1)
                next_states1 = parser.call(ConjunctionCondition, next_states1)
            except TransmuterSymbolMatchError:
                break

            next_states0 = next_states1  # end iteration

        return next_states0


class ProductionSpecifierList(TransmuterNonterminalType):
    @classmethod
    def descend(cls, parser: TransmuterParser, current_state: TransmuterParsingState) -> set[TransmuterParsingState]:
        next_states0 = {current_state}
        next_states0 = parser.call(ProductionSpecifier, next_states0)

        while True:  # begin iteration
            next_states1 = next_states0

            try:
                next_states1 = parser.call(Comma, next_states1)
                next_states1 = parser.call(ProductionSpecifier, next_states1)
            except TransmuterSymbolMatchError:
                break

            next_states0 = next_states1  # end iteration

        return next_states0


class SequenceExpression(TransmuterNonterminalType):
    @classmethod
    def descend(cls, parser: TransmuterParser, current_state: TransmuterParsingState) -> set[TransmuterParsingState]:
        next_states0 = {current_state}

        while transmuter_once:  # begin selection
            if lexical in parser.lexer.conditions:  # begin conditional option 1
                next_states1 = next_states0

                try:
                    next_states1 = parser.call(IterationExpression, next_states1)

                    while True:  # begin iteration
                        next_states2 = next_states1

                        try:
                            next_states2 = parser.call(IterationExpression, next_states2)
                        except TransmuterSymbolMatchError:
                            break

                        next_states1 = next_states2  # end iteration
                except TransmuterSymbolMatchError:
                    pass
                else:
                    next_states0 = next_states1
                    break  # end conditional option 1

            if syntactic in parser.lexer.conditions:  # begin conditional option 2
                next_states1 = next_states0

                try:
                    next_states1 = parser.call(PrimaryExpression, next_states1)

                    while True:  # begin iteration
                        next_states2 = next_states1

                        try:
                            next_states2 = parser.call(PrimaryExpression, next_states2)
                        except TransmuterSymbolMatchError:
                            break

                        next_states1 = next_states2  # end iteration
                except TransmuterSymbolMatchError:
                    pass
                else:
                    next_states0 = next_states1
                    break  # end conditional option 2

            raise TransmuterSymbolMatchError()  # end selection

        return next_states0


class ConjunctionCondition(TransmuterNonterminalType):
    @classmethod
    def descend(cls, parser: TransmuterParser, current_state: TransmuterParsingState) -> set[TransmuterParsingState]:
        next_states0 = {current_state}
        next_states0 = parser.call(NegationCondition, next_states0)

        while True:  # begin iteration
            next_states1 = next_states0

            try:
                next_states1 = parser.call(DoubleAmpersand, next_states1)
                next_states1 = parser.call(NegationCondition, next_states1)
            except TransmuterSymbolMatchError:
                break

            next_states0 = next_states1  # end iteration

        return next_states0


class ProductionSpecifier(TransmuterNonterminalType):
    @classmethod
    def descend(cls, parser: TransmuterParser, current_state: TransmuterParsingState) -> set[TransmuterParsingState]:
        next_states0 = {current_state}

        while transmuter_once:  # begin selection
            if lexical in parser.lexer.conditions:  # begin conditional option 1
                next_states1 = next_states0

                try:
                    while transmuter_once:  # begin selection
                        try:  # begin option 1
                            next_states2 = next_states1

                            while transmuter_once:  # begin selection
                                try:  # begin option 1
                                    next_states3 = next_states2
                                    next_states3 = parser.call(PlusSign, next_states3)
                                except TransmuterSymbolMatchError:
                                    pass
                                else:
                                    next_states2 = next_states3
                                    break  # end option 1

                                try:  # begin option 2
                                    next_states3 = next_states2
                                    next_states3 = parser.call(HyphenMinus, next_states3)
                                except TransmuterSymbolMatchError:
                                    pass
                                else:
                                    next_states2 = next_states3
                                    break  # end option 2

                                raise TransmuterSymbolMatchError()  # end selection

                            next_states2 = parser.call(Identifier, next_states2)
                        except TransmuterSymbolMatchError:
                            pass
                        else:
                            next_states1 = next_states2
                            break  # end option 1

                        try:  # begin option 2
                            next_states2 = next_states1
                            next_states2 = parser.call(Ignore, next_states2)
                        except TransmuterSymbolMatchError:
                            pass
                        else:
                            next_states1 = next_states2
                            break  # end option 2

                        raise TransmuterSymbolMatchError()  # end selection
                except TransmuterSymbolMatchError:
                    pass
                else:
                    next_states0 = next_states1
                    break  # end conditional option 1

            if syntactic in parser.lexer.conditions:  # begin conditional option 2
                next_states1 = next_states0

                try:
                    next_states1 = parser.call(Start, next_states1)
                except TransmuterSymbolMatchError:
                    pass
                else:
                    next_states0 = next_states1
                    break  # end conditional option 2

            raise TransmuterSymbolMatchError()  # end selection

        try:  # begin optional
            next_states1 = next_states0
            next_states1 = parser.call(Condition, next_states1)
        except TransmuterSymbolMatchError:
            pass
        else:
            next_states0 = next_states1  # end optional

        return next_states0


class IterationExpression(TransmuterNonterminalType):
    @classmethod
    def descend(cls, parser: TransmuterParser, current_state: TransmuterParsingState) -> set[TransmuterParsingState]:
        next_states0 = {current_state}

        while transmuter_once:  # begin selection
            if lexical in parser.lexer.conditions:  # begin conditional option 1
                next_states1 = next_states0

                try:
                    next_states1 = parser.call(PrimaryExpression, next_states1)

                    while transmuter_once:  # begin optional selection
                        try:  # begin option 1
                            next_states2 = next_states1
                            next_states2 = parser.call(Asterisk, next_states2)
                        except TransmuterSymbolMatchError:
                            pass
                        else:
                            next_states1 = next_states2
                            break  # end option 1

                        try:  # begin option 2
                            next_states2 = next_states1
                            next_states2 = parser.call(PlusSign, next_states2)
                        except TransmuterSymbolMatchError:
                            pass
                        else:
                            next_states1 = next_states2
                            break  # end option 2

                        try:  # begin option 3
                            next_states2 = next_states1
                            next_states2 = parser.call(QuestionMark, next_states2)
                        except TransmuterSymbolMatchError:
                            pass
                        else:
                            next_states1 = next_states2
                            break  # end option 3

                        try:  # begin option 4
                            next_states2 = next_states1
                            next_states2 = parser.call(ExpressionRange, next_states2)
                        except TransmuterSymbolMatchError:
                            pass
                        else:
                            next_states1 = next_states2
                            break  # end option 4

                        break  # end optional selection
                except TransmuterSymbolMatchError:
                    pass
                else:
                    next_states0 = next_states1
                    break  # end conditional option 1

            if syntactic in parser.lexer.conditions:  # begin conditional option 2
                next_states1 = next_states0

                try:
                    while transmuter_once:  # begin selection
                        try:  # begin option 1
                            next_states2 = next_states1
                            next_states2 = parser.call(LeftCurlyBracket, next_states2)
                        except TransmuterSymbolMatchError:
                            pass
                        else:
                            next_states1 = next_states2
                            break  # end option 1

                        try:  # begin option 2
                            next_states2 = next_states1
                            next_states2 = parser.call(LeftCurlyBracketSolidus, next_states2)
                        except TransmuterSymbolMatchError:
                            pass
                        else:
                            next_states1 = next_states2
                            break  # end option 2

                        raise TransmuterSymbolMatchError()  # end selection

                    next_states1 = parser.call(SelectionExpression, next_states1)
                    next_states1 = parser.call(RightCurlyBracket, next_states1)
                except TransmuterSymbolMatchError:
                    pass
                else:
                    next_states0 = next_states1
                    break  # end conditional option 2

            raise TransmuterSymbolMatchError()  # end selection

        return next_states0


class PrimaryExpression(TransmuterNonterminalType):
    @classmethod
    def descend(cls, parser: TransmuterParser, current_state: TransmuterParsingState) -> set[TransmuterParsingState]:
        next_states0 = {current_state}

        while transmuter_once:  # begin selection
            if lexical in parser.lexer.conditions:  # begin conditional option 1
                next_states1 = next_states0

                try:
                    while transmuter_once:  # begin selection
                        try:  # begin option 1
                            next_states2 = next_states1
                            next_states2 = parser.call(OrdChar, next_states2)
                        except TransmuterSymbolMatchError:
                            pass
                        else:
                            next_states1 = next_states2
                            break  # end option 1

                        try:  # begin option 2
                            next_states2 = next_states1
                            next_states2 = parser.call(QuotedChar, next_states2)
                        except TransmuterSymbolMatchError:
                            pass
                        else:
                            next_states1 = next_states2
                            break  # end option 2

                        try:  # begin option 3
                            next_states2 = next_states1
                            next_states2 = parser.call(FullStop, next_states2)
                        except TransmuterSymbolMatchError:
                            pass
                        else:
                            next_states1 = next_states2
                            break  # end option 3

                        try:  # begin option 4
                            next_states2 = next_states1
                            next_states2 = parser.call(BracketExpression, next_states2)
                        except TransmuterSymbolMatchError:
                            pass
                        else:
                            next_states1 = next_states2
                            break  # end option 4

                        raise TransmuterSymbolMatchError()  # end selection
                except TransmuterSymbolMatchError:
                    pass
                else:
                    next_states0 = next_states1
                    break  # end conditional option 1

            if syntactic in parser.lexer.conditions:  # begin conditional option 2
                next_states1 = next_states0

                try:
                    next_states1 = parser.call(Identifier, next_states1)

                    try:  # begin optional
                        next_states2 = next_states1
                        next_states2 = parser.call(Condition, next_states2)
                    except TransmuterSymbolMatchError:
                        pass
                    else:
                        next_states1 = next_states2  # end optional
                except TransmuterSymbolMatchError:
                    pass
                else:
                    next_states0 = next_states1
                    break  # end conditional option 2

            try:  # begin option 3
                next_states1 = next_states0
                next_states1 = parser.call(LeftParenthesis, next_states1)
                next_states1 = parser.call(SelectionExpression, next_states1)
                next_states1 = parser.call(RightParenthesis, next_states1)

                if syntactic in parser.lexer.conditions:  # begin conditional optional
                    next_states2 = next_states1

                    try:
                        next_states2 = parser.call(Condition, next_states2)
                    except TransmuterSymbolMatchError:
                        pass
                    else:
                        next_states1 = next_states2  # end conditional optional
            except TransmuterSymbolMatchError:
                pass
            else:
                next_states0 = next_states1
                break  # end option 3

            if syntactic in parser.lexer.conditions:  # begin conditional option 4
                next_states1 = next_states0

                try:
                    while transmuter_once:  # begin selection
                        try:  # begin option 1
                            next_states2 = next_states1
                            next_states2 = parser.call(OptionalExpression, next_states2)
                        except TransmuterSymbolMatchError:
                            pass
                        else:
                            next_states1 = next_states2
                            break  # end option 1

                        try:  # begin option 2
                            next_states2 = next_states1
                            next_states2 = parser.call(IterationExpression, next_states2)
                        except TransmuterSymbolMatchError:
                            pass
                        else:
                            next_states1 = next_states2
                            break  # end option 2

                        raise TransmuterSymbolMatchError()  # end selection

                    try:  # begin optional
                        next_states2 = next_states1
                        next_states2 = parser.call(Condition, next_states2)
                    except TransmuterSymbolMatchError:
                        pass
                    else:
                        next_states1 = next_states2  # end optional
                except TransmuterSymbolMatchError:
                    pass
                else:
                    next_states0 = next_states1
                    break  # end conditional option 4

            raise TransmuterSymbolMatchError()  # end selection

        return next_states0


class NegationCondition(TransmuterNonterminalType):
    @classmethod
    def descend(cls, parser: TransmuterParser, current_state: TransmuterParsingState) -> set[TransmuterParsingState]:
        next_states0 = {current_state}

        while True:  # begin iteration
            next_states1 = next_states0

            try:
                next_states1 = parser.call(ExclamationMark, next_states1)
            except TransmuterSymbolMatchError:
                break

            next_states0 = next_states1  # end iteration

        next_states0 = parser.call(PrimitiveCondition, next_states0)
        return next_states0


class OptionalExpression(TransmuterNonterminalType):
    @classmethod
    def descend(cls, parser: TransmuterParser, current_state: TransmuterParsingState) -> set[TransmuterParsingState]:
        next_states0 = {current_state}

        while transmuter_once:  # begin selection
            try:  # begin option 1
                next_states1 = next_states0
                next_states1 = parser.call(LeftSquareBracket, next_states1)
            except TransmuterSymbolMatchError:
                pass
            else:
                next_states0 = next_states1
                break  # end option 1

            try:  # begin option 2
                next_states1 = next_states0
                next_states1 = parser.call(LeftSquareBracketSolidus, next_states1)
            except TransmuterSymbolMatchError:
                pass
            else:
                next_states0 = next_states1
                break  # end option 2

            raise TransmuterSymbolMatchError()  # end selection

        next_states0 = parser.call(SelectionExpression, next_states0)
        next_states0 = parser.call(RightSquareBracket, next_states0)
        return next_states0


class PrimitiveCondition(TransmuterNonterminalType):
    @classmethod
    def descend(cls, parser: TransmuterParser, current_state: TransmuterParsingState) -> set[TransmuterParsingState]:
        next_states0 = {current_state}

        while transmuter_once:  # begin selection
            try:  # begin option 1
                next_states1 = next_states0
                next_states1 = parser.call(Identifier, next_states1)
            except TransmuterSymbolMatchError:
                pass
            else:
                next_states0 = next_states1
                break  # end option 1

            try:  # begin option 2
                next_states1 = next_states0
                next_states1 = parser.call(LeftParenthesis, next_states1)
                next_states1 = parser.call(DisjunctionCondition, next_states1)
                next_states1 = parser.call(RightParenthesis, next_states1)
            except TransmuterSymbolMatchError:
                pass
            else:
                next_states0 = next_states1
                break  # end option 2

            raise TransmuterSymbolMatchError()  # end selection

        return next_states0


class Parser(TransmuterParser):
    NONTERMINAL_TYPES = {Grammar, Production, ProductionHeader, ProductionBody, Condition, ProductionSpecifiers, SelectionExpression, DisjunctionCondition, ProductionSpecifierList, SequenceExpression, ConjunctionCondition, ProductionSpecifier, IterationExpression, PrimaryExpression, NegationCondition, OptionalExpression, PrimitiveCondition}
