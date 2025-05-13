import pytest
import libclicker
import time
import string

def test_move_mouse():
    # Test moving mouse to different positions
    try:
        libclicker.move_mouse(100, 100)
        libclicker.move_mouse(0, 0)
        libclicker.move_mouse(-100, -100)
        assert True  # If no exception is raised
    except Exception as e:
        pytest.fail(f"move_mouse raised {e} unexpectedly!")

def test_click():
    # Test different click types
    try:
        # Test left click
        libclicker.click(100, 100, btn=0, count=1)
        # Test middle click
        libclicker.click(100, 100, btn=1, count=1)
        # Test right click
        libclicker.click(100, 100, btn=2, count=1)
    except Exception as e:
        pytest.fail(f"click raised {e} unexpectedly!")

    # Test invalid inputs
    with pytest.raises(ValueError):
        libclicker.click(100, 100, btn=3)  # Invalid button
    with pytest.raises(ValueError):
        libclicker.click(100, 100, count=4)  # Invalid count

def test_scroll():
    # Test scrolling in different directions
    try:
        libclicker.scroll(100, 100, count=1, direction='up')
        libclicker.scroll(100, 100, count=1, direction='down')
        libclicker.scroll(100, 100, count=1, direction='left')
        libclicker.scroll(100, 100, count=1, direction='right')
    except Exception as e:
        pytest.fail(f"scroll raised {e} unexpectedly!")

    # Test invalid inputs
    with pytest.raises(ValueError):
        libclicker.scroll(100, 100, count=1, direction='invalid')

def test_press_key():
    # Test different types of keys
    try:
        # Test lowercase
        libclicker.press_key('a')
        # Test uppercase
        libclicker.press_key('A')
        # Test number
        libclicker.press_key('1')
        # Test symbol
        libclicker.press_key('!')
        # Test punctuation
        libclicker.press_key('.')
        # Test space
        libclicker.press_key(' ')
        # Test tab
        libclicker.press_key('\t')
        # Test enter
        libclicker.press_key('\n')
    except Exception as e:
        pytest.fail(f"press_key raised {e} unexpectedly!")

    # Test invalid inputs
    with pytest.raises(ValueError):
        libclicker.press_key('invalid')  # More than one character
    with pytest.raises(ValueError):
        libclicker.press_key('☺')  # Non-printable character

def test_type_text():
    # Test typing different strings
    try:
        libclicker.type_text("Hello World!")
        libclicker.type_text("123")
        libclicker.type_text("!@#$%")
    except Exception as e:
        pytest.fail(f"type_text raised {e} unexpectedly!")

    # Test invalid input
    with pytest.raises(ValueError):
        libclicker.type_text("Hello ☺")  # Contains non-printable character
    with pytest.raises(ValueError):
        libclicker.type_text(123)  # Not a string

if __name__ == '__main__':
    pytest.main([__file__])