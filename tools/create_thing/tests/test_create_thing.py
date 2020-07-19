from create_thing.create_thing import string_as_c_literal


def test_string_as_c_literal():
    assert '"line 1\\n"\n"line 2\\n"' == string_as_c_literal( "line 1\nline 2" )

