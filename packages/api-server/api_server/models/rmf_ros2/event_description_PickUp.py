# generated by datamodel-codegen:
#   filename:  event_description_PickUp.json

from __future__ import annotations

from pydantic import BaseModel, Field

from . import event_description_PayloadTransfer


class PickUpEventDescription(BaseModel):
    __root__: event_description_PayloadTransfer.ItemTransferEventDescription = Field(
        ..., title="Pick Up Event Description"
    )