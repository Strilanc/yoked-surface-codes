import abc

import sinter


class CollectionWorkHandler(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def do_some_work(self, task: sinter.Task, max_shots: int) -> sinter.AnonTaskStats:
        pass
