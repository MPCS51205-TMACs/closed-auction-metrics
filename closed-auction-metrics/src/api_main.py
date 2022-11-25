"""This module acts as the API for microservice. Implements the FastAPI package."""

import datetime
import json
from typing import Optional, Union, Dict
from fastapi import FastAPI, Header, HTTPException, APIRouter
from application.requests_responses import *
import uvicorn
from application.closed_auction_metrics_service import ClosedAuctionMetricsService
from domain.auction_repository import AuctionRepository, InMemoryAuctionRepository
from domain.auction_repository_mongo import MongoDbAuctionRepository
import asyncio
import pika, sys, os
from multiprocessing import Process, Manager
from multiprocessing.managers import BaseManager
from infrastructure import utils
from domain.bid import Bid
from domain.closed_auction import ClosedAuction
from fastapi.responses import HTMLResponse
import pprint


VERSION = 'v1'

class RESTAPI:

    def __init__(self, c_a_m_service: ClosedAuctionMetricsService):
        self.c_a_m_service = c_a_m_service
        self.router = APIRouter()
        # self.router.add_api_route("/hello", self.hello, methods=["GET"])
        self.router.add_api_route("/", self.index, methods=["GET"])
        self.router.add_api_route(f"/api/{VERSION}"+"/closedauctions/{item_id}", self.get_closed_auction, methods=["GET"])
        self.router.add_api_route(f"/api/{VERSION}"+"/closedauctions/", self.get_closed_auctions, methods=["GET"])
        self.router.add_api_route(f"/api/{VERSION}"+"/closedauctions/{item_id}/visualization", self.get_closed_auction_visualization, response_class=HTMLResponse,methods=["GET"])
        
    def index(self) -> dict:
        """Returns a default response when no endpoint is specified.

        Returns
        -------
        index : `dict` [`str`, `str`]
            Default response
        """
        return {"home": "route"}

    def get_closed_auction(self, item_id: str, start: str=None, end: str=None, limit: str=None) -> Dict:
        """
        Returns a response containing all closed auctions between a specific time.

        Parameters
        ----------
        start : `str`
            Start time result filter (e.g. "4/25/2022 15:00:00.000000")
        end : `str`
            End time result filter (e.g. "4/26/2022 15:00:00.000000")
        limit : `str`
            Limits the number of reservation results returned 

        Returns
        -------
        : `dict` [`str`, `dict`]
            A response keyed by item_id where each key is mapped to a 
            dictionary containing information about the closed auction.
        
        Notes
        -----
        the closed auctions will be return in chronological increasing order by end_time.
        Query parameters are optional.

        Sample URLs
        No query parameters: http://127.0.0.1:51224/api/v1/closedauctions/100
        With query parameters: http://127.0.0.1:51224/api/v1/closedauctions/100?start=05/04/2022&end=05/05/2022&limit=2

        Sample response body:
        {
            "200": {
                "item_id": "200",
                "start_price_in_cents": 3400,
                "start_time": "2022-03-17 00:00:00.130002",
                "end_time": "2022-03-18 00:00:00.130002",
                "cancellation_time": "",
                "finalized_time": "2022-03-18 00:01:00.130002",
                "bids": [
                    {
                        "bid_id": "100",
                        "item_id": "200",
                        "bidder_user_id": "asclark",
                        "amount_in_cents": 4000,
                        "time_received": "2022-03-17 00:00:00.130002",
                        "active": true
                    },
                    {
                        "bid_id": "101",
                        "item_id": "200",
                        "bidder_user_id": "asclark",
                        "amount_in_cents": 4000,
                        "time_received": "2022-03-17 00:00:00.130002",
                        "active": true
                    },
                    {
                        "bid_id": "102",
                        "item_id": "200",
                        "bidder_user_id": "asclark",
                        "amount_in_cents": 4000,
                        "time_received": "2022-03-17 00:00:00.130002",
                        "active": true
                    }
                ]
            }
        }
        """

        if start is None: 
            start = utils.TIME_ZONE.localize(datetime.datetime(year=1500,month=1,day=1))
        if end is None: 
            end = utils.TIME_ZONE.localize(datetime.datetime(year=4000,month=1,day=1))

        return self.c_a_m_service.get_auction_data(item_id=item_id,start=start,end=end,limit=limit)

    def get_closed_auctions(self, start: str=None, end: str=None, limit: str=None) -> Dict:
        """
        Returns a response containing all closed auctions between a specific time.

        Parameters
        ----------
        start : `str`
            Start time result filter (e.g. "4/25/2022 15:00:00.000000")
        end : `str`
            End time result filter (e.g. "4/26/2022 15:00:00.000000")
        limit : `str`
            Limits the number of reservation results returned 

        Returns
        -------
        : `dict` [`str`, `dict`]
            A response keyed by item_id where each key is mapped to a 
            dictionary containing information about the closed auction.
        
        Notes
        -----
        the closed auctions will be return in chronological increasing order by end_time.
        Query parameters are optional.

        Sample URLs
        No query parameters: http://127.0.0.1:51224/api/v1/closedauctions/100
        With query parameters: http://127.0.0.1:51224/api/v1/closedauctions/100?start=05/04/2022&end=05/05/2022&limit=2

        Sample response body:
        {
            "200": {
                "item_id": "200",
                "start_price_in_cents": 3400,
                "start_time": "2022-03-17 00:00:00.130002",
                "end_time": "2022-03-18 00:00:00.130002",
                "cancellation_time": "",
                "finalized_time": "2022-03-18 00:01:00.130002",
                "bids": [
                    {
                        "bid_id": "100",
                        "item_id": "200",
                        "bidder_user_id": "asclark",
                        "amount_in_cents": 4000,
                        "time_received": "2022-03-17 00:00:00.130002",
                        "active": true
                    },
                    {
                        "bid_id": "101",
                        "item_id": "200",
                        "bidder_user_id": "asclark",
                        "amount_in_cents": 4000,
                        "time_received": "2022-03-17 00:00:00.130002",
                        "active": true
                    },
                    {
                        "bid_id": "102",
                        "item_id": "200",
                        "bidder_user_id": "asclark",
                        "amount_in_cents": 4000,
                        "time_received": "2022-03-17 00:00:00.130002",
                        "active": true
                    }
                ]
            },
            "201": {
                "item_id": "201",
                "start_price_in_cents": 3400,
                "start_time": "2022-03-17 00:00:00.130002",
                "end_time": "2022-03-18 00:00:00.130002",
                "cancellation_time": "",
                "finalized_time": "2022-03-18 00:01:00.130002",
                "bids": [
                    {
                        "bid_id": "103",
                        "item_id": "201",
                        "bidder_user_id": "asclark",
                        "amount_in_cents": 4000,
                        "time_received": "2022-03-17 00:00:00.130002",
                        "active": true
                    },
                    {
                        "bid_id": "104",
                        "item_id": "201",
                        "bidder_user_id": "asclark",
                        "amount_in_cents": 4000,
                        "time_received": "2022-03-17 00:00:00.130002",
                        "active": true
                    }
                ]
            }
        }
        """


        if start is None: 
            start_datetime = utils.TIME_ZONE.localize(datetime.datetime(year=1500,month=1,day=1))
        else:
            try:
                print(start)
                start_datetime = utils.toDatetimeFromStr(start)
            except ValueError:
                raise HTTPException(status_code=400, detail=f"start (time) has incorrect data format, should be {utils.TIME_PARSE_FORMAT}")
            
        if end is None: 
            end_datetime = utils.TIME_ZONE.localize(datetime.datetime(year=4000,month=1,day=1))
        else:
            try:
                print(end)
                end_datetime = utils.toDatetimeFromStr(end)
            except ValueError:
                raise HTTPException(status_code=400, detail=f"end (time) incorrect data format, should be {utils.TIME_PARSE_FORMAT}")

        return self.c_a_m_service.get_auction_data(item_id=None,start=start_datetime,end=end_datetime,limit=limit)

    def get_closed_auction_visualization(self, item_id:str) -> HTMLResponse:
        """
        Returns an html response showing the bid history for the particular item.

        Parameters
        ----------
        item_id : `str`
            item id

        Returns
        -------
        html response
            interactive graphic
        
        Notes
        -----
        """

        return self.c_a_m_service.get_auction_visualization_html(item_id=item_id)


