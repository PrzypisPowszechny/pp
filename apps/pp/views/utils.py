def get_data_fk_value(object, fk):
    """
    A helper function that compensates a JSON-API django module quirk.
    It extract foreign key fields from request body for POST & PATCH mathods
    ...

    The relationship body is
    "relationships": {
        "related_object": {
            "id": "2"
        }
    }
    JSON-API parser parses the request body so that we receive
    ...
    "related_object": {
        "id": "2"
    }

    Before we can safely pass request body to a django_rest.serializer we need to correct it with:
    data["related_object"] = get_data_fk_value(data, "related_object")

    :param object: the data part of a JSON-API data object
    :param fk: The relationship attribute
    :return: this relationship's id value
    """
    relationship_field = object.get(fk, {})
    if isinstance(relationship_field, dict):
        return relationship_field.get('id')
    else:
        return None