# Alternatives

https://useapi.net/docs/start-here/setup-useapi

# Usage examples

## Kling AI Video Generation

This project provides tools for generating and extending videos using the Kling AI API.

### Setup

1. Set your Kling AI credentials as environment variables:
```bash
export KLING_ACCESS_KEY="your_access_key"
export KLING_SECRET="your_secret_key"
```

2. Install required dependencies:
```bash
pip install -r requirements.txt
```

3. Create a `prompts.json` file with your video prompts:

```json
[
    {
        "prompt": "A majestic eagle soaring over snow-capped mountains"
    },
    {
        "prompt": "A busy street scene in Tokyo at night with neon lights"
    },
    {
        "prompt": "Underwater coral reef with colorful fish swimming"
    }
]
```

### CLI Usage Examples

#### Video Creation

**Basic video generation:**
```bash
python generate_video.py prompts.json 0,1,2
```

**Custom video parameters:**
```bash
python generate_video.py prompts.json 0,1 --model kling-v1-6 --aspect-ratio 16:9 --mode pro --duration 15
```

**Generate without monitoring (get task ID only):**
```bash
python generate_video.py prompts.json 0 --no-monitor
```

> **Note:** `--no-monitor` skips the automatic waiting and downloading. You get the task ID immediately and can check status/download later manually.

#### Video Extension

**Extend video without additional prompt:**
```bash
python generate_video.py --extend "your_video_id_here"
```

**Extend video with additional prompts:**
```bash
python generate_video.py --extend "your_video_id_here" prompts.json 0,1
```

**Extend with custom parameters:**
```bash
python generate_video.py --extend "video_id" prompts.json 2 --no-monitor
```

### Programmatic API Usage Examples

#### Basic Video Creation

```python
from kling_api import KlingAPI

# Initialize API client (uses environment variables)
api = KlingAPI()

# Create a video
response = api.create_video(
    prompt="A serene mountain landscape at sunset with flowing rivers",
    model_name="kling-v1-6",
    aspect_ratio="16:9",
    mode="pro",
    duration="10"
)

# Monitor the task until completion
if response.get('code') == 0:
    task_id = response['data']['task_id']
    videos = api.monitor_task(task_id, operation="creation")
    
    if videos:
        for video in videos:
            # Download the video
            video_url = video['url']
            filename = f"generated_video_{video['id']}.mp4"
            api.download_video(video_url, filename)
```

#### Video Extension

```python
from kling_api import KlingAPI

api = KlingAPI()

# Extend an existing video
response = api.extend_video(
    video_id="existing_video_id_here",
    prompt="Continue with birds flying across the sky"
)

# Monitor and download
if response.get('code') == 0:
    task_id = response['data']['task_id']
    videos = api.monitor_task(task_id, operation="extension")
    
    if videos:
        for video in videos:
            filename = f"extended_video_{video['id']}.mp4"
            api.download_video(video['url'], filename)
```

#### Using Custom Credentials

```python
from kling_api import KlingAPI

# Initialize with custom credentials
api = KlingAPI(
    access_key="your_access_key",
    secret_key="your_secret_key"
)

response = api.create_video("A dancing robot in a futuristic city")
```

#### Status Checking Without Monitoring

```python
from kling_api import KlingAPI

api = KlingAPI()

# Create video
response = api.create_video("A beautiful garden with butterflies")
task_id = response['data']['task_id']

# Check status manually
status = api.check_status(task_id, operation="creation")
print(f"Current status: {status['data']['task_status']}")

# Monitor with custom parameters
videos = api.monitor_task(
    task_id, 
    operation="creation",
    check_interval=10,  # Check every 10 seconds
    max_wait_time=3600, # Wait up to 1 hour
    verbose=True
)
```

#### Batch Processing

```python
from kling_api import KlingAPI
import json

api = KlingAPI()

# Load prompts from JSON file
with open('prompts.json', 'r') as f:
    prompts = json.load(f)

# Process multiple prompts
for i, prompt_data in enumerate(prompts[:3]):  # Process first 3 prompts
    prompt_text = prompt_data.get('prompt', '')
    
    print(f"Processing prompt {i+1}: {prompt_text[:50]}...")
    
    response = api.create_video(prompt_text)
    
    if response.get('code') == 0:
        task_id = response['data']['task_id']
        videos = api.monitor_task(task_id)
        
        if videos:
            for j, video in enumerate(videos):
                filename = f"batch_video_{i+1}_{j+1}.mp4"
                api.download_video(video['url'], filename)
                print(f"Downloaded: {filename}")
```

#### Error Handling

