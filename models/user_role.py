import json
from enum import (
    Enum,
    auto,
)


class UserRole(Enum):
    guest = auto()
    normal = auto()
    # 课5作业6
    admin = auto()

# enum UserRole:
#     guest
#     normal


class MxEncoder(json.JSONEncoder):
    # "role": {
    #       "__enum__": "normal"
    #     }
    prefix = "__enum__"

    def default(self, o):
        if isinstance(o, UserRole):
            # self.__class__.prefix
            # self.prefix
            return {self.prefix: o.name}
        else:
            return super().default(self, o)


def mx_decode(d):
    if MxEncoder.prefix in d:
        name = d[MxEncoder.prefix]
        return UserRole[name]
    else:
        return d
