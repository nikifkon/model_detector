from algorithms.base import TokenBasedAlgorithm, NewSequenceResult
from tokens import Sep, TokenSeq, DigitToken


class XReplace(TokenBasedAlgorithm[NewSequenceResult]):
    """
    {DigitToken}({values_to_replace}){DigitToken}

    logs:
    - replaced_char
    """
    values_to_replace = set('xXхХ*')

    def get_target(self):
        return Sep('×')

    def parse_by_tokens(self, token_seq: TokenSeq) -> NewSequenceResult:
        new_tokens = []
        for context, token in token_seq.iter_with_context():
            if token.value in self.values_to_replace and isinstance(context.prev, DigitToken) and isinstance(context.next, DigitToken):
                new_tokens.append(self.get_target())
            else:
                new_tokens.append(token)
        return NewSequenceResult(None, TokenSeq(new_tokens))
