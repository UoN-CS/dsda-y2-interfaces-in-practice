from random import randrange
from consumption_data import ConsumptionData

class ConsumptionDataStub(ConsumptionData):
    """Simple stubbed out implementation of the ConsumptionData interface so I can start writing the client"""

    def get_usage_for_range(self, start: int, end: int) -> int:
        """Stub that returns a random number for the consumption Wh betweeen 10000 and 30000 Wh
        """        
        return 10000 + randrange(20000)

    def has_usage_for_range(self, start: int, end: int) -> bool:
        return true