def start_receiving_rabbitmsgs(c_a_m_service : ClosedAuctionMetricsService):
    try:
        receive_rabbitmq_msgs(c_a_m_service)
    except KeyboardInterrupt:
        print('Interrupted')
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)

def receive_rabbitmq_msgs(c_a_m_service : ClosedAuctionMetricsService):

    RABBITMQ_HOST = "rabbitmq-server" # e.g. "localhost"
    EXCHANGE_NAME = "auction.end"
    QUEUE_NAME = "cam.consume-auctionend"

    connection = pika.BlockingConnection(pika.ConnectionParameters(host=RABBITMQ_HOST))
    channel = connection.channel()

    channel.exchange_declare(exchange=EXCHANGE_NAME, exchange_type='fanout', durable=True)
    result = channel.queue_declare(queue=QUEUE_NAME, durable=True) #durable=True exclusive=False,
    queue_name = result.method.queue

    channel.queue_bind(exchange=EXCHANGE_NAME, queue=queue_name)
    
    print(' [*] Waiting for logs. To exit press CTRL+C')

    def callback(ch, method, properties, body):
        print(" [x] received new auction data.")
        jsondata = json.loads(body)
        print(json.dumps(jsondata, indent=2))
        c_a_m_service.add_auction_data(jsondata)

    # def callback(ch, method, properties, body):
    #     print(" [x] Received %r" % body.decode())
    #     print(" [x] Done")
    #     ch.basic_ack(delivery_tag=method.delivery_tag)


    
    channel.basic_consume(queue=queue_name, on_message_callback=callback, auto_ack=True)
    # channel.basic_qos(prefetch_count=1)
    # channel.basic_consume(queue='task_queue', on_message_callback=callback)
    channel.start_consuming()

