# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.

from typing import List, Callable, Any, Sequence, Hashable
from . import utils
import uuid


class EventData:
    def __init__(self, globals_val, **vars_val):
        if globals_val is not None:
            for key in globals_val:
                setattr(self, key, globals_val[key])
        for key in vars_val:
            setattr(self, key, vars_val[key])

    def __str__(self):
        sb = []
        for key in self.__dict__:
            val = self.__dict__[key]
            if utils.is_scalar(val):
                sb.append('{key}={value}'.format(key=key, value=val))
            else:
                sb.append('{key}="{value}"'.format(key=key, value=val))
 
        return ', '.join(sb)

EventsVars = List[EventData]

class StreamItem:
    def __init__(self, value:Any, stream_name:str=None, item_index:int=None, 
            ended:bool=False, exception:Exception=None, stream_reset:bool=False):
        self.value = value
        self.exception = exception
        self.stream_name = stream_name
        self.item_index = item_index
        self.ended = ended
        self.stream_reset = stream_reset

    def __repr__(self):
        return str(self.__dict__)

EventEvalFunc = Callable[[EventsVars], StreamItem]


class VisParams:
    def __init__(self, vis_type=None, host_vis=None, 
            cell=None, title=None, 
            clear_after_end=False, clear_after_each=False, history_len=1, dim_history=True, opacity=None,
            images=None, images_reshape=None, width=None, height=None, vis_args=None, stream_vis_args=None)->None:
        self.vis_type=vis_type
        self.host_vis=host_vis, 
        self.cell=cell
        self.title=title
        self.clear_after_end=clear_after_end
        self.clear_after_each=clear_after_each
        self.history_len=history_len
        self.dim_history=dim_history
        self.opacity=opacity
        self.images=images
        self.images_reshape=images_reshape
        self.width=width
        self.height=height
        self.vis_args=vis_args or {}
        self.stream_vis_args=stream_vis_args or {}

class StreamOpenRequest:
    def __init__(self, stream_name:str, devices:Sequence[str]=None, 
                 event_name:str='')->None:
        self.stream_name = stream_name or str(uuid.uuid4())
        self.devices = devices
        self.event_name = event_name


class StreamCreateRequest:
    def __init__(self, stream_name:str, devices:Sequence[str]=None, event_name:str='',
                 expr:str=None, throttle:float=None, vis_params:VisParams=None):
        self.event_name = event_name
        self.expr = expr
        self.stream_name = stream_name or str(uuid.uuid4())
        self.devices = devices
        self.vis_params = vis_params

        # max throughput n Lenovo P50 laptop for MNIST
        # text console -> 0.1s
        # matplotlib line graph -> 0.5s
        self.throttle = throttle

class ClientServerRequest:
    def __init__(self, req_type:str, req_data:Any):
        self.req_type = req_type
        self.req_data = req_data

class CliSrvReqTypes:
    create_stream = 'CreateStream'
    del_stream = 'DeleteStream'

class StreamVisInfo:
    def __init__(self, stream, title, clear_after_end, 
                clear_after_each, history_len, dim_history, opacity,
                index, stream_vis_args, last_update):
        self.stream = stream
        self.title, self.opacity = title, opacity
        self.clear_after_end, self.clear_after_each = clear_after_end, clear_after_each
        self.history_len, self.dim_history = history_len, dim_history
        self.index, self.stream_vis_args, self.last_update = index, stream_vis_args, last_update

class ImageData:
    # images are numpy array of shape [[channels,] height, width]
    def __init__(self, images=None, title=None, alpha=None, cmap=None):
        if not isinstance(images, tuple):
            images = (images,)
        self.images, self.alpha, self.cmap, self.title = images, alpha, cmap, title

class PointData:
    def __init__(self, x:float=None, y:float=None, z:float=None, low:float=None, high:float=None,
                 annotation:Any=None, text:Any=None, color:Any=None)->None:
        self.x = x
        self.y = y
        self.z = z
        self.low = low # confidence interval
        self.high = high
        self.annotation = annotation
        self.text = text
        self.color = color # typically string like '#d62728'

class PredictionResult:
    def __init__(self, loss:float=None, class_id:Hashable=None, probability:float=None, 
                 inputs:Any=None, outputs:Any=None, targets:Any=None, others:Any=None):
        self.loss = loss
        self.class_id = class_id
        self.probability = probability
        self.inputs = inputs
        self.outputs = outputs
        self.targets = targets
        self.others = others

class DefaultPorts:
    PubSub = 40859
    CliSrv = 41459

class PublisherTopics:
    StreamItem = 'StreamItem'
    ServerMgmt = 'ServerMgmt'

class ServerMgmtMsg:
    EventServerStart = 'ServerStart'
    def __init__(self, event_name:str, event_args:Any=None):
        self.event_name = event_name
        self.event_args = event_args