from botstory.ast import story_context


def append_location(ctx, location_data):
    return story_context.set_message_data(
        ctx, 'location',
        story_context.get_message_data(ctx).get('location', []) + [location_data])
