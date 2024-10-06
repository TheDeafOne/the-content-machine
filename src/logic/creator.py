from src.logic.llm import LLM 

CONTENT_THEMES = {
    "Storytelling": "Share a quick personal story, anecdote, or a fictional micro-narrative.",
    "Education": "Break down complex topics into bite-sized, easy-to-understand lessons.",
    "News": "Provide brief updates on current events or trending topics.",
    "Tutorials": "Show a quick 'how-to' guide on a specific skill or task.",
    "Motivation/Inspirational": "Share a motivational quote, story, or daily affirmation.",
    "Product Reviews": "Give a fast and concise review of a product or gadget.",
    "Life Hacks": "Showcase quick, clever tips to make everyday tasks easier.",
    "Behind-the-Scenes": "Offer a sneak peek into your work, process, or environment.",
    "Fitness": "Share a one-minute workout or health tip.",
    "Cooking": "Show a fast recipe or cooking tip in action.",
    "Challenges": "Participate in or create a viral challenge.",
    "Q&A": "Answer commonly asked questions in a rapid-fire format.",
    "Quotes/Facts": "Share an interesting fact, quote, or statistic.",
    "Humor/Comedy Skits": "Short comedic sketches or jokes.",
    "Time-lapse": "Condense a longer process into a one-minute time-lapse video."
}

llm = LLM()

def generate_content():
    content_text = generate_text("scary story", "middle schoolers")
    return content_text


def generate_text(story_type: str, audience: str):
    prompt = f'''Generate a {story_type} that takes one minute to read. It should have a beginning, middle, and end. 
    It should be oriented towards {audience} and should be engaging and easy to understand. 
    Only provide the story, do not give any meta-information or context.'''
    return llm.complete(prompt)

def generate_photo(content_text: str):
    prompt = f'''Generate a photo that visually represents the following story: {content_text}'''
    return llm.complete(prompt)


