from infrastructure.services.code_generator import RandomCodeGenerator


def test_default_length_is_six():
    gen = RandomCodeGenerator()

    code = gen.generate()

    assert len(code) == 6


def test_custom_length():
    gen = RandomCodeGenerator()

    assert len(gen.generate(length=4)) == 4
    assert len(gen.generate(length=8)) == 8


def test_contains_only_digits():
    gen = RandomCodeGenerator()

    for _ in range(20):
        code = gen.generate()
        assert code.isdigit()


def test_generates_unique_codes():
    gen = RandomCodeGenerator()
    codes = {gen.generate() for _ in range(50)}

    assert len(codes) > 1
