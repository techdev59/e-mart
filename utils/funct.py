from graphene import Int
from base64 import b64decode
from graphene import relay



from django.db import models

class CustomManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().order_by('-created_at')


def convert_into_id(string):
    """Convert a base64 encoded string into a numeric ID.

    This function takes a base64 encoded string that encodes a numeric ID prefixed with any string followed by a colon.
    It decodes the string from base64, extracts the numeric part after the colon, and converts it to an integer.

    Args:
        string (str): The base64 encoded string containing the numeric ID.

    Returns:
        int: The numeric ID extracted and converted from the provided string.
    """
    decoded_id = b64decode(string).decode('utf-8')
    numeric_id = int(decoded_id.split(':')[1])
    return numeric_id



def get_integer_id(id):
    converted_id = None
    try:
        id = int(id)
    except:
        pass
    if isinstance(id, int):
        converted_id = id
    else:
        converted_id = convert_into_id(id)
    return converted_id



class CountedConnection(relay.Connection):
    """
    A custom GraphQL connection class that includes a total count of items in the connection.

    This class inherits from `relay.Connection` and adds a `total_count` field which represents
    the total number of items in the connection. This is useful for pagination purposes in GraphQL
    queries where the client might need to know the total number of items available.

    Attributes:
        total_count (Int): A GraphQL integer field that resolves to the total count of items in the connection.
    """
    
    class Meta:
        abstract = True

    total_count = Int()

    def resolve_total_count(self, info, **kwargs):
        """
        Resolve the `total_count` field to the number of items in the connection.

        Args:
            info: The GraphQL resolution information.
            **kwargs: Additional keyword arguments.

        Returns:
            int: The total number of items in the connection.
        """
        # Return the length of the edge list which represents the total count of items
        return self.length