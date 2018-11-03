from Foundation import *
import asyncio
import libdispatch
import objc
import pytest
import functools

pytestmark = pytest.mark.asyncio

class MyObject(NSObject):
    ivar_string = objc.ivar()

    def init(self):
        self = objc.super(MyObject, self).init()
        if self is None: return None

        self.ivar_string = NSString.stringWithString_('hello')

        return self


class Function:
    unsafe_event_loop : asyncio.AbstractEventLoop
    unsafe_event : asyncio.Event
    def __init__(self, event_loop : asyncio.AbstractEventLoop, event : asyncio.Event):
        self.unsafe_event_loop = event_loop
        self.unsafe_event = event

    def do_it(self):
        self.unsafe_event_loop.call_soon_threadsafe(self.trigger_event, self.unsafe_event)

    def trigger_event(self, event):
        event.set()

async def test_libdispatch(event_loop : asyncio.AbstractEventLoop):
    did_finish = asyncio.Event()
    block = Function(event_loop, did_finish)
    queue = libdispatch.dispatch_queue_create(b'CoreBluetooth Queue', libdispatch.DISPATCH_QUEUE_SERIAL)
    # TODO: figure out if I can use funcutils to pass kwargs to do_it
    libdispatch.dispatch_async(queue, block.do_it)
    await asyncio.wait_for(did_finish.wait(), 10)
    assert did_finish.is_set()

if __name__ == '__main__':
    event_loop = asyncio.get_event_loop()
    event_loop.run_until_complete(functools.partial(test_libdispatch, event_loop)())