from io import StringIO
from algorithms.base import TokenBasedAlgorithm, NewSequenceResult
from tokens import Token, TokenSeq, DigitToken


class Number(Token):
    pass


class NumbersMerge(TokenBasedAlgorithm[NewSequenceResult]):
    def parse_by_tokens(self, seq: TokenSeq) -> NewSequenceResult:
        """
        {sep0}{digit}({sep1}{digit})*{sep2}
        """
        def sep2(sep):
            return True

        def sep1(sep):
            return sep in set('×-,./')

        def sep0(sep):
            return ' ' in sep

        cont = False
        chanks: list[tuple[int, int]] = []
        chank_start = None
        for context, token in seq.iter_with_context():
            if cont:
                if isinstance(token, DigitToken) and sep1(context.left_sep):
                    continue
                elif sep2(context.left_sep):
                    chanks.append((chank_start, context.token_index))
                    cont = False
                    chank_start = None
            if not cont:
                if isinstance(token, DigitToken) and sep0(context.left_sep):
                    cont = True
                    chank_start = context.token_index

        # merge
        new_tokens = []
        new_seps = []
        near_chank = chanks.pop(0) if len(chanks) else None

        token_value = StringIO()
        for context, token in seq.iter_with_context():
            if near_chank and (near_chank[0] <= context.token_index <= near_chank[1] - 1):
                not_first = near_chank[0] != context.token_index
                is_last = context.token_index == near_chank[1] - 1

                if not_first:
                    token_value.write(context.left_sep)

                token_value.write(token.value)

                if is_last:
                    new_tokens.append(Number(token_value.getvalue()))
                    token_value = StringIO()
                    near_chank = chanks.pop(0) if len(chanks) else None
            else:
                new_seps.append(context.left_sep)
                new_tokens.append(token)
        new_seps.append(seq.seps[-1])
        return NewSequenceResult(TokenSeq(new_tokens, new_seps))
