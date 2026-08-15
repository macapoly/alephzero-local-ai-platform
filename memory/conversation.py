# ============================================================
# ALEPHZERO CONVERSATION MEMORY
# ============================================================


class ConversationMemory:

    def __init__(self):

        self.messages = []

        self.memories = {}


    # ========================================================
    # USER MESSAGE
    # ========================================================

    def add_user_message(
        self,
        message: str
    ):

        self.messages.append({

            "role":
                "user",

            "content":
                message
        })


    # ========================================================
    # ASSISTANT MESSAGE
    # ========================================================

    def add_assistant_message(
        self,
        message: str
    ):

        self.messages.append({

            "role":
                "assistant",

            "content":
                message
        })


    # ========================================================
    # GET MESSAGES
    # ========================================================

    def get_messages(self):

        return list(
            self.messages
        )


    # ========================================================
    # SAVE MEMORY
    # ========================================================

    def save_memory(
        self,
        key: str,
        value: str
    ):

        self.memories[key] = value


    # ========================================================
    # GET MEMORY
    # ========================================================

    def get_memory(
        self,
        key: str
    ):

        return self.memories.get(
            key
        )


    # ========================================================
    # GET ALL MEMORIES
    # ========================================================

    def get_all_memories(self):

        return list(
            self.memories.items()
        )


    # ========================================================
    # MEMORY CONTEXT
    # ========================================================

    def get_memory_context(self):

        if not self.memories:

            return (
                "No persistent user memories "
                "have been stored."
            )

        lines = []

        for key, value in self.memories.items():

            lines.append(
                f"{key}: {value}"
            )

        return (
            "Persistent user memory:\n"
            + "\n".join(lines)
        )