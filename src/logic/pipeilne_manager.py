from src.logic.creators import LLM, ImageGenerator



llm = LLM()
img_gen = ImageGenerator()


def generate_content():
    content_text = generate_text("scary story", "middle schoolers")
    content_photo = generate_photo(content_text)
    return content_photo


def generate_text(story_type: str, audience: str):
    prompt = f'''Generate a {story_type} that takes one minute to read. It should have a beginning, middle, and end. 
    It should be oriented towards {audience} and should be engaging and easy to understand. 
    Only provide the story, do not give any meta-information or context.'''
    return llm.complete(prompt)

def generate_photo(content_text: str):
    prompt = f'''Generate a photo that visually represents the following story: {content_text}'''
    return llm.complete(prompt)


