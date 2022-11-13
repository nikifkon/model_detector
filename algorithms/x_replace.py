from algorithms.base import TokenBasedAlgorithm, NewSequenceResult
from tokens import Sep, TokenSeq, DigitToken


class XReplace(TokenBasedAlgorithm[NewSequenceResult]):
    """
    {DigitToken}({values_to_replace}){DigitToken}
    """
    values_to_replace = set('xXхХ*')

    def get_target(self):
        return Sep('×')

    def parse_by_tokens(self, token_seq: TokenSeq) -> NewSequenceResult:
        new_tokens = []
        gen = token_seq.generate_with_context()
        for context, token in gen:
            if token.value.lower() == 'св':  # TODO see other bugs
                new_tokens.append(token)
                context, token = gen.send(+1)
                if token.value == '-':
                    new_tokens.append(token)
                    context, token = gen.send(+1)
                    while not isinstance(token, Sep):
                        new_tokens.append(token)
                        context, token = gen.send(+1)
                    gen.send(-1)
                    continue
            if token.value in self.values_to_replace and isinstance(context.prev, DigitToken) and isinstance(context.next, DigitToken):
                new_tokens.append(self.get_target())
            else:
                new_tokens.append(token)
        return NewSequenceResult(TokenSeq(new_tokens))
