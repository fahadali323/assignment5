import pytest
from unittest.mock import patch
from app.calculator_repl import calculator_repl
from app.exceptions import ValidationError


@patch('builtins.print')
@patch('app.calculator.Calculator.save_history', side_effect=Exception('disk error'))
@patch('builtins.input', side_effect=['exit'])
def test_repl_exit_save_error(mock_input, mock_save, mock_print):
    calculator_repl()
    # Should warn about save failure and still say goodbye
    mock_print.assert_any_call("Warning: Could not save history: disk error")
    mock_print.assert_any_call("Goodbye!")


@patch('builtins.print')
@patch('builtins.input', side_effect=['history', 'exit'])
@patch('app.calculator.Calculator.show_history', return_value=[])
def test_repl_history_empty(mock_show_history, mock_input, mock_print):
    calculator_repl()
    mock_print.assert_any_call("No calculations in history")


@patch('builtins.print')
@patch('builtins.input', side_effect=['history', 'exit'])
@patch('app.calculator.Calculator.show_history', return_value=['add(2, 3) = 5'])
def test_repl_history_nonempty(mock_show_history, mock_input, mock_print):
    calculator_repl()
    mock_print.assert_any_call("\nCalculation History:")
    mock_print.assert_any_call('1. add(2, 3) = 5')


@patch('builtins.print')
@patch('builtins.input', side_effect=['add', 'cancel', 'exit'])
def test_repl_cancel_first_number(mock_input, mock_print):
    calculator_repl()
    mock_print.assert_any_call("Operation cancelled")


@patch('builtins.print')
@patch('app.calculator.Calculator.perform_operation', side_effect=ValidationError('invalid input'))
@patch('builtins.input', side_effect=['add', '2', '3', 'exit'])
def test_repl_validation_error_during_operation(mock_input, mock_perform, mock_print):
    calculator_repl()
    mock_print.assert_any_call('Error: invalid input')


@patch('builtins.print')
@patch('builtins.input', side_effect=EOFError)
def test_repl_eof_terminates(mock_input, mock_print):
    # EOFError raised immediately should exit the REPL loop
    calculator_repl()
    mock_print.assert_any_call("\nInput terminated. Exiting...")


@patch('builtins.print')
@patch('app.calculator.Calculator.save_history')
@patch('builtins.input', side_effect=[KeyboardInterrupt, 'exit'])
def test_repl_keyboardinterrupt_then_exit(mock_input, mock_save, mock_print):
    calculator_repl()
    mock_print.assert_any_call("\nOperation cancelled")
    mock_print.assert_any_call("Goodbye!")


@patch('builtins.print')
@patch('builtins.input', side_effect=['help', 'exit'])
def test_repl_help_full(mock_input, mock_print):
    calculator_repl()
    # Ensure several help lines are printed
    mock_print.assert_any_call("\nAvailable commands:")
    mock_print.assert_any_call("  add, subtract, multiply, divide, power, root - Perform calculations")
    mock_print.assert_any_call("  exit - Exit the calculator")


@patch('builtins.print')
@patch('app.calculator.Calculator.clear_history')
@patch('builtins.input', side_effect=['clear', 'exit'])
def test_repl_clear(mock_input, mock_clear, mock_print):
    calculator_repl()
    mock_clear.assert_called_once()
    mock_print.assert_any_call("History cleared")


@patch('builtins.print')
@patch('app.calculator.Calculator.undo', return_value=False)
@patch('builtins.input', side_effect=['undo', 'exit'])
def test_repl_undo_nothing(mock_input, mock_undo, mock_print):
    calculator_repl()
    mock_print.assert_any_call("Nothing to undo")


@patch('builtins.print')
@patch('app.calculator.Calculator.undo', return_value=True)
@patch('builtins.input', side_effect=['undo', 'exit'])
def test_repl_undo_success(mock_input, mock_undo, mock_print):
    calculator_repl()
    mock_print.assert_any_call("Operation undone")


@patch('builtins.print')
@patch('app.calculator.Calculator.redo', return_value=False)
@patch('builtins.input', side_effect=['redo', 'exit'])
def test_repl_redo_nothing(mock_input, mock_redo, mock_print):
    calculator_repl()
    mock_print.assert_any_call("Nothing to redo")


@patch('builtins.print')
@patch('app.calculator.Calculator.redo', return_value=True)
@patch('builtins.input', side_effect=['redo', 'exit'])
def test_repl_redo_success(mock_input, mock_redo, mock_print):
    calculator_repl()
    mock_print.assert_any_call("Operation redone")


@patch('builtins.print')
@patch('app.calculator.Calculator.save_history')
@patch('builtins.input', side_effect=['save', 'exit'])
def test_repl_save_success(mock_input, mock_save, mock_print):
    calculator_repl()
    # Calculator.__init__ may call load/save during setup; just ensure save was called
    mock_save.assert_called()
    mock_print.assert_any_call("History saved successfully")


@patch('builtins.print')
@patch('app.calculator.Calculator.save_history', side_effect=Exception('disk full'))
@patch('builtins.input', side_effect=['save', 'exit'])
def test_repl_save_error(mock_input, mock_save, mock_print):
    calculator_repl()
    mock_print.assert_any_call('Error saving history: disk full')


@patch('builtins.print')
@patch('app.calculator.Calculator.load_history')
@patch('builtins.input', side_effect=['load', 'exit'])
def test_repl_load_success(mock_input, mock_load, mock_print):
    calculator_repl()
    # Calculator.__init__ may call load during setup; just ensure load was called
    mock_load.assert_called()
    mock_print.assert_any_call("History loaded successfully")


@patch('builtins.print')
@patch('app.calculator.Calculator.load_history', side_effect=Exception('bad file'))
@patch('builtins.input', side_effect=['load', 'exit'])
def test_repl_load_error(mock_input, mock_load, mock_print):
    calculator_repl()
    mock_print.assert_any_call('Error loading history: bad file')


@patch('builtins.print')
@patch('builtins.input', side_effect=['add', '2', 'cancel', 'exit'])
def test_repl_cancel_second_number(mock_input, mock_print):
    calculator_repl()
    mock_print.assert_any_call("Operation cancelled")


@patch('builtins.print')
@patch('app.calculator.Calculator.perform_operation', side_effect=Exception('boom'))
@patch('builtins.input', side_effect=['add', '2', '3', 'exit'])
def test_repl_unexpected_exception_in_operation(mock_input, mock_perform, mock_print):
    calculator_repl()
    mock_print.assert_any_call('Unexpected error: boom')


@patch('builtins.print')
@patch('app.calculator_repl.Calculator', side_effect=Exception('init fail'))
def test_repl_fatal_init_exception(mock_calc, mock_print):
    with pytest.raises(Exception, match='init fail'):
        calculator_repl()
    mock_print.assert_any_call('Fatal error: init fail')


@patch('builtins.print')
@patch('builtins.input', side_effect=['foobar', 'exit'])
def test_repl_unknown_command(mock_input, mock_print):
    calculator_repl()
    mock_print.assert_any_call("Unknown command: 'foobar'. Type 'help' for available commands.")


@patch('builtins.print')
@patch('builtins.input', side_effect=[Exception('pop'), 'exit'])
def test_repl_inner_generic_exception(mock_input, mock_print):
    # First input raises a generic Exception, should be caught and printed
    calculator_repl()
    mock_print.assert_any_call('Error: pop')
