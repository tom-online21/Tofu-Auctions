def format_data(input_data):
    words_to_remove = [":generalist:", ":ninja:", ":healer:", ":warrior:"]
    words_to_replace = {
        ":Worn:": "<:Pristine:830383264572243978>",
        ":Great:": "<:Pristine:830383264572243978>",
        ":Pristine:": "<:Pristine:830383264572243978>",
        ":Good:": "<:Pristine:830383264572243978>",
        ":Scarred:": "<:Pristine:830383264572243978>",
        ":Worn~1:": "<:Pristine:830383264572243978>",
        ":Great~1:": "<:Pristine:830383264572243978>",
        ":Pristine~1:": "<:Pristine:830383264572243978>",
        ":Good~1:": "<:Pristine:830383264572243978>",
        ":Scarred~1:": "<:Pristine:830383264572243978>"

    }
    placeholder = "<TEMP_PLACEHOLDER>"

    formatted_output = ""
    for line in input_data.split("\n"):
        if "discord.com" in line:
            formatted_output += f"\n{line}\n\n"
        elif line.strip():
            for word in words_to_remove:
                line = line.replace(word, "")
            for key in words_to_replace.keys():
                line = line.replace(key, placeholder)
            line = line.replace(placeholder, words_to_replace[":Pristine:"])
            formatted_output += line + "\n"

    return formatted_output.strip()
