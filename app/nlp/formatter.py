def format_quoted_translation(original_text, target_lang, translated_text, quoted_label=None):
    if quoted_label:
        return f"""> **{quoted_label}:**
> {original_text}

**Translation ({target_lang}):**
{translated_text}
"""
    else:
        return f"""> {original_text}

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

