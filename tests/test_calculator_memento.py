from decimal import Decimal
import datetime

from app.calculation import Calculation
from app.calculator_memento import CalculatorMemento


def test_memento_to_dict_and_from_dict():
    # Create a Calculation instance
    calc = Calculation(operation='Addition', operand1=Decimal('2'), operand2=Decimal('3'))

    # Create memento and serialize
    m = CalculatorMemento(history=[calc])
    d = m.to_dict()

    # Basic structure checks
    assert 'history' in d
    assert 'timestamp' in d
    assert isinstance(d['history'], list)
    assert d['history'][0]['operation'] == 'Addition'

    # Deserialize back
    m2 = CalculatorMemento.from_dict(d)
    assert isinstance(m2, CalculatorMemento)
    assert len(m2.history) == 1

    # Check that the deserialized calculation matches the original
    loaded = m2.history[0]
    assert loaded.operation == calc.operation
    assert loaded.operand1 == calc.operand1
    assert loaded.operand2 == calc.operand2

    # Timestamp round-trip
    assert isinstance(m2.timestamp, datetime.datetime)
    assert m2.timestamp.isoformat() == d['timestamp']
