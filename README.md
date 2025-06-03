# robocopilot2.0
An AI based IsaacSim extension for robot programming
robocopilot2.0: Currently work in progress - A chat agent built in the form of an IsaacSim extension that takes in language commands and runs a robot program on the simulator. The language commands are first mapped to objects in the scene based on their assigned names in the simulation. Then, background methods such as pick, place and move provided by the IsaacSim API are wrapped in RoboCopilotAPIs that are ingestible by LLMs. These wrappers are then converted to a workflow based on RoboCopilot APIs and executed in the correct order in IsaacSim.

This approach is "spatially-aware" as the pose of the objects specified in the language instruction can be queried from the simulation scene.

This is a simulation based digital twin robot-programmer and can be extended to the real robot if there is minimal sim2real gap. This can double as a dataset generator and used for model fine-tuning with VLA models such as Gr00t-N1 and pi0.

The architecture diagram for this approach is shown below:
![image](https://github.com/user-attachments/assets/808d8ba5-23af-44b1-8593-52cf1ff5271b)

Extension pings Groq, receives reponse and uses the response to call relevant IsaacSim APIs

TASK 1: 'Place the green cube on top of red cube'. 





https://github.com/user-attachments/assets/c409a116-5285-421c-90fd-5f5e68914d64





TASK 2: 'Place the red cube on top of the green object'. Extension generalizes for words such as objects because there is only one green object in the scene.



https://github.com/user-attachments/assets/3b0b3b66-5ca1-4011-9b42-520241a2b64e








