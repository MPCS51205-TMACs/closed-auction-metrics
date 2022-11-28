from typing import Dict, List, Optional
from domain.auction_repository import AuctionRepository, InMemoryAuctionRepository
from infrastructure import utils
from domain.bid import Bid
from domain.closed_auction import ClosedAuction
import datetime
from fastapi.responses import HTMLResponse

class ClosedAuctionMetricsService():

    def __init__(self,auction_repository : AuctionRepository) -> None:
        self._auction_repo = auction_repository

    def add_auction_data(self, data : Dict):
        print("[ClosedAuctionMetricsService] adding new auction data...")
        # example data dicts received
        # ex_data = {
        #     'Item': {
        #             'item_id': '20',
        #             'seller_user_id': 'asclark109',
        #             'start_time': '2022-11-23 01:41:13.629971',
        #             'end_time': '2022-11-23 01:42:13.629971',
        #             'start_price_in_cents': 2000
        #     },
        #     'Bids': [],
        #     'Cancellation': {
        #         'time_received': '2022-11-23 01:41:18.633116'
        #     },
        #     'SentStartSoonAlert': True,
        #     'SentEndSoonAlert': True,
        #     'Finalization': {
        #         'time_received': '2022-11-23 01:41:23.630086'
        #     }
        # }

        # ex_data2 = {
        #     'Item': {
        #         'item_id': '20',
        #         'seller_user_id': 'asclark109',
        #         'start_time': '2022-11-23 02:00:18.060466',
        #         'end_time': '2022-11-23 02:10:18.060466',
        #         'start_price_in_cents': 2000
        #     },
        #     'Bids': [
        #         {'bid_id': '101', 'item_id': '20', 'bidder_user_id': 'asclark109', 'time_received': '2014-02-04 00:00:00.000000', 'amount_in_cents': 300, 'active': True},
        #         {'bid_id': '102', 'item_id': '20', 'bidder_user_id': 'mcostigan9', 'time_received': '2014-02-04 00:00:00.000000', 'amount_in_cents': 300, 'active': True},
        #         {'bid_id': '103', 'item_id': '20', 'bidder_user_id': 'katharine2', 'time_received': '2014-02-04 00:00:00.000001', 'amount_in_cents': 400, 'active': True},
        #         {'bid_id': '104', 'item_id': '20', 'bidder_user_id': 'katharine2', 'time_received': '2014-02-04 00:00:01.000000', 'amount_in_cents': 10, 'active': True}
        #     ],
        #     'Cancellation': {
        #         'time_received': '2022-11-23 02:00:23.062227'
        #     },
        #     'SentStartSoonAlert': True,
        #     'SentEndSoonAlert': True,
        #     'Finalization': {
        #         'time_received': '2022-11-23 02:00:28.061013'
        #     }
        # }
        
        refined_data = self._cast_str_times_to_datetimes(data) # creates a new dict
        # print()
        # print(refined_data)
        
        closed_auction = self._create_closed_auction_from_data(refined_data) 
        # print()
        print("[ClosedAuctionMetricsService] created ClosedAuction object from refined data")
        print(closed_auction)

        print("[ClosedAuctionMetricsService] saving ClosedAuction object...")
        self._auction_repo.save_auction(closed_auction)

        # {
        #     'Item': {
        #             'item_id': '20',
        #             'seller_user_id': 'asclark109',
        #             'start_time': '2022-11-23 01:41:13.629971',
        #             'end_time': '2022-11-23 01:42:13.629971',
        #             'start_price_in_cents': 2000
        #     },
        #     'Bids': [],
        #     'Cancellation': {
        #         'time_received': '2022-11-23 01:41:18.633116'
        #     },
        #     'SentStartSoonAlert': True,
        #     'SentEndSoonAlert': True,
        #     'Finalization': {
        #         'time_received': '2022-11-23 01:41:23.630086'
        #     }
        # }
        # {'Item': {'item_id': '20', 'seller_user_id': 'asclark109', 'start_time': '2022-11-23 01:41:13.629971', 'end_time': '2022-11-23 01:42:13.629971', 'start_price_in_cents': 2000}, 'Bids': [], 'Cancellation': {'time_received': '2022-11-23 01:41:18.633116'}, 'SentStartSoonAlert': True, 'SentEndSoonAlert': True, 'Finalization': {'time_received': '2022-11-23 01:41:23.630086'}}
        # {'Item': {'item_id': '20', 'seller_user_id': 'asclark109', 'start_time': '2022-11-23 01:38:13.664840', 'end_time': '2022-11-23 01:39:13.664840', 'start_price_in_cents': 2000}, 'Bids': [], 'Cancellation': {'time_received': '2022-11-23 01:38:18.669475'}, 'SentStartSoonAlert': False, 'SentEndSoonAlert': False, 'Finalization': None}

    def get_auction_data(self, item_id: Optional[str], start: Optional[datetime.datetime]=None, end: Optional[datetime.datetime]=None, limit: int=None) -> Dict:
        print("[ClosedAuctionMetricsService] getting auction data...")

        if item_id:
            auction = self._auction_repo.get_auction(item_id)
            if auction:
                return {auction._item_id : auction.convert_to_dict()}
            else :
                return dict()
        else:
            auctions = self._auction_repo.get_auctions(leftBound = start, rightBound = end, limit = limit) # returns auctions that were over between these times
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

    def _cast_str_times_to_datetimes(self, rawdata: Dict) -> Dict:
        # ex_data = {
        #     'Item': {
        #             'item_id': '20',
        #             'seller_user_id': 'asclark109',
        #             'start_time': '2022-11-23 01:41:13.629971',
        #             'end_time': '2022-11-23 01:42:13.629971',
        #             'start_price_in_cents': 2000
        #     },
        #     'Bids': [],
        #     'Cancellation': {
        #         'time_received': '2022-11-23 01:41:18.633116'
        #     },
        #     'SentStartSoonAlert': True,
        #     'SentEndSoonAlert': True,
        #     'Finalization': {
        #         'time_received': '2022-11-23 01:41:23.630086'
        #     }
        # }

        # ex_data2 = {
        #     'Item': {
        #         'item_id': '20',
        #         'seller_user_id': 'asclark109',
        #         'start_time': '2022-11-23 02:00:18.060466',
        #         'end_time': '2022-11-23 02:10:18.060466',
        #         'start_price_in_cents': 2000
        #     },
        #     'Bids': [
        #         {'bid_id': '101', 'item_id': '20', 'bidder_user_id': 'asclark109', 'time_received': '2014-02-04 00:00:00.000000', 'amount_in_cents': 300, 'active': True},
        #         {'bid_id': '102', 'item_id': '20', 'bidder_user_id': 'mcostigan9', 'time_received': '2014-02-04 00:00:00.000000', 'amount_in_cents': 300, 'active': True},
        #         {'bid_id': '103', 'item_id': '20', 'bidder_user_id': 'katharine2', 'time_received': '2014-02-04 00:00:00.000001', 'amount_in_cents': 400, 'active': True},
        #         {'bid_id': '104', 'item_id': '20', 'bidder_user_id': 'katharine2', 'time_received': '2014-02-04 00:00:01.000000', 'amount_in_cents': 10, 'active': True}
        #     ],
        #     'Cancellation': {
        #         'time_received': '2022-11-23 02:00:23.062227'
        #     },
        #     'SentStartSoonAlert': True,
        #     'SentEndSoonAlert': True,
        #     'Finalization': {
        #         'time_received': '2022-11-23 02:00:28.061013'
        #     }
        #         "WinningBid": {
        #               "bid_id": "104",
        #               "item_id": "20",
        #               "bidder_user_id": "katharine2",
        #               "time_received": "2014-02-04 00:00:01.000000",
        #               "amount_in_cents": 10,
        #               "active": true
        #     }
        # }

        # note this data comes from the auctions context
        data = rawdata.copy()
        data["Item"]["dt_start_time"] = utils.toDatetimeFromStr(data["Item"]["start_time"])
        data["Item"]["dt_end_time"] = utils.toDatetimeFromStr(data["Item"]["end_time"])

        for bid in data["Bids"]:
            bid["dt_time_received"] = utils.toDatetimeFromStr(bid["time_received"])

        if data["Cancellation"]:
            data["Cancellation"]["dt_time_received"] = utils.toDatetimeFromStr(data["Cancellation"]["time_received"])

        if data["Finalization"]:
            data["Finalization"]["dt_time_received"] = utils.toDatetimeFromStr(data["Finalization"]["time_received"])

        if data["WinningBid"]:
            data["WinningBid"]["dt_time_received"] = utils.toDatetimeFromStr(data["WinningBid"]["time_received"])

        return data

    def _create_closed_auction_from_data(self,refined_data: Dict) -> ClosedAuction:
        # ALL STRING TIME REPRS ARE NOW DATETIMES

        # ex_data2 = {
        #     'Item': {
        #         'item_id': '20',
        #         'seller_user_id': 'asclark109',
        #         'start_time': '2022-11-23 02:00:18.060466',
        #         'end_time': '2022-11-23 02:10:18.060466',
        #         'start_price_in_cents': 2000
        #     },
        #     'Bids': [
        #         {'bid_id': '101', 'item_id': '20', 'bidder_user_id': 'asclark109', 'time_received': '2014-02-04 00:00:00.000000', 'amount_in_cents': 300, 'active': True},
        #         {'bid_id': '102', 'item_id': '20', 'bidder_user_id': 'mcostigan9', 'time_received': '2014-02-04 00:00:00.000000', 'amount_in_cents': 300, 'active': True},
        #         {'bid_id': '103', 'item_id': '20', 'bidder_user_id': 'katharine2', 'time_received': '2014-02-04 00:00:00.000001', 'amount_in_cents': 400, 'active': True},
        #         {'bid_id': '104', 'item_id': '20', 'bidder_user_id': 'katharine2', 'time_received': '2014-02-04 00:00:01.000000', 'amount_in_cents': 10, 'active': True}
        #     ],
        #     'Cancellation': {
        #         'time_received': '2022-11-23 02:00:23.062227'
        #     },
        #     'SentStartSoonAlert': True,
        #     'SentEndSoonAlert': True,
        #     'Finalization': {
        #         'time_received': '2022-11-23 02:00:28.061013'
        #     }
        #         "WinningBid": {
        #               "bid_id": "104",
        #               "item_id": "20",
        #               "bidder_user_id": "katharine2",
        #               "time_received": "2014-02-04 00:00:01.000000",
        #               "amount_in_cents": 10,
        #               "active": true
        #     }
        # }
        
        
        bids: List[Bid] = []

        for bid in refined_data["Bids"]:
            bids.append(Bid(bid["bid_id"],bid["item_id"],bid["bidder_user_id"],bid["amount_in_cents"],bid["dt_time_received"],bid["active"]))

        item_id : str = refined_data["Item"]["item_id"]
        start_price_in_cents : int = refined_data["Item"]["start_price_in_cents"]
        start_time : datetime.datetime = refined_data["Item"]["dt_start_time"]
        end_time  : datetime.datetime = refined_data["Item"]["dt_end_time"]
        cancellation_time  : Optional[datetime.datetime] = refined_data["Cancellation"]["dt_time_received"] if refined_data["Cancellation"] else None
        finalized_time  : datetime.datetime = refined_data["Finalization"]["dt_time_received"]

        winning_bid = None
        if refined_data["WinningBid"]:
            bid_data = refined_data["WinningBid"]
            winning_bid = Bid(bid_data["bid_id"],bid_data["item_id"],bid_data["bidder_user_id"],bid_data["amount_in_cents"],bid_data["dt_time_received"],bid_data["active"])

        new_closed_auction = ClosedAuction(item_id,start_price_in_cents,start_time,end_time,cancellation_time,finalized_time,bids,winning_bid)
        return new_closed_auction
