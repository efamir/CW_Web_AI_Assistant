determine_command = """
#### YOUR TASK ####
Read the USER INPUT.
Match it to ONE of the COMMANDS below.
Output ONLY the number of the matching command.

#### COMMANDS ####
1. General Chat / Other: If the input is NOT a command for Weather, Timer, Note, Joke, or Fact. This is the default if no other command matches.
Examples: "Today i visited my Grandma...", "Give me advice...", "How are you?", "Tell me about your day."

2. Get Weather: User asks for current weather information.
Examples: "What is the weather in <City>", "How hot is it in <City>"

3. Set Timer/Reminder: User asks to set a timer or reminder.
Examples: "Set a timer for 10 minutes.", "Start a 5-minute countdown.", "Remind me in 5 minutes to make a call"

4. Create/Save Note: User asks to create or save a note.
Examples: "Create a note: buy milk.", "Take a note about the meeting.", "Save 'client call details'."

5. Tell a Joke: User asks for a joke.
Examples: "Tell me a joke.", "Make me laugh.", "Something funny?"

6. Tell a Fact: User asks for a fact.
Examples: "Tell me a fact.", "Give me a random fact.", "Tell me something I don't know."

#### ANSWER FORMAT ####
Match this format: ****<command_number>****
Example: ****1****

#### USER INPUT HERE ####
{}
"""

extract_weather_details_short = """
#### TASK ####
Input is a "Get Weather" request. Extract the city.
Output JSON: {"city": "<city_name>"}
If no city is found, output: {"city": "error"}
ONLY output the JSON.

#### EXAMPLES ####
USER INPUT: "What is the weather in London?"
OUTPUT: {"city": "London"}

USER INPUT: "How hot is it in New York?"
OUTPUT: {"city": "New York"}

USER INPUT: "Tell me the weather."
OUTPUT: {"city": "error"}

#### USER INPUT HERE ####

""".replace("{", "{{").replace("}", "}}") + "{}"

extract_timer_details_short = """
#### TASK ####
Input is a "Set Timer/Reminder" request. Extract duration (in total seconds) and reminder message.
Output JSON: {"seconds": <total_seconds_as_integer>, "message": "<reminder_message_string>"}.
If no duration is found, set "seconds" to "error".
If no specific message is given, use an empty string for "message".
ONLY output the JSON.

#### EXAMPLES ####
USER INPUT: "Set a timer for 10 minutes."
OUTPUT: {"seconds": 600, "message": ""}

USER INPUT: "Remind me in 5 minutes to make a call"
OUTPUT: {"seconds": 300, "message": "to make a call"}

USER INPUT: "Start a 1 hour countdown for the food."
OUTPUT: {"seconds": 3600, "message": "for the food"}

USER INPUT: "Remind me to check the oven."
OUTPUT: {"seconds": "error", "message": "to check the oven"}

#### USER INPUT HERE ####
{}
""".replace("{", "{{").replace("}", "}}") + "{}"

extract_note_content_short = """
#### TASK ####
Input is a "Create/Save Note" request. Extract the core content of the note.
Remove instructional phrases (e.g., "Create a note:", "Save", "Note to self:").
Output ONLY the plain text content of the note. Ensure it's a good summary, capturing key details.

#### EXAMPLES ####
USER INPUT: "Create a note: buy milk, eggs, and bread."
OUTPUT: buy milk, eggs, and bread.

USER INPUT: "Take a note about the meeting - project deadline is next Friday, assign tasks to John."
OUTPUT: meeting - project deadline is next Friday, assign tasks to John.

USER INPUT: "Save 'Client X called, needs follow-up Q3 results.'"
OUTPUT: Client X called, needs follow-up Q3 results.

USER INPUT: "Note to self: finish report by 5 PM."
OUTPUT: finish report by 5 PM.

#### USER INPUT HERE ####
{}
""".replace("{", "{{").replace("}", "}}") + "{}"