
from domain.closed_auction import *
from domain.auction_repository import *
from typing import Dict

from pymongo import MongoClient
from pymongo.database import Database, Collection
# pprint library is used to make the output look more pretty
from pprint import pprint


# name the database for the project
DATABASE_NAME = "closed_auction_metrics_db"
AUCTION_COLLECTION_NAME = "auctions"

class PostgresSQLAuctionRepository(AuctionRepository):

    # MONGO_DB_CONNECTION_PATH = "mongodb://localhost:27017/"

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
        # client.drop_database(DATABASE_NAME)

        # create database if it doesn't already exist (this done automatically?)
        if DATABASE_NAME not in client.list_database_names():
            print(f"database '{DATABASE_NAME}' does not exist")
        else:
            print(f"database '{DATABASE_NAME}' appears to already exist")
        self.my_db = client[DATABASE_NAME]

        # create collection to store auction data
        if AUCTION_COLLECTION_NAME not in self.my_db.list_collection_names():
            print(f"collection '{AUCTION_COLLECTION_NAME}' does not exist")
            auction_collection = self.my_db.create_collection(AUCTION_COLLECTION_NAME)
        else:
            print(f"collection '{AUCTION_COLLECTION_NAME}' appears to already exist")
            auction_collection = self.my_db[AUCTION_COLLECTION_NAME]

        
    def _get_auction_collection(self) -> Collection:
        return self.my_db[AUCTION_COLLECTION_NAME]
        
        # self._auctions: Dict[str,str] = dict() 

    def check_server_status(self):
        serverStatusResult = self.my_db.command("serverStatus")
        pprint(serverStatusResult)

    def get_auction(self, item_id: str) -> Optional[ClosedAuction]:
        if item_id in self._auctions:
            return self._auctions[item_id]
        return None

    def get_auctions(self, leftBound: datetime.datetime, rightBound: datetime.datetime) -> List[ClosedAuction]:
        pass


    def save_auction(self, auction: ClosedAuction):
        self._auctions[auction._item_id] = auction # works for both add new and update

