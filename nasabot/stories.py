from nasabot.help import help_stories

story_modules = (help_stories,)


def setup(story):
    for m in story_modules:
        m.setup(story)
