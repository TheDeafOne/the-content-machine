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