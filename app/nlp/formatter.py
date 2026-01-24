def format_quoted_translation(original_text, target_lang, translated_text, quoted_label=None):
    # Normalize LLM output (remove stray >)
    translated_text = "\n".join(
        line.lstrip("> ").rstrip()
        for line in translated_text.splitlines()
        if line.strip()
    )

    # Always quote original cleanly
    quoted = "\n".join(f"> {line}" for line in original_text.splitlines() if line.strip())

    return f"""{quoted}

**Translation ({target_lang}):**

{translated_text}
"""

    
def format_proxy_reply(parent_text, speaker_username, translated_text, original_text, target_lang):
    return f"""> {parent_text}

@{speaker_username} says:
{translated_text}

<details>
<summary>Original</summary>

{original_text}  
— @{speaker_username}
</details>
"""

def format_thread_summary(summary_text, target_lang):
    return f"""### Thread Summary ({target_lang})

{summary_text}

"""

