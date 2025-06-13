import logging

from channels.generic.websocket import AsyncWebsocketConsumer


logger = logging.getLogger("app")


class HomeConsumer(AsyncWebsocketConsumer):
    async def websocket_connect(self, event):
        logger.debug("websocket_connect: %s", event)
        await self.channel_layer.group_add("home", self.channel_name)
        await self.accept()

    async def websocket_send(self, event):
        logger.debug("websocket_send: %s", event)
        logger.debug("scope: %s", self.scope)
        if self.scope["client"][1] is None:
            logger.warning("self.scope[client][1] is None")
            return
        await self.send(text_data=event["text"])

    async def websocket_receive(self, event):
        logger.debug("websocket_receive: %s", event)
        logger.debug("scope: %s", self.scope)

        if event["text"] == "ping":
            logger.debug("ping -> pong")
            return await self.send(text_data="pong")
