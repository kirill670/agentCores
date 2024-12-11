"""agent_core.py

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
    
    @LeoBorcherding
    12/10/2024
    
"""
import json
import time
import hashlib
from typing import Optional, Dict, Any
from agentMatrix import agentMatrix
# add uithub scrape, add arxiv

class agentCore:
    def __init__(self, db_path: str = "agent_matrix.db"):
        self.current_date = time.strftime("%Y-%m-%d")
        
        # Initialize agentMatrix
        self.agent_library = agentMatrix(db_path)
        
        # Initialize templates
        self.initBaseTemplate()
        # self.loadPredefinedAgents()  # This loads the templates into the DB

    def initBaseTemplate(self):
        """Initialize the base agent template - this is the reset state for any agent."""
        self.base_template = {
            "agentCore": {
                "agent_id": None,
                "version" : None,
                "uid": None,
                "cpu_noise_hex": None,
                "save_state_date": None,
                "models": {
                    "large_language_model": None,
                    "embedding_model": None,
                    "language_and_vision_model": None,
                    "yolo_model": None,
                    "whisper_model": None,
                    "voice_model": None,
                },
                "prompts": {
                    "user_input_prompt": "",
                    "agentPrompts": {
                        "llmSystemPrompt": None,
                        "llmBoosterPrompt": None,
                        "visionSystemPrompt": None,
                        "visionBoosterPrompt": None,
                    },
                },
                "commandFlags": {
                    "TTS_FLAG": False,
                    "STT_FLAG": False,
                    "CHUNK_FLAG": False,
                    "AUTO_SPEECH_FLAG": False,
                    "LLAVA_FLAG": False,
                    "SPLICE_FLAG": False,
                    "SCREEN_SHOT_FLAG": False,
                    "LATEX_FLAG": False,
                    "CMD_RUN_FLAG": False,
                    "AGENT_FLAG": True,
                    "MEMORY_CLEAR_FLAG": False
                },
                "conversation": {
                    "save_name": "defaultConversation",
                    "load_name": "defaultConversation",
                }
            }
        }
        
        # Initialize current agent core with base template
        self.agentCore = self.getNewAgentCore()

    def getNewAgentCore(self) -> Dict:
        """Get a fresh agent core based on the base template."""
        return json.loads(json.dumps(self.base_template))  # Deep copy

    # def loadPredefinedAgents(self, templates=templates):
    #     """Load the predefined agent templates into the database."""
        
    #     self.metaAgentLibrary()
        
    #     templates = {
    #         self.default_agent["agent_id"]: self.default_agent,
    #         self.promptBase["agent_id"]: self.promptBase,
    #         self.minecraft_agent["agent_id"]: self.minecraft_agent,
    #         self.general_navigator_agent["agent_id"]: self.general_navigator_agent,
    #         self.speedChatAgent["agent_id"]: self.speedChatAgent,
    #         self.ehartfordDolphin["agent_id"]: self.ehartfordDolphin
    #     }
        
    #     # Store each template using its own agent_id
    #     for agent_id, config in templates.items():
    #         template_config = self._createAgentConfig(agent_id, config)
    #         self.storeAgentCore(agent_id, template_config)
        
    def _createAgentConfig(self, agent_id: str, config: Dict) -> Dict:
        """Create a full agent configuration from base template and config data."""
        new_core = self.getNewAgentCore()
        new_core["agentCore"]["agent_id"] = agent_id
        new_core["agentCore"]["save_state_date"] = self.current_date
        
        # Update prompts
        if "llmSystemPrompt" in config:
            new_core["agentCore"]["prompts"]["agentPrompts"]["llmSystemPrompt"] = config["llmSystemPrompt"]
        if "llmBoosterPrompt" in config:
            new_core["agentCore"]["prompts"]["agentPrompts"]["llmBoosterPrompt"] = config["llmBoosterPrompt"]
        if "visionSystemPrompt" in config:
            new_core["agentCore"]["prompts"]["agentPrompts"]["visionSystemPrompt"] = config["visionSystemPrompt"]
        if "visionBoosterPrompt" in config:
            new_core["agentCore"]["prompts"]["agentPrompts"]["visionBoosterPrompt"] = config["visionBoosterPrompt"]
            
        # Update command flags
        if "commandFlags" in config:
            new_core["agentCore"]["commandFlags"].update(config["commandFlags"])
            
        return new_core

    def storeAgentCore(self, agent_id: str, core_config: Dict[str, Any]) -> None:
        """Store an agent configuration in the matrix."""
        core_json = json.dumps(core_config)
        self.agent_library.upsert(
            documents=[core_json],
            ids=[agent_id],  # No need for extra agent_ prefix, keep IDs clean
            metadatas=[{"agent_id": agent_id, "save_date": self.current_date}]
        )

    def loadAgentCore(self, agent_id: str) -> Optional[Dict[str, Any]]:
        """Load an agent configuration from the library."""
        results = self.agent_library.get(ids=[agent_id])
        if results and results["documents"]:
            loaded_config = json.loads(results["documents"][0])
            self.agentCore = loaded_config
            return loaded_config
        return None

    def listAgentCores(self) -> list:
        """List all available agent cores."""
        all_agents = self.agent_library.get()
        agent_cores = []
        for metadata, document in zip(all_agents["metadatas"], all_agents["documents"]):
            agent_core = json.loads(document)  # Deserialize the JSON string into a dictionary
            agent_cores.append({
                "agent_id": metadata["agent_id"],
                "uid": agent_core["agentCore"].get("uid", "Unknown"),
                "version": agent_core["agentCore"].get("version", "Unknown"),
            })
        return agent_cores
    
    def _generateUID(self, core_config: Dict) -> str:
        """Generate a unique identifier (UID) based on the agent core configuration."""
        core_json = json.dumps(core_config, sort_keys=True)
        return hashlib.sha256(core_json.encode()).hexdigest()[:8]
    
    def mintAgent(self, template_id: str, new_agent_id: str, overrides: Dict = None) -> Dict:
        """Create a new agent instance from a template."""
        template = self.loadAgentCore(template_id)  # Use direct template_id
        if not template:
            raise ValueError(f"Template {template_id} not found")
        
        new_config = template.copy()
        new_config["agentCore"]["agent_id"] = new_agent_id  # Set new instance ID
        new_config["agentCore"]["save_state_date"] = self.current_date
        new_config["agentCore"]["version"] = 1  # Start with version 1
        new_config["agentCore"]["uid"] = self._generateUID(new_config)
        
        if overrides:
            self._mergeConfig(new_config["agentCore"], overrides)
        
        # Store with new agent_id
        self.storeAgentCore(new_agent_id, new_config)
        return new_config

    def resetAgentCore(self):
        """Reset the current agent core to base template state."""
        self.agentCore = self.getNewAgentCore()
        return self.agentCore

    def getCurrentCore(self) -> Dict:
        """Get the current agent core configuration."""
        return self.agentCore

    def updateCurrentCore(self, updates: Dict):
        """Update the current agent core with new values."""
        self._mergeConfig(self.agentCore["agentCore"], updates)
        self.agentCore["agentCore"]["version"] += 1
        self.agentCore["agentCore"]["uid"] = self._generateUID(self.agentCore)
        
    def _mergeConfig(self, base: Dict, updates: Dict):
        """Recursively merge configuration updates."""
        for key, value in updates.items():
            if key in base and isinstance(base[key], dict) and isinstance(value, dict):
                self._mergeConfig(base[key], value)
            else:
                base[key] = value

    def deleteAgentCore(self, agent_id: str) -> None:
        """Remove an agent configuration from storage."""
        self.agent_library.delete(ids=[agent_id])

    def saveToFile(self, agent_id: str, file_path: str) -> None:
        """Save an agent configuration to a JSON file."""
        config = self.loadAgentCore(agent_id)
        if config:
            with open(file_path, 'w') as f:
                json.dump(config, f, indent=4)

    def loadAgentFromFile(self, file_path: str) -> None:
        """Load an agent configuration from a JSON file and store in matrix."""
        with open(file_path, 'r') as f:
            config = json.load(f)
            if "agentCore" in config and "agent_id" in config["agentCore"]:
                self.storeAgentCore(config["agentCore"]["agent_id"], config)
            else:
                raise ValueError("Invalid agent configuration file")
        
    def migrateAgentCores(self):
        """Add versioning and UID to existing agent cores."""
        print("Migrating agent cores to include versioning and UID...")
        all_agents = self.agent_library.get()
        for metadata, document in zip(all_agents["metadatas"], all_agents["documents"]):
            agent_core = json.loads(document)
            
            # Add versioning and UID if missing
            if "version" not in agent_core["agentCore"] or agent_core["agentCore"]["version"] is None:
                agent_core["agentCore"]["version"] = 1
            if "uid" not in agent_core["agentCore"] or agent_core["agentCore"]["uid"] is None:
                agent_core["agentCore"]["uid"] = self._generateUID(agent_core)
            
            # Save the updated agent core back to the database
            self.storeAgentCore(metadata["agent_id"], agent_core)
        print("Migration complete.")
 
    def commandInterface(self):
        """Command-line interface for managing agents."""
        
        print("Enter commands to manage agent cores. Type '/help' for options.")
        
        while True:
            command = input("> ").strip()
            if command == "/help":
                print("Commands:")
                print("  /agentCores - List all agent cores.")
                print("  /showAgent <agent_id> - Show agents with the specified ID.")
                print("  /createAgent <template_id> <new_agent_id> - Mint a new agent.")
                print("  /storeAgent <file_path> - Store agentCore from json path.")
                print("  /exportAgent <agent_id> - Export agentCore to json.")
                print("  /deleteAgent <uid> - Delete an agent by UID.")
                print("  /resetAgent <uid> - Reset an agent to the base template.")
                print("  /exit - Exit the interface.")
                
            elif command == "/agentCores":
                agents = self.listAgentCores()
                for agent in agents:
                    print(f"ID: {agent['agent_id']}, UID: {agent['uid']}, Version: {agent['version']}")
                    
            elif command.startswith("/showAgent"):
                try:
                    _, agent_id = command.split()
                    agents = self.agent_library.get(ids=[agent_id])
                    if agents and agents["documents"]:
                        for document in agents["documents"]:
                            agent_core = json.loads(document)  # Deserialize the JSON document
                            print(json.dumps(agent_core, indent=4))  # Pretty-print the JSON structure
                    else:
                        print(f"No agents found with ID: {agent_id}")
                except ValueError:
                    print("Usage: /showAgent <agent_id>")
                    
            elif command.startswith("/createAgent"):
                _, template_id, new_agent_id = command.split()
                self.mintAgent(template_id, new_agent_id)
                print(f"Agent '{new_agent_id}' created successfully.")
                
            elif command.startswith("/storeAgent"):
                try:
                    # Debug print to see the full command
                    print(f"Received command: {command}")

                    _, file_path = command.split()

                    # Debug print to check the file path
                    print(f"File path: {file_path}")

                    with open(file_path, "r") as file:
                        agent_core = json.load(file)

                    # Debug print to check the loaded JSON content
                    print(f"Loaded JSON: {agent_core}")

                    if "agentCore" not in agent_core:
                        print("Invalid JSON structure. The file must contain an 'agentCore' object.")
                        return

                    agent_id = agent_core["agentCore"].get("agent_id")
                    uid = agent_core["agentCore"].get("uid")

                    # Debug print to check agent_id and uid
                    print(f"agent_id: {agent_id}, uid: {uid}")

                    if not agent_id or not uid:
                        print("Invalid agent core. Both 'agent_id' and 'uid' are required.")
                        return

                    # Check if this agent already exists in the database
                    existing_agents = self.agent_library.get(ids=[agent_id])

                    # Debug print to check existing agents
                    print(f"Existing agents: {existing_agents}")

                    for document in existing_agents["documents"]:
                        existing_core = json.loads(document)
                        if existing_core["agentCore"]["uid"] == uid:
                            # Update the existing agent
                            self.storeAgentCore(agent_id, agent_core)
                            print(f"Agent core '{agent_id}' with UID '{uid}' updated successfully.")
                            return

                    # Otherwise, create a new agent core
                    self.storeAgentCore(agent_id, agent_core)
                    print(f"Agent core '{agent_id}' with UID '{uid}' added successfully.")

                except FileNotFoundError:
                    print(f"File not found: {file_path}")
                except json.JSONDecodeError:
                    print("Error decoding JSON from the file. Please check the file content.")
                except ValueError:
                    print("Usage: /storeAgent <file_path>")
                except Exception as e:
                    print(f"⚠️ Error storing agent core: {e}")

            elif command.startswith("/exportAgent"):
                try:
                    _, agent_id = command.split()
                    agents = self.agent_library.get(ids=[agent_id])
                    if agents and agents["documents"]:
                        for document in agents["documents"]:
                            agent_core = json.loads(document)
                            # Define the file path
                            file_path = f"{agent_id}_core.json"
                            with open(file_path, "w") as file:
                                json.dump(agent_core, file, indent=4)
                            print(f"Agent core saved to {file_path}")
                    else:
                        print(f"No agents found with ID: {agent_id}")
                except ValueError:
                    print("Usage: /exportAgent <agent_id>")
                except Exception as e:
                    print(f"⚠️ Error saving agent core: {e}")
                    
            elif command.startswith("/deleteAgent"):
                _, uid = command.split()
                self.deleteAgentCore(uid)
                print(f"Agent with UID '{uid}' deleted.")
                
            elif command.startswith("/resetAgent"):
                _, uid = command.split()
                agent = self.loadAgentCore(uid)
                if agent:
                    self.resetAgentCore()
                    print(f"Agent with UID '{uid}' reset.")
                    
            elif command == "/exit":
                break
            
            else:
                print("Invalid command. Type '/help' for options.")
                   
if __name__ == "__main__":
    try:
        print("\n=== Welcome to agentCore Management Interface ===\n")
        
        # Initialize agentCore
        core = agentCore()
        
        # Migrate existing agent cores
        core.migrateAgentCores()
        
        print("agentCore system initialized. Enter '/help' for a list of commands.\n")
        
        # Start the command-line interface
        core.commandInterface()

    except Exception as e:
        print(f"\n⚠️ Unexpected error occurred: {e}")
        raise
