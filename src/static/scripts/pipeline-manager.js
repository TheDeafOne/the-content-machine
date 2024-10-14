
// const CONTENT_THEMES = {
//     "Storytelling": "Share a quick personal story, anecdote, or a fictional micro-narrative.",
//     "Education": "Break down complex topics into bite-sized, easy-to-understand lessons.",
//     "News": "Provide brief updates on current events or trending topics.",
//     "Tutorials": "Show a quick 'how-to' guide on a specific skill or task.",
//     "Motivation/Inspirational": "Share a motivational quote, story, or daily affirmation.",
//     "Product Reviews": "Give a fast and concise review of a product or gadget.",
//     "Life Hacks": "Showcase quick, clever tips to make everyday tasks easier.",
//     "Behind-the-Scenes": "Offer a sneak peek into your work, process, or environment.",
//     "Fitness": "Share a one-minute workout or health tip.",
//     "Cooking": "Show a fast recipe or cooking tip in action.",
//     "Challenges": "Participate in or create a viral challenge.",
//     "Q&A": "Answer commonly asked questions in a rapid-fire format.",
//     "Quotes/Facts": "Share an interesting fact, quote, or statistic.",
//     "Humor/Comedy Skits": "Short comedic sketches or jokes.",
//     "Time-lapse": "Condense a longer process into a one-minute time-lapse video."
// }


async function generateStory() {
    const prompt = `Generate a scary story that takes one minute to read. It should have a beginning, middle, and end. 
It should be oriented towards children and should be engaging and easy to understand. 
Only provide the story, do not give any meta-information or context.`

    const response = await fetch('generate-text', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            prompt: prompt
        })
    });

    const data = await response.json();
    const story = data[0].text;
    const storyDiv = document.getElementById('text-result');
    storyDiv.textContent = story;

    await generateImageGenerationPrompt();
}


async function generateImageGenerationPrompt() {
    const story = document.getElementById('text-result').textContent;
    const prompt = `Generate an image prompt for the following story. Do not give any meta-information or context, only provide the prompt (e.g. DO NOT SAY "here is the image prompt"). Here is the story: ${story}`;

    const response = await fetch('generate-image-prompt', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            prompt: prompt
        })
    });

    const data = await response.json();
    const imagePrompt = data[0].text;
    const imagePromptDiv = document.getElementById('image-prompt-result');
    imagePromptDiv.textContent = imagePrompt;

    await generateImage();
    await generateVoiceOver();
}

async function generateImage() {
    const imagePrompt = document.getElementById('image-prompt-result').textContent;

    const response = await fetch('generate-image', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            prompt: imagePrompt
        })
    });

    const data = await response.json();
    const imageUrl = data.url;
    const imageDiv = document.getElementById('image-result');
    imageDiv.src = imageUrl;
}

async function generateVoiceOver() {
    const story = document.getElementById('text-result').textContent;

    const response = await fetch('generate-voice-over', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            text: story
        })
    });

    if (response.status !== 200) {
        console.log("Error generating voice over");
        return;
    }
    const data = await response.blob();
    const url = URL.createObjectURL(data);
    const playButton = document.getElementById('narration-play-button');
    playButton.disabled = false;
    playButton.onclick = () => {
        const audio = new Audio(url);
        audio.play();
    };
}