from dataclasses import dataclass
from typing import Optional


class MessageTemplate:
    COMPLETION_FOOTER = '''
Response format should be formatted in a JSON block like this:
```json
{ "user": "{agent_name}", "text": "string", "action": "string" }
```'''

    MESSAGE_HANDLER_TEMPLATE = '''# Action Examples
{action_examples}
(Action examples are for reference only. Do not use the information from them in your response.)

# Knowledge
{knowledge}

# Task: Generate dialog and actions for the character {agent_name}.
About {agent_name}:
{bio}
{lore}

{attachments}

# Capabilities
Note that {agent_name} is capable of reading/seeing/hearing various forms of media, including images, videos, audio, plaintext and PDFs. Recent attachments have been included above under the "Attachments" section.

{message_directions}

{recent_messages}

{actions}

# Instructions: Write the next message for {agent_name}.
'''

    @classmethod
    def format_template(cls,
                        agent_name: str,
                        action_examples: str,
                        knowledge: str,
                        bio: str,
                        lore: str,
                        attachments: str = "",
                        message_directions: str = "",
                        recent_messages: str = "",
                        actions: str = ""
                        ) -> str:
        """


        """

        main_template = cls.MESSAGE_HANDLER_TEMPLATE.format(
            agent_name=agent_name,
            action_examples=action_examples,
            knowledge=knowledge,
            bio=bio,
            lore=lore,
            attachments=attachments,
            message_directions=message_directions,
            recent_messages=recent_messages,
            actions=actions
        )

        footer = cls.COMPLETION_FOOTER.format(agent_name=agent_name)

        return main_template + footer


@dataclass
class MessageContext:
    agent_name: str
    action_examples: str
    knowledge: str
    bio: str
    lore: str
    providers: Optional[str] = ""
    attachments: Optional[str] = ""
    message_directions: Optional[str] = ""
    recent_messages: Optional[str] = ""
    actions: Optional[str] = ""

    def to_template(self) -> str:
        return MessageTemplate.format_template(
            agent_name=self.agent_name,
            action_examples=self.action_examples,
            knowledge=self.knowledge,
            bio=self.bio,
            lore=self.lore,
            attachments=self.attachments,
            message_directions=self.message_directions,
            recent_messages=self.recent_messages,
            actions=self.actions
        )