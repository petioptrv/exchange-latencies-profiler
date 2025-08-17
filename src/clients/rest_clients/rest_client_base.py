from abc import ABC, abstractmethod


class RESTClientBase(ABC):
    @abstractmethod
    def get_server_time_ms(self) -> float:
        ...
