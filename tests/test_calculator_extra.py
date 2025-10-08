import logging
from pathlib import Path
from decimal import Decimal
from tempfile import TemporaryDirectory
from unittest.mock import patch, PropertyMock

import pandas as pd
import pytest

from app.calculator import Calculator, TransientFileHandler
from app.calculator_config import CalculatorConfig
from app.exceptions import OperationError
from app.calculation import Calculation


@pytest.fixture
def temp_config():
    with TemporaryDirectory() as td:
        base = Path(td)
        cfg = CalculatorConfig(base_dir=base)
        # Patch config paths to point inside temp dir
        with patch.object(CalculatorConfig, 'log_dir', new_callable=PropertyMock) as mock_log_dir, \
             patch.object(CalculatorConfig, 'log_file', new_callable=PropertyMock) as mock_log_file, \
             patch.object(CalculatorConfig, 'history_dir', new_callable=PropertyMock) as mock_history_dir, \
             patch.object(CalculatorConfig, 'history_file', new_callable=PropertyMock) as mock_history_file:
            mock_log_dir.return_value = base / 'logs'
            mock_log_file.return_value = base / 'logs' / 'calc.log'
            mock_history_dir.return_value = base / 'history'
            mock_history_file.return_value = base / 'history' / 'history.csv'
            yield cfg


def test_setup_logging_failure(temp_config):
    # Make the TransientFileHandler constructor raise to trigger the logging setup error path
    with patch('app.calculator.TransientFileHandler.__init__', side_effect=Exception('boom')):
        with pytest.raises(Exception, match='boom'):
            Calculator(config=temp_config)


def test_close_logging_idempotent(temp_config):
    calc = Calculator(config=temp_config)
    # Ensure file handler exists
    assert hasattr(calc, '_file_handler')
    calc.close_logging()
    # Closing again should be safe
    calc.close_logging()
    assert getattr(calc, '_file_handler', None) is None


@patch('app.calculator.pd.DataFrame.to_csv')
def test_save_history_empty_calls_to_csv(mock_to_csv, temp_config):
    calc = Calculator(config=temp_config)
    # Ensure history is empty
    calc.history.clear()
    calc.save_history()
    mock_to_csv.assert_called()


@patch('app.calculator.Path.exists', return_value=True)
@patch('app.calculator.pd.read_csv')
def test_load_history_empty_df(mock_read_csv, mock_exists, temp_config):
    # read_csv returns an empty DataFrame -> should not raise
    mock_read_csv.return_value = pd.DataFrame()
    calc = Calculator(config=temp_config)
    calc.load_history()
    assert calc.history == []


@patch('app.calculator.Path.exists', return_value=True)
@patch('app.calculator.pd.read_csv', side_effect=Exception('io'))
def test_load_history_raises_operation_error(mock_read_csv, mock_exists, temp_config):
    calc = Calculator(config=temp_config)
    with pytest.raises(OperationError):
        calc.load_history()


def test_get_history_dataframe_and_show_history(temp_config):
    calc = Calculator(config=temp_config)
    # create a Calculation and append
    c = Calculation(operation='Addition', operand1=Decimal('1'), operand2=Decimal('2'))
    calc.history.append(c)
    df = calc.get_history_dataframe()
    assert 'operation' in df.columns
    assert df.iloc[0]['operation'] == 'Addition'
    sh = calc.show_history()
    assert sh[0].startswith('Addition(')


def test_transient_file_handler_emit_handles_open_error():
    handler = TransientFileHandler(filename='does_not_matter')
    record = logging.LogRecord('test', logging.INFO, '', 0, 'msg', None, None)
    # Patch builtins.open to raise so emit's internal open fails and is handled
    with patch('builtins.open', side_effect=OSError('nope')):
        # Should not raise
        handler.emit(record)