def startupRESTAPI(app: FastAPI, port:int, log_level:str = "info"):
    # uvicorn.run("api_main:app", port=51224, log_level=log_level)
    proc = Process(target=uvicorn.run,
                    args=(app,),
                    kwargs={
                        "host": "0.0.0.0", # e.g. "127.0.0.1",
                        "port": port,
                        "log_level": "info"},
                    daemon=True)
    proc.start()

LOCAL_PORT = 51224 # port for this service (And its restful api)

def main():

    app = FastAPI()

    inMemory = False

    if inMemory: # use in memory repos
        auction_repo: AuctionRepository = InMemoryAuctionRepository()

        bid1 = Bid.generate_basic_bid(100,200)
        bid2 = Bid.generate_basic_bid(101,200)
        bid3 = Bid.generate_basic_bid(102,200)
        start = utils.TIME_ZONE.localize(datetime.datetime(year = 2022, month=3, day=17, hour=0, minute=0, second=0,microsecond=130002 ))
        duration = datetime.timedelta(minutes=30)
        auction1 = ClosedAuction.generate_auction([bid1,bid2,bid3],200, start, duration)

        bid4 = Bid.generate_basic_bid(103,201)
        bid5 = Bid.generate_basic_bid(104,201)
        start2 = utils.TIME_ZONE.localize(datetime.datetime(year = 2022, month=3, day=17, hour=1, minute=10, second=0,microsecond=130002 ))
        duration2 = datetime.timedelta(minutes=24)
        auction2 = ClosedAuction.generate_auction([bid4,bid5],201, start2, duration2)

        bid6 = Bid.generate_basic_bid(105,202)
        start3 = utils.TIME_ZONE.localize(datetime.datetime(year = 2022, month=3, day=17, hour=1, minute=17, second=10,microsecond=130002 ))
        duration3 = datetime.timedelta(minutes=14)
        auction3 = ClosedAuction.generate_auction([bid6],202, start3,duration)

        auction_repo.save_auction(auction1)
        auction_repo.save_auction(auction2)
        auction_repo.save_auction(auction3)
    
        # app.closed_auction_metrics_service = closed_auction_metrics_service.ClosedAuctionMetricsService(auction_repo)
        # c_a_m_service = ClosedAuctionMetricsService(auction_repo)
        BaseManager.register('ClosedAuctionMetricsService', ClosedAuctionMetricsService)
        manager = BaseManager()
        manager.start()
        c_a_m_service = manager.ClosedAuctionMetricsService(auction_repo)
    
        api = RESTAPI(c_a_m_service)
        app.include_router(api.router)
        
        # spawn child process to handle the HTTP requests against the REST api
        startupRESTAPI(app,LOCAL_PORT)

        # main function enters method that blocks and never returns
        start_receiving_rabbitmsgs(c_a_m_service)
    else: # use sql repos
        # auction_repo: AuctionRepository = InMemoryAuctionRepository()
        CAM_MONGO_CONTAINER_HOSTNAME = "cam-mongo-server"
        auction_repo1: AuctionRepository = MongoDbAuctionRepository(CAM_MONGO_CONTAINER_HOSTNAME)
        auction_repo2: AuctionRepository = MongoDbAuctionRepository(CAM_MONGO_CONTAINER_HOSTNAME)

        # bid1 = Bid.generate_basic_bid(100,200)
        # bid2 = Bid.generate_basic_bid(101,200)
        # bid3 = Bid.generate_basic_bid(102,200)
        # start = utils.TIME_ZONE.localize(datetime.datetime(year = 2022, month=3, day=17, hour=0, minute=0, second=0,microsecond=130002 ))
        # duration = datetime.timedelta(minutes=30)
        # auction1 = ClosedAuction.generate_auction([bid1,bid2,bid3],200, start, duration)

        # bid4 = Bid.generate_basic_bid(103,201)
        # bid5 = Bid.generate_basic_bid(104,201)
        # start2 = utils.TIME_ZONE.localize(datetime.datetime(year = 2022, month=3, day=17, hour=1, minute=10, second=0,microsecond=130002 ))
        # duration2 = datetime.timedelta(minutes=24)
        # auction2 = ClosedAuction.generate_auction([bid4,bid5],201, start2, duration2)

        # bid6 = Bid.generate_basic_bid(105,202)
        # start3 = utils.TIME_ZONE.localize(datetime.datetime(year = 2022, month=3, day=17, hour=1, minute=17, second=10,microsecond=130002 ))
        # duration3 = datetime.timedelta(minutes=14)
        # auction3 = ClosedAuction.generate_auction([bid6],202, start3,duration)

        # auction_repo2.save_auction(auction1)
        # auction_repo2.save_auction(auction2)
        # auction_repo2.save_auction(auction3)

        c_a_m_service1 = ClosedAuctionMetricsService(auction_repo1)
        c_a_m_service2 = ClosedAuctionMetricsService(auction_repo2)

        api = RESTAPI(c_a_m_service1)
        app.include_router(api.router)
        
        # spawn child process to handle the HTTP requests against the REST api
        startupRESTAPI(app,LOCAL_PORT)

        # main function enters method that blocks and never returns
        start_receiving_rabbitmsgs(c_a_m_service2)

if __name__ == "__main__":
    main()