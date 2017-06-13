from botstory.ast import story_context


def get_last_location_data(ctx):
    """
    get last extracted location

    :param ctx:
    :return:
    """
    return story_context.get_message_data(ctx, 'location')[-1]