```python
from kling_api import KlingAPI

try:
    api = KlingAPI()
    
    # This will raise ValueError if prompt is too long
    response = api.create_video("A" * 3000)  # Too long!
    
except ValueError as e:
    print(f"Validation error: {e}")
except Exception as e:
    print(f"API error: {e}")
```

### Output

Generated videos are saved in the `results/` directory with descriptive filenames:
- Creation: `{prompt_file}_{indices}.mp4`
- Extension: `extended_{video_id}_{prompt_file}_{indices}.mp4`

**Note:** Both `prompts/` and `videos/` folders are ignored by git to keep your workspace clean.

### API Reference

#### KlingAPI Class Methods

- `create_video(prompt, model_name, aspect_ratio, mode, duration)` - Generate new video
- `extend_video(video_id, prompt)` - Extend existing video
- `check_status(task_id, operation)` - Check task status
- `monitor_task(task_id, operation, check_interval, max_wait_time, verbose)` - Monitor until completion
- `download_video(url, filename, results_dir)` - Download video file

#### Parameters

**Video Creation:**
- `model_name`: "kling-v1-6", "kling-v2-master"
- `aspect_ratio`: "9:16", "16:9", "1:1"
- `mode`: "std", "pro"
- `duration`: "5", "10" (seconds)

**Common:**
- `prompt`: Text description (max 2500 characters)
- `operation`: "creation" or "extension"

# KlingAI official documentation

[API docs](https://docs.qingque.cn/d/home/eZQDkhg4h2Qg8SEVSUTBdzYeY?identityId=1oEG9JKKMFv)

## Prompt Instructions

[Images](https://docs.qingque.cn/d/home/eZQCtOj9fX_6cUjT_0yuk-yrL?identityId=1uX4dFq8Jtr#section=h.avhgs1y0tchp)

[Videos](https://docs.qingque.cn/d/home/eZQDvlYrDMyE9lOforCeWA4KP?identityId=2AwUiwWiFnw)

### Prompt instruction for videos extracted

Prompt = Subject (Subject Description) + Subject Movement + Scene (Scene Description) + (Camera Language + Lighting + Atmosphere)

Lighting and Atmosphere are optional.

Subject: The subject is the main focus in the video, serving as an important embodiment of the theme. It can be people, animals, plants, objects, and so on.

Subject Description: Descriptions of the subject’s appearance details and body posture can be listed using multiple short sentences. For example: athletic performance, hairstyle and color, clothing and accessories, facial features, body posture, and so on.

Subject Movement: Descriptions of the subject’s movement status, including stillness and motion, should be straightforward and suitable for a 5-second video.

Scene: The scene represents the environment in which the subject is situated, encompassing the foreground, background, and other elements.

Scene Description: Scene descriptions for the subject’s environment can be concise and focused, using a few short sentences to outline the setting without overwhelming the viewer. It should be suitable for what can be displayed within a 5-second video. Examples: indoor scene, outdoor setting, natural scene.

Camera Language: Refers to the use of various camera techniques, lens types, transitions, and edits between shots to communicate a narrative or message and to generate particular visual or emotional effects. Techniques include ultra-wide angle shots, bokeh (background blur), close-ups, telephoto shots, low-angle shots, high-angle shots, aerial views, and depth of field. This should be distinguished from camera motion control.

Lighting: Light and shadow bring depth and expressive power to the image. Techniques may include ambient lighting, morning light, sunset, interplay of light and shadow, Tyndall effect, and artificial lighting.

Atmosphere: Describes the mood and tone of the anticipated video.

The most fundamental components of the prompt are the subject, motion, and setting. Use short descriptive sentences to define these components clearly. Kling will extrapolate from your expression to generate a matching video.

Example:
Given the prompt “A giant panda is reading a book in a café”, you can enrich it by saying “A giant panda, wearing black-rimmed glasses, is reading a book in a café, with the book resting on a table where a steaming cup of coffee sits beside it, next to the café’s window.”
To add cinematic and lighting details, you might say “Shot in medium range, with a blurred background and atmospheric lighting, a giant panda, adorned with black-rimmed glasses, is seen reading a book in a café. The book lies on a table, accompanied by a steaming cup of coffee, steaming hot, next to the cafe windows, movie-level color palette.”

Tips:
	•	Use simple words and sentence structures.
	•	Keep the visual content simple; aim for a 5 to 10 second video.
	•	Phrases like “Oriental mood”, “China”, and “Asia” more easily evoke a Chinese style.
	•	Current models are not sensitive to numbers; e.g., “10 puppies on the beach” may not generate correctly.
	•	For split-screen scenes, use prompts like “4 camera angles, representing spring, summer, autumn, and winter.”
	•	Avoid complex physical movements such as bouncing balls or high throws, as they are hard to generate at this stage.
