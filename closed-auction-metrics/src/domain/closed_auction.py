from __future__ import annotations
import base64
import datetime
from io import BytesIO
from typing import List, Optional, Dict, Tuple

from matplotlib.figure import Figure
from domain.bid import *
from infrastructure import utils

import numpy as np
import matplotlib.pyplot as plt

class ClosedAuction(object):

    def __init__(
        self,
        item_id : str,
        start_price_in_cents : int,
        start_time : datetime.datetime,
        end_time : datetime.datetime,
        cancellation_time: Optional[datetime.datetime],
        finalized_time : datetime.datetime,
        bids: List[Bid],
        winning_bid: Optional[Bid],
        ) -> None:

        self._item_id = item_id
        self._start_price_in_cents = start_price_in_cents
        self._start_time = start_time
        self._end_time = end_time
        self._cancellation_time = cancellation_time
        self._finalized_time = finalized_time
        self._bids = bids
        self._winning_bid = winning_bid

    @staticmethod
    def create_from_data(data_dict : Dict) -> ClosedAuction:
        pass

    def winning_bid(self) -> Optional[Bid]:
        if self._winning_bid is not None:
            return self._winning_bid
        else:
            return self.infer_winning_bid()

    def infer_winning_bid(self) -> Optional[Bid]:
        if len(self._bids) == 0 or self._cancellation_time is not None:
            return None
        
        self._bids.sort(key=lambda x: x._time_received)

        idx = len(self._bids) - 1 # last idx
        while not self._bids[idx]._active:
            idx-=1
            if idx < 0:
                return None

        return self._bids[idx]

    def __repr__(self) -> str:
        winning_bid = self.winning_bid()
        win_price = winning_bid._amount_in_cents/100 if winning_bid is not None else 0
        winning_bid_user_id : str = winning_bid._bidder_user_id if winning_bid is not None else "N/A"
        args = f"itemID={self._item_id}, "
        args += "start_price=${:.2f}, ".format(self._start_price_in_cents/100)
        args += "win_price=${:.2f}, ".format(win_price) if winning_bid is not None else "win_price=N/A, "
        args += f"winner_user_id={winning_bid_user_id}, "
        args += f"time_start={self._start_time}, "
        args += f"time_cancel={self._cancellation_time}, "
        args += f"time_end={self._end_time}, "
        args += f"time_finalized={self._finalized_time}, "
        args += f"num_bids={len(self._bids)}, "
        return "ClosedAuction(" + args + ")" 

    def get_finalized_time(self) -> datetime.datetime :
        return self._finalized_time

    def get_end_time(self) -> datetime.datetime :
        return self._end_time

    def show_bid_history(self, toSave: bool=True) -> Figure:

        times = [bid._time_received for bid in self._bids]
        for time in times:
            print(time)
        amounts = [bid._amount_in_cents/100 for bid in self._bids]

        fig, ax = plt.subplots()
        ax.step(times, amounts, where='post', label='post')
        ax.plot(times, amounts, 'o--', color='grey', alpha=0.3)
        ax.grid()

        max_bid : Bid = None
        for bid in self._bids:
            if not max_bid or bid._amount_in_cents > max_bid._amount_in_cents:
                max_bid = bid
            
        highest_bid_offer_amount = max_bid._amount_in_cents/100
        highest_bid_offer_amount_time = max_bid._time_received
        ax.axvline(x = self._start_time, color = 'g', label = 'axvline - full height', ymin = 0, ymax = highest_bid_offer_amount, linestyle = 'dashed')
        if self._cancellation_time:
            ax.axvline(x = self._cancellation_time, color = 'r', label = 'axvline - full height',ymin = 0, ymax = highest_bid_offer_amount , linestyle = 'dashed')
        ax.axvline(x = self._end_time, color = 'g', label = 'axvline - full height', ymin = 0, ymax = highest_bid_offer_amount , linestyle = 'dashed')

        ax.set_xlabel('time')
        ax.set_ylabel('bid offer amount [$]')
        ax.set_title(f'Auction for item "{self._item_id}"')

        _annot_max(highest_bid_offer_amount_time,highest_bid_offer_amount,ax)

        ax.tick_params(axis='x', labelrotation = 45)

        if toSave:
            plt.savefig(f'bid_history_itemid{self._item_id}.png',bbox_inches="tight")

        return fig

    def generate_bid_history_as_html(self) -> Tuple[str, bool]:

        try: 
            fig = self.show_bid_history()
            tmpfile = BytesIO()
            fig.savefig(tmpfile, format='png', bbox_inches="tight")
            encoded = base64.b64encode(tmpfile.getvalue()).decode('utf-8')

            html = '<img src=\'data:image/png;base64,{}\'>'.format(encoded)

            return html, False

            # cache perhaps?
            # with open('test.html','w') as f: 
            #     f.write(html)
        except:
            msg = "encountered error generating graphics; " +\
            "see ClosedAuction.generate_bid_history_as_html() in closed-auctions-service"
            return msg, True



    def convert_to_dict(self) -> Dict:
        """
        returns a json-like representation of the internal contents
        of a ClosedAuction.
        """

        return {
            'item_id': self._item_id,
            'start_price_in_cents': self._start_price_in_cents,
            'start_time': utils.toSQLTimestamp6Repr(self._start_time),
            'end_time': utils.toSQLTimestamp6Repr(self._end_time),
            'cancellation_time': utils.toSQLTimestamp6Repr(self._cancellation_time) if self._cancellation_time else "",
            'finalized_time': utils.toSQLTimestamp6Repr(self._finalized_time),
            'bids': [bid.convert_to_dict() for bid in self._bids],
            'winning_bid': self._winning_bid.convert_to_dict() if self._winning_bid else None,
        }

    def convert_to_dict_w_datetimes(self) -> Dict:
        """
        returns a json-like representation of the internal contents
        of a ClosedAuction. keeps times as date-time objects
        """

        return {
            'item_id': self._item_id,
            'start_price_in_cents': self._start_price_in_cents,
            'start_time': self._start_time,
            'end_time': self._end_time,
            'cancellation_time': self._cancellation_time if self._cancellation_time else "",
            'finalized_time': self._finalized_time,
            'str_start_time': utils.toSQLTimestamp6Repr(self._start_time),
            'str_end_time': utils.toSQLTimestamp6Repr(self._end_time),
            'str_cancellation_time': utils.toSQLTimestamp6Repr(self._cancellation_time) if self._cancellation_time else "",
            'str_finalized_time': utils.toSQLTimestamp6Repr(self._finalized_time),
            'bids': [bid.convert_to_dict_w_datetimes() for bid in self._bids],
            'winning_bid': self._winning_bid.convert_to_dict_w_datetimes() if self._winning_bid else None,
        }

    @staticmethod
    def generate_auction(bids: List[Bid],  itemid: int, time_start: datetime.datetime, duration: datetime.timedelta, winning_bid: Optional[Bid]) -> ClosedAuction:
        
        item_id = str(itemid)
        start_price_in_cents = 3400 # $34
        time_end = time_start + duration
        time_finalized = time_end + datetime.timedelta(minutes=1)
        return ClosedAuction(item_id,start_price_in_cents,time_start,time_end,None,time_finalized,bids,winning_bid)

def _annot_max(xmax,ymax, ax=None):

    text= "time={}, ${:.2f}".format(xmax, ymax)
    if not ax:
        ax=plt.gca()
    bbox_props = dict(boxstyle="square,pad=0.3", fc="w", ec="k", lw=0.72)
    arrowprops=dict(arrowstyle="->",connectionstyle="angle,angleA=0,angleB=45")
    kw = dict(xycoords='data',textcoords="axes fraction",
            arrowprops=arrowprops, bbox=bbox_props, ha="right", va="top")
    ax.annotate(text, xy=(xmax, ymax), xytext=(0.8,0.8), **kw)

