from typing import TYPE_CHECKING, Any, Dict

from dis_snek.mixins.serialization import DictSerializationMixin
from dis_snek.models.snowflake import SnowflakeObject
from dis_snek.utils.attr_utils import define, field

if TYPE_CHECKING:
    from dis_snek.client import Snake


@define()
class DiscordObject(SnowflakeObject, DictSerializationMixin):
    _client: "Snake" = field()

    @classmethod
    def from_dict(cls, data: Dict[str, Any], client: "Snake"):
        data = cls.process_dict(data, client)
        return cls(client=client, **cls._filter_kwargs(data, cls._get_init_keys()))

    @classmethod
    def process_dict(cls, data: Dict[str, Any], client: "Snake") -> Dict[str, Any]:
        return super().process_dict(data)