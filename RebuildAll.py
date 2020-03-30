# -*- coding: utf-8 -*-
# See github page to report issues or to contribute:
# https://github.com/Arthaey/anki-rebuild-all
#
# Also available for Anki at https://ankiweb.net/shared/info/1639597619
#
# Contributors:
# - @Arthaey
# - @ankitest
# - @ArthurMilchior

import threading
from anki.cards import Card
import time
from anki.lang import _
from anki.hooks import wrap
from aqt import mw
from aqt.deckbrowser import DeckBrowser
from aqt.utils import tooltip
from .config import getUserOption

def _updateFilteredDecks(actionFuncName):
    dynDeckIds = [ d["id"] for d in mw.col.decks.all() if d["dyn"] ]
    count = len(dynDeckIds)

    if not count:
        tooltip("No filtered decks found.")
        return

    # should be one of "rebuildDyn" or "emptyDyn"
    actionFunc = getattr(mw.col.sched, actionFuncName)

    mw.checkpoint("{0} {1} filtered decks".format(actionFuncName, count))
    mw.progress.start()
    [ actionFunc(did) for did in sorted(dynDeckIds) ]
    mw.progress.finish()
    tooltip("Updated {0} filtered decks.".format(count))

    mw.reset()


def _handleFilteredDeckButtons(self, url):
    if url in ["rebuildDyn", "emptyDyn"]:
        _updateFilteredDecks(url)


def _addButtons(self):
    drawLinks = [
        ["", "rebuildDyn", _("Rebuild All")],
        ["", "emptyDyn", _("Empty All")]
    ]
    # don't duplicate buttons every click
    if drawLinks[0] not in self.drawLinks:
        self.drawLinks += drawLinks

DeckBrowser._drawButtons = wrap(DeckBrowser._drawButtons, _addButtons, "before")
DeckBrowser._linkHandler = wrap(DeckBrowser._linkHandler, _handleFilteredDeckButtons, "after")

lastReview = None

def postSched(self):
    global lastReview
    delta = getUserOption("time")
    print("New Flush")
    if delta and (lastReview is None or time.time() > lastReview + delta):
        print("doing it")
        _updateFilteredDecks("rebuildDyn")
        lastReview = time.time()

Card.flushSched = wrap(Card.flushSched, postSched)
Card.sched = wrap(Card.flush, postSched)
