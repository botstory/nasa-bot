from nasabot.help import help_stories
from nasabot.query import query_stories


def setup(story):
    @story.on_start()
    def on_start_story():
        @story.part()
        async def greet(ctx):
            await story.say(help_stories.SHORT_INTO.format(first_name=ctx['user']['first_name']),
                            user=ctx['user'])
            await story.say('For example right now you can find satellite images of your region',
                            user=ctx['user'])

            await query_stories.ask_location(story, ctx)
