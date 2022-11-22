from typing import Dict, Optional
from domain.auction_repository import AuctionRepository
import datetime
from fastapi.responses import HTMLResponse

class ClosedAuctionMetricsService():

    def __init__(self,auction_repository : AuctionRepository) -> None:
        self._auction_repo = auction_repository

    def add_auction_data(self):
        print("[ClosedAuctionMetricsService] STUBBED adding new auction data...")

    def get_auction_data(self, item_id: Optional[str], start: Optional[datetime.datetime]=None, end: Optional[datetime.datetime]=None, limit: int=None) -> Dict:
        print("[ClosedAuctionMetricsService] getting auction data...")

        if item_id:
            auction = self._auction_repo.get_auction(item_id)
            if auction:
                return {auction._item_id : auction.convert_to_dict()}
            else :
                return dict()
        else:
            auctions = self._auction_repo.get_auctions(leftBound = start, rightBound = end) # returns auctions that were over between these times
            return {auction._item_id : auction.convert_to_dict() for auction in auctions}

    def get_auction_visualization_html(self,item_id: str) -> HTMLResponse:
        auction = self._auction_repo.get_auction(item_id)
        if auction:
            html, withErrors = auction.generate_bid_history_as_html()
            if withErrors:
                return HTMLResponse(content= html, status_code=400)
            else:
                return HTMLResponse(content= html, status_code=200)
        else:
            return HTMLResponse(content= f"could not find closed auction for item_id={item_id}", status_code=200)
