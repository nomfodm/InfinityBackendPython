import random
import string

from domain.interfaces.services.code_generator import CodeGenerator


class DigitCodeGenerator(CodeGenerator):
    def generate(self, length: int = 6) -> str:
        return "".join(random.choices(string.digits, k=length))
