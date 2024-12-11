# agentCore
This file provides a class with methods to handle agentCores for agent_matrix.db

agentCore System:
1. Successfully initializes and stores your predefined agents in SQLite
2. Lists all available agent cores
3. Can mint new instances from any template
4. Properly handles loading and saving configurations

This gives you a solid foundation to:
1. Move the agent templates to separate JSON files later
2. Add more agent types easily
3. Track instances and templates in the database
4. Eventually add embedding functionality

The test shows everything working as intended:
- All predefined agents are loaded and stored
- Can create new instances with overrides (like the Minecraft agent with llama2)
- Loading and verification works
- Cleanup works
    
# installation
Clone the agentCore repo:
```cmd
git clone https://github.com/Leoleojames1/agentCore
```

Install the required python packages (file not existant):
```
pip install -r requirements.txt
```

To Run and access the agent_matrix.db use:
```
python agentCore.py
```

Start by using the /help command:
```cmd
Enter commands to manage agent cores. Type '/help' for options.
> /help
Commands:
  /agentCores - List all agent cores.
  /showAgent <agent_id> - Show agents with the specified ID.
  /createAgent <template_id> <new_agent_id> - Mint a new agent.
  /storeAgent <file_path> - Store agentCore from json path.
  /deleteAgent <uid> - Delete an agent by UID.
  /exportAgent <agent_id> - Export agentCore to json.
  /deleteAgent <uid> - Delete an agent by UID.
  /resetAgent <uid> - Reset an agent to the base template.
  /exit - Exit the interface.
```

Now to get the agentCores type:
```
> /agentCores

ID: default_agent, UID: ff22a0c1, Version: 1
ID: promptBase, UID: 6f18aba0, Version: 1
ID: speedChatAgent, UID: f1a7092c, Version: 1
ID: ehartfordDolphin, UID: 18556c0c, Version: 1
ID: minecraft_agent, UID: 25389031, Version: 1
ID: general_navigator_agent, UID: d1f12a46, Version: 1
```

Now to see an agent core use the following command
```cmd
> /showAgent general_navigator_agent
```

The agentCore will now be displayed:
```json
{
    "agentCore": {
        "agent_id": "general_navigator_agent",
        "version": 1,
        "uid": "d1f12a46",
        "save_state_date": "2024-12-11",
        "models": {
            "large_language_model": null,
            "embedding_model": null,
            "language_and_vision_model": null,
            "yolo_model": null,
            "whisper_model": null,
            "voice_model": null
        },
        "prompts": {
            "user_input_prompt": "",
            "agentPrompts": {
                "llmSystemPrompt": "You are a helpful llm assistant, designated with with fulling the user's request, the user is communicating with speech recognition and is sending their screenshot data to the                   vision model for decomposition. Receive this destription and Instruct the user and help them fullfill their request by collecting the vision data and responding. ",
                "llmBoosterPrompt": "Here is the output from the vision model describing the user screenshot data along with the users speech data. Please reformat this data, and formulate a fullfillment for the                   user request in a conversational speech manner which will be processes by the text to speech model for output. ",
                "visionSystemPrompt": "You are an image recognition assistant, the user is sending you a request and an image please fullfill the request. ",
                "visionBoosterPrompt": "Given the provided screenshot, please provide a list of objects in the image with the attributes that you can recognize. "
            }
        },
        "commandFlags": {
            "TTS_FLAG": false,
            "STT_FLAG": true,
            "CHUNK_FLAG": false,
            "AUTO_SPEECH_FLAG": false,
            "LLAVA_FLAG": true,
            "SPLICE_FLAG": false,
            "SCREEN_SHOT_FLAG": false,
            "LATEX_FLAG": false,
            "CMD_RUN_FLAG": false,
            "AGENT_FLAG": true,
            "MEMORY_CLEAR_FLAG": false
        },
        "conversation": {
            "save_name": "defaultConversation",
            "load_name": "defaultConversation"
        }
    }
}
```

Now to export an agentCore to json execute the following:
```cmd
> /exportAgent general_navigator_agent
Agent core saved to general_navigator_agent_core.json
```
