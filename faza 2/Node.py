from abc import ABC, abstractmethod

class Node(ABC):

    # тот от кого получать
    @abstractmethod
    def followeesSet(self, followees):
        pass

    #список всех неподтвержденных транзакций
    @abstractmethod
    def pendingTransactionSet(self, pendingTransactions):
        pass

    #отправлять фоловеру
    @abstractmethod
    def followersSend(self):
        pass

    # получать от узла за которым наблюдаем
    @abstractmethod
    def followeesReceive(self, candidates):
        pass
