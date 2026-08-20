import json
from channels.generic.websocket import AsyncWebsocketConsumer


class TempsReelConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_group_name = "temps_reel"
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def envoyer_donnees(self, event):
        await self.send(text_data=json.dumps(event["data"]))