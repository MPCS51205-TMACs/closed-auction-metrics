"""test module for closed_auction_metrics_service.py"""

import pytest
from datetime import datetime

class TestClosedAuctionMetrics:

    def setup_class(cls):
        """this code runs before this whole test module runs"""

        
        resv_id = "1"
        client_id = "0012"
        date_booked = TIME_ZONE.localize(datetime(year = 2022, month=3, day=17, hour=0, minute=0)) 
        duration_blocks = 1
        date_reserved = TIME_ZONE.localize(datetime(year = 2022, month=4, day=2, hour=10, minute=0))
        resource = Workshop("10","1") # work_1
        canceled = False
        cls.c_reservation1 = ConcreteReservation(resv_id,"0012",date_booked,date_reserved,resource,duration_blocks,canceled)

        # transactional reservation for LightningHarvester
        resv_id = "11"
        client_id = "0013"
        date_booked = TIME_ZONE.localize(datetime(year = 2022, month=3, day=29, hour=0, minute=0)) 
        duration_blocks = 1
        date_reserved = TIME_ZONE.localize(datetime(year = 2022, month=4, day=5, hour=10, minute=30))
        resource = LightningHarvester("9","1") # work_1
        canceled = False
        cls.c_reservation2 = ConcreteReservation(resv_id,"0012",date_booked,date_reserved,resource,duration_blocks,canceled)


    def test_get_transactions(database_reset_before_and_after):
        '''get all transactions'''
        # ###### no filter
        response = client.get(
            url="/v4/transactions",
        )
        assert response.status_code == 200
        response_json = response.json()
        assert len(response_json) == 50
        for transaction_id, transaction_dict in response_json.items():
            assert transaction_id.isdigit() # key is a digit
            # check expected keys are found 
            assert all(key in VIEW_TRANSACTIONS_JSON_KEYS for key in transaction_dict.keys()) 
            assert len(VIEW_TRANSACTIONS_JSON_KEYS) == len(transaction_dict.keys())
            # check keys of response_json are mapped to the correct dictionary
            assert transaction_dict['transaction_id'] == transaction_id