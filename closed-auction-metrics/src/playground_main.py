from typing import Optional, Union, Dict

from application.closed_auction_metrics_service import ClosedAuctionMetricsService
from domain.auction_repository import AuctionRepository, InMemoryAuctionRepository
from domain.auction_repository_mongo import PostgresSQLAuctionRepository
from infrastructure import utils
from domain.bid import Bid
from domain.closed_auction import ClosedAuction

import datetime

def main():
    auctionRepo = PostgresSQLAuctionRepository("mongo-server")

    bid1 = Bid.generate_basic_bid(100,200)
    bid2 = Bid.generate_basic_bid(101,200)
    bid3 = Bid.generate_basic_bid(102,200)
    time_start1 = utils.TIME_ZONE.localize(datetime.datetime(year = 2022, month=3, day=17, hour=0, minute=0, second=0,microsecond=130002 ))
    duration1 = datetime.timedelta(days=1)
    auction1 = ClosedAuction.generate_auction([bid1,bid2,bid3],200,time_start1,duration1)

    duration2 = datetime.timedelta(days=2)
    auction2 = ClosedAuction.generate_auction([bid1,bid2,bid3],201,time_start1,duration2)

    duration3 = datetime.timedelta(days=3)
    auction3 = ClosedAuction.generate_auction([bid1,bid2,bid3],202,time_start1,duration3)
    print("created 3 auctions; saving...")

    auctionRepo.save_auction(auction1)
    auctionRepo.save_auction(auction2)
    auctionRepo.save_auction(auction3)

    # print()
    # print("now trying to retreive...")
    # auctionRepo.get_auction(auction1._item_id)
    # print()
    # print("changing data and saving changes...")
    # auction1._start_price_in_cents = 300000
    # auctionRepo.save_auction(auction1)
    # print()
    # print("now trying to retreive...")
    # auctionRepo.get_auction(auction1._item_id)
    # print()

    print("fetching all")
    left = time_start1 - datetime.timedelta(hours=2)
    right = time_start1 + datetime.timedelta(days=4)
    auctions = auctionRepo.get_auctions(left,right)

    for auction in auctions:
        print(auction)
    # auctionRepo.check_server_status()
    # Issue the serverStatus command and print the results
    
if __name__ == "__main__":
    main()
    
    # auction_repo: AuctionRepository = InMemoryAuctionRepository()

    # bid1 = Bid.generate_basic_bid(100,200)
    # bid2 = Bid.generate_basic_bid(101,200)
    # bid3 = Bid.generate_basic_bid(102,200)
    # auction1 = ClosedAuction.generate_auction([bid1,bid2,bid3],200)

    # bid4 = Bid.generate_basic_bid(103,201)
    # bid5 = Bid.generate_basic_bid(104,201)
    # auction2 = ClosedAuction.generate_auction([bid4,bid5],201)

    # bid6 = Bid.generate_basic_bid(105,202)
    # auction3 = ClosedAuction.generate_auction([bid6],202)

    # auction_repo.save_auction(auction1)
    # auction_repo.save_auction(auction2)
    # auction_repo.save_auction(auction3)
    
    # # app.closed_auction_metrics_service = closed_auction_metrics_service.ClosedAuctionMetricsService(auction_repo)
    # c_a_m_service = ClosedAuctionMetricsService(auction_repo)


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
    #     'Cancellation': None,
    #     'SentStartSoonAlert': True,
    #     'SentEndSoonAlert': True,
    #     'Finalization': {
    #         'time_received': '2022-11-23 02:00:28.061013'
    #     }
    # }
    
    # c_a_m_service.add_auction_data(ex_data2)