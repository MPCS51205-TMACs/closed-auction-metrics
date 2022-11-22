from abc import ABC, abstractmethod
from domain.closed_auction import *
from typing import Dict

class AuctionRepository(ABC):

    @abstractmethod
    def get_auction(self, item_id: str) -> ClosedAuction:
        pass

    @abstractmethod
    def get_auctions(self, leftBound: datetime.datetime, rightBound: datetime.datetime) -> List[ClosedAuction]:
        pass

    @abstractmethod
    def save_auction(self, auction: ClosedAuction):
        pass


class inMemoryAuctionRepository(AuctionRepository):

    def __init__(self) -> None:
        super().__init__()
        self._auctions: Dict[str,ClosedAuction] = dict() 

    def get_auction(self, item_id: str) -> Optional[ClosedAuction]:
        if item_id in self._auctions:
            return self._auctions[item_id]
        return None

    def get_auctions(self, leftBound: Optional[datetime.datetime], rightBound: Optional[datetime.datetime], limit: Optional[int]=None) -> List[ClosedAuction]:
        # filter out the Transactions by the left and right date range specified
        auction_list = self._auctions.values()


        if not leftBound and not rightBound:
            auction_list_trimmed = auction_list
        else:
            auction_list_trimmed = []
            for auction in auction_list:
                finalization_datetime = auction.get_end_time()
                # trim by a left and right bound
                if leftBound and rightBound:
                    if leftBound <= finalization_datetime <= rightBound:
                        auction_list_trimmed.append(auction)
                # trim by a left bound
                elif leftBound:
                    if leftBound <= finalization_datetime:
                        auction_list_trimmed.append(auction)
                # trim by a right bound
                elif rightBound:
                    if finalization_datetime <= rightBound:
                        auction_list_trimmed.append(auction)
            return auction_list_trimmed

        _sort_auction_results(auction_list_trimmed)

        if limit:
            return _limit_auction_results(auction_list_trimmed,limit,toSort=False)
        else:
            return auction_list_trimmed

    def save_auction(self, auction: ClosedAuction):
        self._auctions[auction._item_id] = auction # works for both add new and update

def _sort_auction_results(closed_auctions: List[ClosedAuction]):
    """sorts the closed auctions sorted from ending the farthest back in time to most recent (last idx)."""
    # sort closed auctions in ascending order by time of finalization
    closed_auctions.sort(key=lambda ca: ca.get_end_time())
    
def _limit_auction_results(closed_auctions: List[ClosedAuction], limit: int, toSort: bool=False) -> List[ClosedAuction]:
    """Returns the most recently closed auctions up till limit into the past."""
    if len(closed_auctions) > limit:
        if toSort:
            _sort_auction_results(closed_auctions)
        closed_auctions = closed_auctions[len(closed_auctions)-limit:] # keep most recently ended closed-auctions until limit
    return closed_auctions

class postgresSQLAuctionRepository(AuctionRepository):

    def __init__(self) -> None:
        super().__init__()
        self._auctions: Dict[str,str] = dict() 

    def get_auction(self, item_id: str) -> Optional[ClosedAuction]:
        if item_id in self._auctions:
            return self._auctions[item_id]
        return None

    def save_auction(self, auction: ClosedAuction):
        self._auctions[auction._item_id] = auction # works for both add new and update