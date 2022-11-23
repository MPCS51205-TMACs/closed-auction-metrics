
from domain.closed_auction import *
from domain.auction_repository import *
from typing import Dict

from pymongo import MongoClient
from pymongo.database import Database, Collection
from pprint import pprint # to print bson like data prettier


# name the database for the project
DATABASE_NAME = "closed_auction_metrics_db"
AUCTION_COLLECTION_NAME = "auctions"

class PostgresSQLAuctionRepository(AuctionRepository):

    # (typical) MONGO_DB_CONNECTION_PATH = "mongodb://localhost:27017/"

    # def _connect(self) -> None:
    #     self._client = MongoClient(self._mongo_db_connection_url)

    # def _drop_create_db(self) -> Database:
    #     # drop database (if already exists)?? optional
    #     self._client.drop_database(DATABASE_NAME)

    #     # create database with name specified above
    #     self._my_db = self._client[DATABASE_NAME]

    def __init__(self, hostname: str, port: str= "27017") -> None:

        mongo_db_connection_url = f"mongodb://{hostname}:{port}/"
        
        # establish connection to where mongo database lives (will live)
        print("establishing connection to MongoDB server...")
        client = MongoClient(mongo_db_connection_url)

        # # drop database (if already exists)?? optional
        print("dropping database '{DATABASE_NAME}'")
        client.drop_database(DATABASE_NAME)

        # create database if it doesn't already exist (this done automatically?)
        if DATABASE_NAME not in client.list_database_names():
            print(f"database '{DATABASE_NAME}' does not exist")
        else:
            print(f"database '{DATABASE_NAME}' appears to already exist")
        self.my_db = client[DATABASE_NAME]

        # create collection to store auction data
        if AUCTION_COLLECTION_NAME not in self.my_db.list_collection_names():
            print(f"collection '{AUCTION_COLLECTION_NAME}' does not exist; creating...")
            auction_collection = self.my_db.create_collection(AUCTION_COLLECTION_NAME)
        else:
            print(f"collection '{AUCTION_COLLECTION_NAME}' appears to already exist")
            auction_collection = self.my_db[AUCTION_COLLECTION_NAME]

        
    def _get_auction_collection(self) -> Collection:
        return self.my_db[AUCTION_COLLECTION_NAME]

    def check_server_status(self):
        serverStatusResult = self.my_db.command("serverStatus")
        pprint(serverStatusResult)

    def get_auction(self, item_id: str) -> Optional[ClosedAuction]:
        query_doc = {
            "item_id": item_id
        }
        auction_collection = self._get_auction_collection()
        data = auction_collection.find_one(query_doc)
        return self._mongoDataToClosedAuction(data) if data else None

    def get_auctions(self, leftBound: Optional[datetime.datetime], rightBound: Optional[datetime.datetime], limit: Optional[int]=None) -> List[ClosedAuction]:
        auction_collection = self._get_auction_collection()

        if leftBound or rightBound:
            if leftBound and rightBound:
                time_param = {'$lte': rightBound, '$gte': leftBound}
            elif leftBound:
                time_param = {'$gte': leftBound}
            else: # rightBound
                time_param = {'$lte': rightBound}
            query_doc = { "end_time": time_param }
        else:
            query_doc = {} # getting all auctions (up to default limit)...

        # retreive auctions
        cursor = auction_collection.find(query_doc)
        auctions : List[ClosedAuction] = []
        for data in cursor:
            closed_auction = self._mongoDataToClosedAuction(data)
            auctions.append(closed_auction)

        # order auctions by end time
        _sort_auction_results(auctions)

        # filter down number of results
        if not limit:
            limit = 10 # default max number of auctions returned
        auction_list_trimmed = _limit_auction_results(auctions,limit,toSort=False)

        return auction_list_trimmed

    def save_auction(self, auction: ClosedAuction):
        auction_collection = self._get_auction_collection()
        document = auction.convert_to_dict_w_datetimes()
        auction_collection.update_one({ '_id' : auction._item_id}, { '$set': document }, upsert=True)

    def _mongoDataToClosedAuction(self, data: Dict) -> ClosedAuction:
        bids: List[Bid] = []
        for bid in data["bids"]:
            bids.append(Bid(bid["bid_id"],bid["item_id"],bid["bidder_user_id"],bid["amount_in_cents"],bid["time_received"],bid["active"]))

        item_id : str = data["item_id"]
        start_price_in_cents : int = data["start_price_in_cents"]
        start_time : datetime.datetime = data["start_time"]
        end_time  : datetime.datetime = data["end_time"]
        cancellation_time  : Optional[datetime.datetime] = data["cancellation_time"] if data["cancellation_time"]!="" else None
        finalized_time  : datetime.datetime = data["finalized_time"]

        new_closed_auction = ClosedAuction(item_id,start_price_in_cents,start_time,end_time,cancellation_time,finalized_time,bids)
        return new_closed_auction



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
