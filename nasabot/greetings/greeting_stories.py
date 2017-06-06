from nasabot.help import help_stories


def setup(story):
    @story.on_start()
    def on_start_story():
        @story.part()
        async def greet(ctx):
            await story.say(help_stories.SHORT_INTO,
                            user=ctx['user'])
            await story.say('For example right now you can find satellite images of your region',
                            user=ctx['user'])
            await story.ask('Please specify interesting location',
                            quick_replies=[{
                                'title': 'my location',
                                'payload': 'MY_LOCATION',
                            }, {
                                'title': 'Europe',
                                'payload': 'SET_LOCATION_EU',
                            }, {
                                'title': 'US :',
                                'payload': 'SET_LOCATION_US',
                            }, {
                                'title': 'Ukraine',
                                'payload': 'SET_LOCATION_UA',
                            }, ],
                            user=ctx['user'])
