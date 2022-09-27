from algorithms.base import TokenBasedAlgorithm, NewSequenceResult
from tokens import Token, TokenSeq, DigitToken


class XReplace(TokenBasedAlgorithm[NewSequenceResult]):
    def parse_by_tokens(self, token_seq: TokenSeq) -> NewSequenceResult:
        seps_to_replace = set('*')
        values_to_replace = set('xXхХ')
        target_sep = '×'

        seps = token_seq.seps
        for i, (t1, t2) in token_seq.iter_pairwise():
            if isinstance(t1, DigitToken) and isinstance(t2, DigitToken) and token_seq.seps[i + 1] in seps_to_replace:
                seps[i + 1] = target_sep

        # seperate
        new_tokens: list[Token] = []
        new_seps: list[str] = [seps[0]]

        for context, token in token_seq.iter_with_context():
            is_digits_around = (context.prev
                                and isinstance(context.prev, DigitToken)
                                and context.next
                                and isinstance(context.next, DigitToken))
            if (is_digits_around and token.value in values_to_replace):
                new_seps.pop()
                new_seps.append(target_sep)
            else:
                new_tokens.append(token)
                new_seps.append(context.right_sep)

        return NewSequenceResult(TokenSeq(new_tokens, new_seps))
